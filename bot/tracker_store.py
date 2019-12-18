import logging
import os
import requests
import yaml

from rasa.core.events import SlotSet
from rasa.core.tracker_store import InMemoryTrackerStore

logger = logging.getLogger(__name__)

ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'False').lower() == 'true'
ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME', 'locahost')
BOT_VERSION = os.getenv('BOT_VERSION', 'notdefined')


class CustomInMemoryTrackerStore(InMemoryTrackerStore):
    def __init__(self, domain, url):
        super(CustomInMemoryTrackerStore, self).__init__(domain)

        yml_data = yaml.load(
            open("credentials_facebook.yml"), Loader=yaml.FullLoader)

        self.fb_access_token = yml_data["facebook"]["page-access-token"]

    def save(self, tracker, timeout=None):
        # setting user name and email with facebook graph API
        if not tracker.get_slot('name'):
            sender_id = tracker.sender_id
            fields = "fields=first_name,last_name,email"
            access_token = "access_token={}".format(self.fb_access_token)
            url = "https://graph.facebook.com/{}?{}&{}".format(
                sender_id, fields, access_token)

            r = requests.get(url).json()

            first_name = r.get("first_name", "")
            last_name = r.get("last_name", "")

            if first_name:
                name = "{} {}".format(first_name, last_name)
                tracker.update(SlotSet('name', name))
                tracker.update(SlotSet('nickname', r.get("first_name")))

            email = r.get('email', None)
            tracker.update(SlotSet('email', email)) if email else None

            tracker.update(SlotSet('hostname', "Muck"))
            tracker.update(SlotSet('city', "Canoas"))
            tracker.update(SlotSet('uf_code', "RS"))

        super(CustomInMemoryTrackerStore, self).save(tracker)
