## Greet + How doing + affirm
* greet
    - utter_greet
* ask_how_doing
    - utter_ask_how_doing
* affirm
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

## How doing
* ask_how_doing
    - utter_ask_how_doing
* affirm
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

## How doing
* ask_how_doing
    - utter_ask_how_doing
* deny
    - utter_great

## Wanna Buy - Happy Path
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

## Wanna Buy - Happy Path + deny secondary preferences
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
* deny
    - utter_great
    - action_post_lead

## Wanna Buy - Happy Path, Greet
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

## Wanna Buy - Happy Path, Greet, deny secondary
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
* deny
    - utter_great
    - action_post_lead

## Wanna Buy - Happy Path, Greet, how_doing
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

## Wanna Buy - Happy Path, Greet, how_doing, deny secondary
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
* deny
    - utter_great
    - action_post_lead

## Wanna Buy, almost deny lead_form
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
* deny
    - utter_cant_signup
    - utter_ask_continue
* affirm
    - utter_great
    - lead_form
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

## Wanna Buy, almost deny lead_form, deny secondary
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
* deny
    - utter_cant_signup
    - utter_ask_continue
* affirm
    - utter_great
    - lead_form
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
    - form{"name": null}
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* deny
    - utter_great
    - action_post_lead

## Wanna Buy, almost deny lead_form address_form
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
* deny
    - utter_cant_signup
    - utter_ask_continue
* affirm
    - utter_great
    - lead_form
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
* deny
    - utter_cant_signup_without_address
    - utter_ask_continue
* affirm
    - utter_great
    - address_form
    - form{"name": null}
    - primary_preferences_form
    - form{"name": "primary_preferences_form"}
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - action_post_lead

## Wanna Buy, almost deny lead_form address_form primary_form
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
* deny
    - utter_cant_signup
    - utter_ask_continue
* affirm
    - utter_great
    - lead_form
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
* deny
    - utter_cant_signup_without_address
    - utter_ask_continue
* affirm
    - utter_great
    - address_form
    - form{"name": null}
    - primary_preferences_form
* deny
    - utter_cant_signup_without_primary
    - utter_ask_continue
* affirm
    - utter_great
    - primary_preferences_form
    - form{"name": null}
* affirm
    - secondary_preferences_form
    - form{"name": "secondary_preferences_form"}
    - form{"name": null}
    - action_post_lead

## Wanna Buy, deny lead_form
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
* deny
    - utter_cant_signup
    - utter_ask_continue
* deny
    - utter_great
    - action_deactivate_form
    - form{"name": null}

## Wanna Buy, almost deny lead_form, deny address_form
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
* deny
    - utter_cant_signup
    - utter_ask_continue
* affirm
    - utter_great
    - lead_form
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
* deny
    - utter_cant_signup_without_address
    - utter_ask_continue
* deny
    - utter_great
    - action_deactivate_form
    - form{"name": null}

## Wanna Buy, almost deny lead_form address_form, deny primary_form
* i_wanna_buy
    - lead_form
    - form{"name": "lead_form"}
* deny
    - utter_cant_signup
    - utter_ask_continue
* affirm
    - utter_great
    - lead_form
    - form{"name": null}
    - address_form
    - form{"name": "address_form"}
* deny
    - utter_cant_signup_without_address
    - utter_ask_continue
* affirm
    - utter_great
    - address_form
    - form{"name": null}
    - primary_preferences_form
* deny
    - utter_cant_signup_without_primary
    - utter_ask_continue
* deny
    - utter_great
    - action_deactivate_form
    - form{"name": null}

## Sell
* i_wanna_sell
    - utter_sell

## Rent
* i_wanna_rent
    - utter_rent
