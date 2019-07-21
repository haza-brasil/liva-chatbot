import logging

from rocketchat_py_sdk.driver import Driver

logger = logging.getLogger(__name__)


class RocketChatDriver(Driver):
    def __init__(self, url, ssl):
        super(RocketChatDriver, self).__init__(url, ssl)

    def send_message(self, id, message):
        self.call('sendMessage', [{'msg': message, 'rid': id}], self.cb)

    def send_attachments(self, id, message, attachments):
        self.call('sendMessage', [
            {'msg': message, 'rid': id, 'attachments': attachments}], self.cb)
