import logging
import json
import re
import requests
import unidecode

from typing import Dict, Text, Any, List, Union, Optional

from rasa.utils.io import configure_colored_logging

from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

logger = logging.getLogger(__name__)
configure_colored_logging(loglevel='DEBUG')


class ZipCodeForm(FormAction):
    def name(self) -> Text:
        """Unique identifier of the form"""

        return "zip_code_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["zip_code"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "zip_code": [self.from_entity(entity="phone-number"),
                         self.from_text(not_intent="deny"), ],
        }

    def validate_zip_code(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        zip_code_pattern = re.compile(
            r"\b[\d]{5}([\d]{3}|-[\d]{3}|\s[\d]{3})\b")

        if zip_code_pattern.match(value):
            return {"zip_code": value}
        else:
            dispatcher.utter_template("utter_wrong_zip_code", tracker)
            return {"zip_code": None}

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any],) -> List[Dict]:
        zip_code = tracker.get_slot("zip_code")

        dispatcher.utter_template("utter_searching_zip_code", tracker)

        events = []

        # API liva

        try:
            location_request = requests.get(
                "https://viacep.com.br/ws/{}/json/".format(zip_code))
        except Exception as ex:
            logger.info(ex)
            dispatcher.utter_template("utter_cant_get_correios", tracker)
            return events

        try:
            location = json.loads(location_request.text)
        except Exception as ex:
            logger.info(ex)
            dispatcher.utter_template("utter_cant_get_correios", tracker)
            return events

        if location.get("erro", None) or location.get("status_code") == 400:
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
            "name": [self.from_text(not_intent="deny"),
                     self.from_entity(entity="name", intent="lead_data")],
            "phone": [self.from_text(not_intent="deny"),
                      self.from_entity(entity="phone-number", intent="lead_data")],
            "email": [self.from_text(not_intent="deny"),
                      self.from_entity(entity="email", intent="lead_data")],
        }

    def validate_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        name_pattern = re.compile(
            r"^[a-zA-Zà-ÿÀ-Ÿ]+(([',. -][a-zA-Zà-ÿÀ-Ÿ ])?[a-zA-Zà-ÿÀ-Ÿ]*)*$")

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
            "property_type": [self.from_entity(entity="property_type"),
                              self.from_text(), ],
            "min_value": [self.from_entity(entity="amount-of-money"),
                          self.from_entity(entity="number"),
                          self.from_text(not_intent="deny"), ],
            "max_value": [self.from_entity(entity="amount-of-money"),
                          self.from_entity(entity="number"),
                          self.from_text(not_intent="deny"), ],
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

        if max_value <= tracker.get_slot("min_value"):
            dispatcher.utter_message(
                "O valor informado é menor ou igual ao mínimo!")
            return {"max_value": None}

        return {"max_value": max_value}

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
            "useful_area": [self.from_entity(entity="distance"),
                            self.from_entity(entity="number"),
                            self.from_text(not_intent="deny"), ],
            "suite_qtt": [self.from_entity(entity="number"),
                          self.from_text(not_intent="deny"), ],
            "toilet_qtt": [self.from_entity(entity="number"),
                           self.from_text(not_intent="deny"), ],
            "parking_space_qtt": [self.from_entity(entity="number"),
                                  self.from_text(not_intent="deny"), ],
        }

    def validate_useful_area(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:

        try:
            useful_area = float(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_useful_area", tracker)
            return {"useful_area": None}

        return {"useful_area": useful_area}


    def validate_suite_qtt(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        try:
            suite_qtt = int(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_suite_qtt", tracker)
            return {"suite_qtt": None}

        return {"suite_qtt": suite_qtt}

    def validate_toilet_qtt(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        try:
            toilet_qtt = int(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_toilet_qtt", tracker)
            return {"toilet_qtt": None}

        return {"toilet_qtt": toilet_qtt}

    def validate_parking_space_qtt(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        try:
            parking_space_qtt = int(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_parking_space_qtt", tracker)
            return {"parking_space_qtt": None}

        return {"parking_space_qtt": parking_space_qtt}

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any],) -> List[Dict]:
        return []
