first-run:
	docker-compose up -d rocketchat
	docker-compose up -d elasticsearch
	docker-compose up -d kibana

	cd docker/requirements/ && ./build-requirements.sh

	docker-compose build bot
	docker-compose run --rm -v $PWD/analytics:/analytics bot python /analytics/setup_elastic.py --task setup

	docker-compose run --rm bot make train
	docker-compose run --rm bot make config-rocket
	docker-compose up -d bot

	# Actions?

train:
	docker-compose run bot make train

console:
	docker-compose run bot make shell