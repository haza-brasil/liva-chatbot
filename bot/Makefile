train:
	rasa train --fixed-model-name current --verbose

shell:
	rasa shell -m models/current.tar.gz --endpoints endpoints_shell.yml --debug

rasa-run:
	rasa run --endpoints endpoints.yml --log-file bot.log

rasa-run-debug:
	rasa run --endpoints endpoints.yml --log-file bot.log --debug

run-actions:
	rasa run actions --actions actions

# only use this if testing nlu separately
train-nlu:
	rasa train nlu --fixed-model-name nlu

nlu-shell:
	rasa shell nlu --debug

api:
	rasa run --enable-api

create-neighborhoods:
	python3 scripts/neighborhoods.py

config-rocket:
	python /scripts/bot_config.py
