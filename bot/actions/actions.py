import logging
import json
import re
import requests
import unidecode

from typing import Dict, Text, Any, List, Union, Optional

from rasa_core.utils import configure_colored_logging

from rasa_core_sdk import Action, Tracker
from rasa_core_sdk.events import SlotSet
from rasa_core_sdk.executor import CollectingDispatcher
from rasa_core_sdk.forms import FormAction

logger = logging.getLogger(__name__)
configure_colored_logging(loglevel='DEBUG')


class ActionZipCode(Action):
    def name(self):
        return "action_zip_code"

    def run(self, dispatcher, tracker, domain):
        if not tracker.latest_message.get("entities", None):
            dispatcher.utter_template("utter_wrong_zip_code", tracker)
        else:
            zip_value = tracker.get_slot("zip_code")

            # removing any spaces or - from zip code
            zip_code = ''.join(e for e in zip_value if e.isalnum())

            dispatcher.utter_template("utter_searching_zip_code", tracker)

            events = []

            try:
                location_request = requests.get(
                    "https://viacep.com.br/ws/{}/json/".format(zip_code))
            except Exception as ex:
                logger.info(ex)
                dispatcher.utter_template("utter_cant_get_correios", tracker)
                return events

            location = json.loads(location_request.text)

            if location.get("erro", None):
                dispatcher.utter_template("utter_cant_find_zip_code", tracker)
            else:
                uf_code = location.get("uf")
                city = location.get("localidade")
                neighborhood = location.get("bairro")

                if tracker.get_slot("uf_code") != uf_code:
                    events.append(SlotSet("uf_code", uf_code))
                if tracker.get_slot("city") != city:
                    events.append(SlotSet("city", city))
                if tracker.get_slot("neighborhood") != neighborhood:
                    events.append(SlotSet("neighborhood", neighborhood))

                dispatcher.utter_message(
                    "UF: {}\nCidade: {}\nBairro: {}\n".format(
                        uf_code, city, neighborhood) +
                    "É isso mesmo?")

                # API liva

            return events


class LeadForm(FormAction):
    def name(self) -> Text:
        """Unique identifier of the form"""

        return "lead_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["name", "phone", "email"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "name": self.from_text(),
            "phone": self.from_text(),
            "email": self.from_text(),
        }

    def validate_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        name_pattern = re.compile(
            r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$")

        if name_pattern.match(value):
            return {"name": value}
        else:
            dispatcher.utter_template("utter_wrong_name", tracker)
            return {"name": None}

    def validate_phone(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        phone_pattern = re.compile(
            r"((?:\([0-9]{1,3}\)|[0-9]{2})[ \-]*?[0-9]{4,5}(?:[\-\s\_]{1,2})" +
            r"?[0-9]{4}(?:(?=[^0-9])|$)|[0-9]{4,5}" +
            r"(?:[\-\s\_]{1,2})?[0-9]{4}(?:(?=[^0-9])|$))")

        if phone_pattern.match(value):
            return {"phone": value}
        else:
            dispatcher.utter_template("utter_wrong_phone", tracker)
            return {"phone": None}

    def validate_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        email_pattern = re.compile(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

        if email_pattern.match(value):
            return {"email": value}
        else:
            dispatcher.utter_template("utter_wrong_email", tracker)
            return {"email": None}

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any],) -> List[Dict]:
        nickname = tracker.get_slot("name").split(" ")[0].capitalize()

        dispatcher.utter_template("utter_submit", tracker, nickname=nickname)

        events = []

        slot_nickname = tracker.get_slot("nickname")

        if slot_nickname != nickname:
            events.append(SlotSet("nickname", nickname))

        return events

    def run(self, dispatcher, tracker, domain):
        if not tracker.get_slot("name") and not tracker.get_slot("requested_slot"):
            dispatcher.utter_template("utter_greetings_lead", tracker)

        return super(LeadForm, self).run(dispatcher, tracker, domain)


class PrimaryPreferencesForm(FormAction):
    def name(self) -> Text:
        return "primary_preferences_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["property_type", "min_value", "max_value"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "property_type": [
                self.from_entity(entity="property_type"), self.from_text()],
            "min_value": self.from_text(),
            "max_value": self.from_text(),
        }

    def validate_property_type(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        types = ["apartamento", "casa", "comercio", "rural", "terreno"]

        if unidecode.unidecode(value.lower()) in types:
            return {"property_type": value}
        else:
            dispatcher.utter_template("utter_wrong_property_type", tracker)
            return {"property_type": None}

    def validate_min_value(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:

        try:
            min_value = float(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_min_value", tracker)
            return {"min_value": None}

        return {"min_value": min_value}

    def validate_max_value(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:

        try:
            max_value = float(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_max_value", tracker)
            return {"max_value": None}

        min_value = tracker.get_slot("min_value")

        if max_value <= min_value:
            dispatcher.utter_message(
                "O valor informado é menor ou igual ao mínimo!")
            return {"max_value": None}

        return {"max_value": value}

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any],) -> List[Dict]:
        dispatcher.utter_template("utter_ask_secondary_informations", tracker)

        return []


class SecondaryPreferencesForm(FormAction):
    def name(self) -> Text:
        return "secondary_preferences_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["useful_area", "suite_qtt",
                "toilet_qtt", "parking_space_qtt"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "useful_area": self.from_text(),
            "suite_qtt": self.from_text(),
            "toilet_qtt": self.from_text(),
            "parking_space_qtt": self.from_text(),
        }

    def validate_useful_area(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        if value:
            return {"useful_area": value}
        else:
            dispatcher.utter_template("utter_wrong_useful_area", tracker)
            return {"useful_area": None}

    def validate_suite_qtt(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        if value:
            return {"suite_qtt": value}
        else:
            dispatcher.utter_template("utter_wrong_suite_qtt", tracker)
            return {"suite_qtt": None}

    def validate_toilet_qtt(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        if value:
            return {"toilet_qtt": value}
        else:
            dispatcher.utter_template("utter_wrong_toilet_qtt", tracker)
            return {"toilet_qtt": None}

    def validate_parking_space_qtt(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        if value:
            return {"parking_space_qtt": value}
        else:
            dispatcher.utter_template("utter_wrong_parking_space_qtt", tracker)
            return {"parking_space_qtt": None}

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any],) -> List[Dict]:
        return []
