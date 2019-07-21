import logging
import os
import datetime
import hashlib
import json

from rasa_core.tracker_store import MongoTrackerStore
from rasa_core.trackers import EventVerbosity

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
    def __init__(self, m_domain, e_domain, e_user=None,
                 e_password=None, e_scheme='http', e_scheme_port=80):
        super(CustomMongoTrackerStore, self).__init__(
            domain=m_domain,
            host="mongodb://" + m_domain)

        # ElasticSearch Integration
        from elasticsearch import Elasticsearch

        if e_user is None:
            self.es = Elasticsearch([e_domain])
        else:
            self.es = Elasticsearch(
                ['{}://{}:{}@{}:{}'.format(e_scheme, e_user, e_password,
                                           e_domain, e_scheme_port)],)

        # RocketChat Database Integration
        from pymongo.database import Database

        self.rocket_db = Database(self.client, "rocketchat")
        self.collection_message = "rocketchat_message"

    @property
    def rocketchat_message(self):
        return self.rocket_db[self.collection_message]

    def get_last_hostname(self, sender_id):
        last_history = self.rocketchat_message.find_one(
            {"t": "livechat_navigation_history",
             "rid": sender_id}, sort=[('ts', -1)])

        if not last_history:
            return None

        return last_history['navigation']['page']['location']['hostname']

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
        super(CustomMongoTrackerStore, self).save(tracker)

        conversation = tracker.current_state(EventVerbosity.ALL)

        if ENABLE_ANALYTICS:
            try:
                self._conversation_to_elastic_search(conversation)
            except Exception as ex:
                logger.error('Could not track messages '
                             'for user {}'.format(tracker.sender_id))
                logger.error(str(ex))
