train:
	rasa train --fixed-model-name current --verbose

shell:
	rasa shell --endpoints endpoints_shell.yml --debug

run-actions:
	rasa run actions --actions actions

rasa-run:
	rasa run --endpoints endpoints.yml

rasa-run-debug:
	rasa run --endpoints endpoints.yml --debug

config-rocket:
	python /scripts/bot_config.py



run-telegram:
	python -m rasa_core.run -d /models/dialogue -u /models/nlu/current --port 5001 --credentials credentials.yml --endpoints endpoints.yml

run-api:
	python3 -m rasa_core.run -d /models/dialogue -u /models/nlu/current --debug \
  --port 5005 --endpoints endpoints.yml --enable_api

evaluate:
	python3 -m rasa_core.evaluate -d /models/dialogue -s data/core/