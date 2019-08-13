first-run:
	docker-compose up mongo-init-replica
	docker-compose up -d rocketchat
	docker-compose up -d elasticsearch
	docker-compose up -d kibana

	cd docker/requirements/ && ./build-requirements.sh

	docker-compose build bot
	docker-compose run --rm -v $PWD/analytics:/analytics bot python /analytics/setup_elastic.py --task setup

	docker-compose run --rm bot make train
	docker-compose run --rm bot make config-rocket
	docker-compose up -d bot

	docker-compose up -d kibana-web

	# Actions?

train:
	docker-compose run bot make train

train-nlu:
	docker-compose run bot make train-nlu

console:
	docker-compose run bot make shell