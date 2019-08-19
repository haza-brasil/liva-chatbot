## Wanna Buy - Happy Path 1
* greet
    - utter_greet
* ask_how_doing
    - utter_ask_how_doing
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
    - form{"name": null}
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - action_post_lead
* bye
    - utter_bye

## Wanna Buy - Happy Path 2
* greet
    - utter_greet
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
    - form{"name": null}
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - action_post_lead
* bye
    - utter_bye

## Wanna Buy - Happy Path 3
* greet+ask_how_doing
    - utter_greet_ask_how_doing
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
    - form{"name": null}
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - action_post_lead
* bye
    - utter_bye

## Wanna Buy - Happy Path 4
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
    - form{"name": null}
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - action_post_lead
* bye
    - utter_bye

## Wanna Buy + Almost Cancel Lead Form
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
    - form{"name": null}
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}

## Sell
* i_wanna_sell
    - utter_sell

## Rent
* i_wanna_rent
    - utter_rent
