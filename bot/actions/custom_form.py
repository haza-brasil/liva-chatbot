import logging
import unidecode

from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet

logger = logging.getLogger(__name__)


class CustomFormAction(FormAction):
    def name(self):
        return "custom_form"

    def simple_text(self, text):
        return unidecode.unidecode(text.lower())

    def validate_slots(self, slot_dict, dispatcher, tracker, domain):
        for slot, value in list(slot_dict.items()):
            validate_func = getattr(
                self, "validate_{}".format(slot), lambda *x: {slot: value}
            )
            validation_out = validate_func(value, dispatcher, tracker, domain)

            for value, key in list(validation_out.items()):
                slot_dict.update({value: key})

        # validation succeed, set slots to extracted values
        return [SlotSet(slot, value) for slot, value in slot_dict.items()]

    def request_next_slot(self, dispatcher, tracker, domain):
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.debug("Request next slot '{}'".format(slot))

                should_use_ask_template = True

                error_utters = ["wrong_", "cant_"]

                for msg in dispatcher.messages:
                    template = msg.get("template")

                    # checking if any error utter can be found on template
                    if template:
                        if any(map(lambda w: w in template, error_utters)):
                            should_use_ask_template = False
                            break

                if should_use_ask_template:
                    dispatcher.utter_template(
                        "utter_ask_{}".format(slot),
                        tracker,
                        silent_fail=False,
                        **tracker.slots
                    )
                return [SlotSet("requested_slot", slot)]
        return None
