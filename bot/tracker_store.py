import logging
import os
import datetime
import hashlib
import json
import requests
import yaml

from rasa.core.events import SlotSet
from rasa.core.tracker_store import MongoTrackerStore
from rasa.core.trackers import EventVerbosity

try:
    from nltk.corpus import stopwords
except Exception:
    import nltk
    nltk.download('stopwords')
    from nltk.corpus import stopwords
    pass

logger = logging.getLogger(__name__)

ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'False').lower() == 'true'
ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME', 'locahost')
BOT_VERSION = os.getenv('BOT_VERSION', 'notdefined')

HASH_GEN = hashlib.md5()


def gen_id(timestamp):
    HASH_GEN.update(str(timestamp).encode('utf-8'))
    _id = HASH_GEN.hexdigest()[10:]
    return _id


class CustomMongoTrackerStore(MongoTrackerStore):
    def __init__(self, domain, url, e_domain, e_user=None,
                 e_password=None, e_scheme='http', e_scheme_port=80):
        super(CustomMongoTrackerStore, self).__init__(
            domain=domain,
            host="mongodb://" + url)

        yml_data = yaml.load(
            open("credentials_facebook.yml"), Loader=yaml.FullLoader)

        self.fb_access_token = yml_data["facebook"]["page-access-token"]

        # ElasticSearch Integration
        from elasticsearch import Elasticsearch

        if e_user is None:
            self.es = Elasticsearch([e_domain])
        else:
            self.es = Elasticsearch(
                ['{}://{}:{}@{}:{}'.format(e_scheme, e_user, e_password,
                                           e_domain, e_scheme_port)],)

    def _get_bag_of_words(self, message):
        tags = []
        for word in message.replace('. ', ' ')\
                           .replace(',', ' ') \
                           .replace('"', '')  \
                           .replace("'", '')  \
                           .replace('*', '')  \
                           .replace('(', '')  \
                           .replace(')', '')  \
                           .split(' '):
            if word.lower() not in stopwords.words('portuguese') \
                            and len(word) > 1:
                tags.append(word)

        return tags

    def _save_on_elastic(self, sender_id, text, timestamp, hostname,
                         is_bot=False, tags=[], entities=[], intent_name='',
                         intent_confidence='', utter_name='',
                         is_fallback=False):

        time = datetime.datetime.strftime(
            datetime.datetime.fromtimestamp(timestamp), '%Y/%m/%d %H:%M:%S')

        message = {
            'environment': ENVIRONMENT_NAME,
            'version': BOT_VERSION,

            'user_id': sender_id,
            'is_bot': is_bot,

            'text': text,
            'tags': tags,
            'timestamp': time,
            'hostname': hostname or '',

            'intent_name': intent_name,
            'intent_confidence': intent_confidence,
            'entities': entities,

            'utter_name': utter_name,
            'is_fallback': is_fallback,
        }

        msg_type = "user"

        if is_bot:
            msg_type = "bot"

        self.es.index(index='messages', doc_type='message',
                      id='{}_{}_{}'.format(ENVIRONMENT_NAME,
                                           msg_type,
                                           gen_id(timestamp)),
                      body=json.dumps(message))

    def _conversation_to_elastic_search(self, conversation):
        message_text = conversation['latest_message']['text']

        # Checking if conversation contains any relevant data
        if not message_text:
            return

        events = conversation['events']
        index = len(events) - 1

        # Checking if last event is from the user
        while events[index]['event'] != 'action':
            event = events[index]

            if event['event'] == 'user':
                tags = self._get_bag_of_words(message_text)
                entities = conversation['latest_message']['entities']

                self._save_on_elastic(
                    conversation['sender_id'],
                    message_text,
                    event['timestamp'],
                    conversation['slots']['hostname'],
                    False,
                    tags,
                    [entity['value'] for entity in entities],
                    event['parse_data']['intent']['name'],
                    event['parse_data']['intent']['confidence'])
                return

            index -= 1

        # Last event is from the bot. Saving the utter(s)
        while events[index]['event'] != 'user':
            event = events[index]

            if event['event'] == 'action' and event['name'] != 'action_listen':
                # policy = event['policy']
                self._save_on_elastic(
                    conversation['sender_id'],
                    message_text,
                    event['timestamp'],
                    conversation['slots']['hostname'],
                    True,
                    utter_name=event['name'],
                    is_fallback=event['name'] == 'action_default_fallback')
            index -= 1

    def save(self, tracker, timeout=None):
        # setting user name and email with facebook graph API
        if not tracker.get_slot('name'):
            sender_id = tracker.sender_id
            fields = "fields=first_name,last_name,email"
            access_token = "access_token={}".format(self.fb_access_token)
            url = "https://graph.facebook.com/{}?{}&{}".format(
                sender_id, fields, access_token)

            r = requests.get(url).json()

            name = "{} {}".format(r.get("first_name"), r.get("last_name"))

            email = r.get('email', None)

            tracker.update(SlotSet('name', name))
            tracker.update(SlotSet('email', email)) if email else None

        super(CustomMongoTrackerStore, self).save(tracker)

        conversation = tracker.current_state(EventVerbosity.ALL)

        if ENABLE_ANALYTICS:
            try:
                self._conversation_to_elastic_search(conversation)
            except Exception as ex:
                logger.error('Could not track messages '
                             'for user {}'.format(tracker.sender_id))
                logger.error(str(ex))
