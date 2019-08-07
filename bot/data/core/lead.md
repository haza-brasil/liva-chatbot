## Wanna Buy - Happy Path 1
* greet
    - utter_greet
* ask_how_doing
    - utter_ask_how_doing
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
    - form{"name": null}
    - zip_code_form
    - form{"name": "zip_code_form"}
    - form{"name": null}
* affirm
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - utter_lead_slot_values
* bye
    - utter_bye

## Wanna Buy - Happy Path 2
* greet
    - utter_greet
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
    - form{"name": null}
    - zip_code_form
    - form{"name": "zip_code_form"}
    - form{"name": null}
* affirm
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - utter_lead_slot_values
* bye
    - utter_bye

## Wanna Buy - Happy Path 3
* greet+ask_how_doing
    - utter_greet_ask_how_doing
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
    - form{"name": null}
    - zip_code_form
    - form{"name": "zip_code_form"}
    - form{"name": null}
* affirm
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - utter_lead_slot_values
* bye
    - utter_bye

## Wanna Buy - Happy Path 4
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
    - form{"name": null}
    - zip_code_form
    - form{"name": "zip_code_form"}
    - form{"name": null}
* affirm
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - utter_lead_slot_values
* bye
    - utter_bye

## Wanna Buy + Almost Cancel Lead Form
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
* deny
    - utter_cant_signup
    - utter_ask_continue_lead_form
* affirm
    - lead_form
    - form{"name": null}
    - zip_code_form
    - form{"name": "zip_code_form"}
    - form{"name": null}
* affirm
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}

## Collect Lead + Cancel lead form
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
* deny
    - utter_cant_signup
    - utter_ask_continue_lead_form
* deny
    - utter_great
    - action_deactivate_form
    - form{"name": null}
    - utter_anything_else

## Sell
* i_wanna_sell
    - utter_sell

## Rent
* i_wanna_rent
    - utter_rent