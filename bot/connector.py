import logging
import threading
import os
import time

from typing import Text
from sanic import Blueprint
from sanic.response import json

from rasa.core.channels.channel import UserMessage, OutputChannel, InputChannel

logger = logging.getLogger(__name__)

WORDS_SEC = float(os.getenv('WORDS_PER_SECOND_TYPING', 2.5))
PHRASE_WORDS = int(os.getenv('DEFAULT_PHRASE_WORDS', 8))
MIN_TIME = int(os.getenv('MIN_TYPING_TIME', 1))
MAX_TIME = int(os.getenv('MAX_TYPING_TIME', 10))


class RocketChatBot(OutputChannel):
    @classmethod
    def name(cls):
        return "rocketchat"

    def __init__(self, user, password, server, ssl=False):
        from rocketchat_py_sdk.driver import Driver

        self.username = user
        self.connector = Driver(url=server, ssl=ssl)
        self.users = {}
        self.user = user
        self.password = password

        self.logged_in = False

        self.connector.connect()
        self.login()

    def login(self):
        while not self.logged_in:
            logger.info('Trying to login to rocketchat as {}'
                        .format(self.user))
            self.connector.login(user=self.user, password=self.password,
                                 callback=self._login_callback)
            time.sleep(10)

    """
    Internal callback handlers
    """
    def _login_callback(self, error, data):
        if error:
            logger.error('[-] callback error:')
            logger.error(error)
        else:
            self.logged_in = True
            logger.info("[+] callback success")
            logger.debug(data)

    """
    Messages handlers
    """
    async def send_text_message(self, recipient_id, text, **kwargs):
        if recipient_id not in self.users:
            self.users[recipient_id] = RocketchatHandleMessages(recipient_id,
                                                                self)

        messages = text.split("\n\n")

        t = threading.Thread(
            target=self.users[recipient_id].send_messages,
            args=(messages, ))
        t.start()


class RocketChatInput(InputChannel):
    """RocketChat input channel implementation."""

    @classmethod
    def name(cls):
        return "rocketchat"

    @classmethod
    def from_credentials(cls, credentials):
        if not credentials:
            cls.raise_missing_credentials_exception()

        return cls(credentials.get("user"),
                   credentials.get("password"),
                   credentials.get("server_url"))

    def __init__(self, user, password, server_url):
        # type: (Text, Text, Text) -> None

        self.user = user
        self.password = password
        self.server_url = server_url

        self.output_channel = RocketChatBot(
            self.user, self.password, self.server_url)

    def blueprint(self, on_new_message):
        rocketchat_webhook = Blueprint('rocketchat_webhook', __name__)

        @rocketchat_webhook.route("/", methods=['GET'])
        async def health(request):
            return json({'status': 200})

        @rocketchat_webhook.route("/webhook", methods=['GET', 'POST'])
        async def webhook(request):
            if request.json:
                output = request.json

                if "visitor" not in output:
                    sender_name = output.get("user_name", None)
                    text = output.get("text", None)
                    recipient_id = output.get("channel_id", None)
                else:
                    messages_list = output.get("messages", None)

                    sender_name = messages_list[0].get("username", None)
                    text = messages_list[0].get("msg", None)
                    recipient_id = output.get("_id")

                if sender_name != self.user:
                    user_msg = UserMessage(text,
                                           self.output_channel,
                                           recipient_id,
                                           input_channel=self.name())

                    await on_new_message(user_msg)

            return json({'status': 200})

        return rocketchat_webhook


class RocketchatHandleMessages:
    def __init__(self, rid, bot):
        self.rid = rid
        self.bot = bot
        self.is_typing = False
        self.semaphore = threading.Semaphore()

    def manage_is_typing_message(self, log_message, activate_is_typing,
                                 typing_function):
        logger.info(log_message)

        self.bot.connector.call(
            'stream-notify-room',
            [self.rid + '/typing', self.bot.username, activate_is_typing],
            typing_function
        )

    def send_messages(self, messages):
        self.semaphore.acquire()

        for idx, message in enumerate(messages):
            self.manage_is_typing_message('activate typing for {}'.
                                          format(self.rid),
                                          True, self.activate_typing)

            n_words = len(messages[idx].split()) if idx != 0 else PHRASE_WORDS

            wait_time = min(MAX_TIME, max(MIN_TIME, n_words // WORDS_SEC))

            time.sleep(wait_time)

            logger.info('[ ] schedule msg {}: {}'.format(self.rid, message))

            self.bot.connector.send_message(self.rid, message)

            logger.info('[+] send msg {}: {}'.format(self.rid, message))

            self.manage_is_typing_message('deactivate typing for {}'.
                                          format(self.rid),
                                          False, self.deactivate_typing)

            time.sleep(0.5)
        self.semaphore.release()

    def activate_typing(self, error, data):
        if not error:
            self.is_typing = True

    def deactivate_typing(self, error, data):
        if not error:
            self.is_typing = False
