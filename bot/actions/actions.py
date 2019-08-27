import logging
import json
import os
import re
import requests
import unidecode

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet

from .custom_form import CustomFormAction

LIVA_API_CEP = os.getenv('LIVA_API_CEP', None)
LIVA_API_LEAD = os.getenv('LIVA_API_LEAD', None)
LIVA_PROFILE = os.getenv('LIVA_PROFILE', None)

logger = logging.getLogger(__name__)


class ActionPostLead(Action):
    def name(self):
        return "action_post_lead"

    def run(self, dispatcher, tracker, domain):
        events = []

        # e se nao informar opções secundárias
        data = {
            "name": tracker.get_slot("name"),
            "email": tracker.get_slot("email"),
            "phone": tracker.get_slot("phone"),
            "platform_origin_name": "Site Imobiliária",
            "real_estate_identifier": "beiramarimoveis",
            "min_budget": tracker.get_slot("min_value"),
            "max_budget": tracker.get_slot("max_value"),
            "min_suites": tracker.get_slot("suite_qtt"),
            "min_parking_spots": tracker.get_slot("parking_space_qtt"),
            "min_bedrooms": tracker.get_slot("toilet_qtt"),
            "min_usable_area": tracker.get_slot("useful_area"),
            "property_type": tracker.get_slot("property_type"),
            "neighborhood_data": [[tracker.get_slot("uf_code"),
                                   tracker.get_slot("city"),
                                   tracker.get_slot("neighborhood")]]
        }

        if not tracker.get_slot("posted_api"):
            try:
                requests.post(LIVA_API_LEAD, json=data)
            except Exception as ex:
                logger.info(ex)
                dispatcher.utter_template("utter_cant_get_liva", tracker)
            else:
                events.append(SlotSet("posted_api", True))

        dispatcher.utter_template(
            "utter_liva_url_profile", tracker,
            liva_url=LIVA_PROFILE, email=tracker.get_slot("email").lower())

        return events


class LeadForm(CustomFormAction):
    def __init__(self):
        self.name_pattern = re.compile(
            r"^[a-zA-Zà-ÿÀ-Ÿ]+(([',. -][a-zA-Zà-ÿÀ-Ÿ ])?[a-zA-Zà-ÿÀ-Ÿ]*)*$")

        self.phone_pattern = re.compile(
            r"((?:\([0-9]{1,3}\)|[0-9]{2})[ \-]*?[0-9]{4,5}(?:[\-\s\_]{1,2})" +
            r"?[0-9]{4}(?:(?=[^0-9])|$)|[0-9]{4,5}" +
            r"(?:[\-\s\_]{1,2})?[0-9]{4}(?:(?=[^0-9])|$))")

        self.email_pattern = re.compile(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    def name(self):
        return "lead_form"

    @staticmethod
    def required_slots(tracker: Tracker):
        return ["name", "phone", "email"]

    def slot_mappings(self):
        return {
            "name": [self.from_entity(entity="PER"),
                     self.from_entity(entity="LOC"),
                     self.from_text(not_intent="deny"), ],
            "phone": [self.from_entity(entity="phone-number"),
                      self.from_text(not_intent="deny"), ],
            "email": [self.from_entity(entity="email"),
                      self.from_text(not_intent="deny"), ],
        }

    def validate_name(self, value, dispatcher, tracker, domain):
        slot_dict = {"name": None}

        if self.name_pattern.match(value):
            slot_dict.update({"name": value})
        else:
            dispatcher.utter_template("utter_wrong_name", tracker)

        return slot_dict

    def validate_phone(self, value, dispatcher, tracker, domain):
        slot_dict = {"phone": None}

        if self.phone_pattern.match(value):
            slot_dict.update({"phone": value})
        else:
            dispatcher.utter_template("utter_wrong_phone", tracker)

        return slot_dict

    def validate_email(self, value, dispatcher, tracker, domain):
        slot_dict = {"email": None}

        if self.email_pattern.match(value):
            slot_dict.update({"email": value})
        else:
            dispatcher.utter_template("utter_wrong_email", tracker)

        return slot_dict

    def submit(self, dispatcher, tracker, domain):
        nickname = tracker.get_slot("name").split(" ")[0].capitalize()

        dispatcher.utter_template("utter_submit", tracker, nickname=nickname)

        events = []

        slot_nickname = tracker.get_slot("nickname")

        if slot_nickname != nickname:
            events.append(SlotSet("nickname", nickname))

        return events

    def run(self, dispatcher, tracker, domain):
        name = tracker.get_slot("name")
        requested_slot = tracker.get_slot("requested_slot")

        if not any([name, requested_slot]):
            dispatcher.utter_template("utter_greetings_lead", tracker)

        return super(LeadForm, self).run(dispatcher, tracker, domain)


class AddressForm(CustomFormAction):
    def __init__(self):
        f = open("actions/data/neighborhoods.json", "r")
        self.neighborhoods = json.load(f)
        f.close()

        self.neighborhood_pattern = re.compile(
            r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z0-9 ]*)*$")

        self.zip_code_pattern = re.compile(
            r"\b[\d]{5}([\d]{3}|-[\d]{3}|\s[\d]{3})\b")

    def name(self):
        return "address_form"

    @staticmethod
    def required_slots(tracker):
        return ["neighborhood", "confirmation", "city"]

    def slot_mappings(self):
        return {
            "neighborhood": [self.from_entity(entity="neighborhood"),
                             self.from_entity(entity="LOC"),
                             self.from_entity(entity="phone-number"),
                             self.from_text(not_intent="deny"), ],
            "confirmation": [self.from_text(), ],
            "city": [self.from_entity(entity="LOC"),
                     self.from_text(not_intent="deny"), ],
        }

    def validate_neighborhood(self, value, dispatcher, tracker, domain):
        slot_dict = {"neighborhood": None}

        value = self.simple_text(value)

        if self.neighborhood_pattern.match(value):
            try:
                neighborhood = self.neighborhoods[value]
            except KeyError:
                dispatcher.utter_template(
                    "utter_cant_find_neighborhood", tracker)
            else:
                # verificar se imobiliária trabalha com bairro

                if len(neighborhood) == 1:
                    slot_dict = {
                        "neighborhood": neighborhood[0].get("name"),
                        "city": neighborhood[0].get("city"),
                        "uf_code": neighborhood[0].get("uf_code"),
                        "confirmation": True
                    }
                else:
                    # verifica cidades do hostname e filtra lista
                    cities = " | ".join([e.get("city") for e in neighborhood])

                    slot_dict = {
                        "neighborhood": neighborhood[-1].get("name"),
                        "confirmation": True,
                        "cities": cities
                    }
        elif self.zip_code_pattern.match(value):
            # real_estate_identifier = tracker.get_slot("hotname")
            real_estate_identifier = "beiramarimoveis"

            url = (LIVA_API_CEP +
                   "postal_code={}&".format(value) +
                   "real_estate_identifier={}".format(real_estate_identifier))

            try:
                location_request = requests.get(url)
            except Exception as ex:
                logger.warning(ex)
                dispatcher.utter_template("utter_cant_get_api", tracker)
                return slot_dict

            if location_request.status_code == 200:
                location = json.loads(location_request.content)
                uf_code = location.get('state').get('uf')
                city = location.get('city').get('name')
                neighborhood = location.get('neighborhood').get('name')

                slot_dict.update({"confirmation": None})

                if tracker.get_slot("uf_code") != uf_code:
                    slot_dict.update({"uf_code": uf_code})
                if tracker.get_slot("city") != city:
                    slot_dict.update({"city": city})
                if tracker.get_slot("neighborhood") != neighborhood:
                    slot_dict.update({"neighborhood": neighborhood})
            elif location_request.status_code == 400:
                dispatcher.utter_template("utter_cant_work_neighborhood",
                                          tracker)
            elif location_request.status_code == 404:
                dispatcher.utter_template("utter_cant_find_zip_code", tracker)
            elif location_request.status_code == 500:
                dispatcher.utter_template("utter_cant_get_api", tracker)
        else:
            dispatcher.utter_template("utter_wrong_neighborhood", tracker)

        return slot_dict

    def validate_confirmation(self, value, dispatcher, tracker, domain):
        slot_dict = {"confirmation": None}

        last_intent = tracker.latest_message["intent"]["name"]

        if last_intent == "affirm":
            slot_dict.update({"confirmation": True})
        elif last_intent == "deny":
            slot_dict.update({"neighborhood": None,
                              "city": None})

        return slot_dict

    def validate_city(self, value, dispatcher, tracker, domain):
        slot_dict = {"city": None}

        neighborhood = self.simple_text(
            tracker.get_slot("neighborhood"))

        value = self.simple_text(value)

        neighborhood_list = self.neighborhoods.get(neighborhood)

        city_found = False

        for element in neighborhood_list:
            if self.simple_text(element.get("city")) == value:
                city_found = True
                break

        if city_found:
            slot_dict.update({"city": element.get("city")})
            slot_dict.update({"uf_code": element.get("uf_code")})
            slot_dict.update({"confirmation": True})
        else:
            dispatcher.utter_template("utter_wrong_city", tracker)

        return slot_dict

    def submit(self, dispatcher, tracker, domain):
        return []


class PrimaryPreferencesForm(CustomFormAction):
    def name(self):
        return "primary_preferences_form"

    @staticmethod
    def required_slots(tracker):
        return ["property_type", "min_value", "max_value"]

    def slot_mappings(self):
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

    def validate_property_type(self, value, dispatcher, tracker, domain):
        slot_dict = {"property_type": None}

        types = ["apartamento", "casa", "comercial", "rural", "terreno"]

        if unidecode.unidecode(value.lower()) in types:
            slot_dict.update({"property_type": value.capitalize()})
        else:
            dispatcher.utter_template("utter_wrong_property_type", tracker)

        return slot_dict

    def validate_min_value(self, value, dispatcher, tracker, domain):
        slot_dict = {"min_value": None}

        try:
            min_value = float(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_min_value", tracker)
        else:
            if min_value > 0:
                slot_dict.update({"min_value": min_value})
            elif min_value == 0:
                dispatcher.utter_template("utter_wrong_zero", tracker)
            else:
                dispatcher.utter_template("utter_wrong_negative", tracker)

        return slot_dict

    def validate_max_value(self, value, dispatcher, tracker, domain):
        slot_dict = {"max_value": None}

        try:
            max_value = float(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_max_value", tracker)
        else:
            min_value = tracker.get_slot("min_value")

            if (max_value > 0) and (max_value > min_value):
                slot_dict.update({"max_value": max_value})
            elif (max_value > 0) and (max_value <= min_value):
                dispatcher.utter_template("utter_cant_max_big_min", tracker)
            elif max_value == 0:
                dispatcher.utter_template("utter_wrong_zero", tracker)
            else:
                dispatcher.utter_template("utter_wrong_negative", tracker)

        return slot_dict

    def submit(self, dispatcher, tracker, domain):
        dispatcher.utter_template("utter_ask_secondary_informations", tracker)

        return []


class SecondaryPreferencesForm(CustomFormAction):
    def name(self):
        return "secondary_preferences_form"

    @staticmethod
    def required_slots(tracker):
        return ["suite_qtt", "toilet_qtt",
                "parking_space_qtt", "useful_area"]

    def slot_mappings(self):
        return {
            "suite_qtt": [self.from_entity(entity="number"),
                          self.from_text(not_intent="deny"), ],
            "toilet_qtt": [self.from_entity(entity="number"),
                           self.from_text(not_intent="deny"), ],
            "parking_space_qtt": [self.from_entity(entity="number"),
                                  self.from_text(not_intent="deny"), ],
            "useful_area": [self.from_entity(entity="distance"),
                            self.from_entity(entity="number"),
                            self.from_text(not_intent="deny"), ],
        }

    def validate_suite_qtt(self, value, dispatcher, tracker, domain):
        slot_dict = {"suite_qtt": None}

        try:
            suite_qtt = int(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_suite_qtt", tracker)
        else:
            if suite_qtt >= 0:
                slot_dict.update({"suite_qtt": suite_qtt})
            else:
                dispatcher.utter_template("utter_wrong_negative", tracker)

        return slot_dict

    def validate_toilet_qtt(self, value, dispatcher, tracker, domain):
        slot_dict = {"toilet_qtt": None}

        try:
            toilet_qtt = int(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_toilet_qtt", tracker)
        else:
            if toilet_qtt >= 0:
                slot_dict.update({"toilet_qtt": toilet_qtt})
            else:
                dispatcher.utter_template("utter_wrong_negative", tracker)

        return slot_dict

    def validate_parking_space_qtt(self, value, dispatcher, tracker, domain):
        slot_dict = {"parking_space_qtt": None}

        try:
            parking_space_qtt = int(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_parking_space_qtt",
                                      tracker)
        else:
            if parking_space_qtt >= 0:
                slot_dict.update({"parking_space_qtt": parking_space_qtt})
            else:
                dispatcher.utter_template("utter_wrong_negative", tracker)

        return slot_dict

    def validate_useful_area(self, value, dispatcher, tracker, domain):
        slot_dict = {"useful_area": None}

        try:
            useful_area = float(value)
        except Exception:
            dispatcher.utter_template("utter_wrong_useful_area", tracker)
        else:
            if useful_area >= 0:
                slot_dict.update({"useful_area": useful_area})
            else:
                dispatcher.utter_template("utter_wrong_negative", tracker)

        return slot_dict

    def submit(self, dispatcher, tracker, domain):
        return []
