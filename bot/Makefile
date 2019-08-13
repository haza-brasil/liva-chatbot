train:
	rasa train --fixed-model-name current --verbose

train-nlu:
	rasa train nlu --fixed-model-name nlu

shell:
	rasa shell -m models/current.tar.gz --endpoints endpoints_shell.yml --debug

nlu-shell:
	rasa shell nlu --debug

run-actions:
	rasa run actions --actions actions

rasa-run:
	rasa run --endpoints endpoints.yml --log-file bot.log

rasa-run-debug:
	rasa run --endpoints endpoints.yml --log-file bot.log --debug

api:
	rasa run --enable-api

create-neighborhoods:
	python3 neighborhoods/neighborhoods.py

config-rocket:
	python /scripts/bot_config.py
