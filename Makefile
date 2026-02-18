# Path to arches-docker infrastructure repo.
# Override via .env file or command line:
#   make ARCHES_DOCKER=~/path/to/arches-docker docker-build
-include .env
export

ARCHES_DOCKER ?= ../arches-docker

# Infrastructure files copied from arches-docker before builds.
# These are gitignored — arches-docker is the source of truth.
# Do not edit them here; edit the originals in $(ARCHES_DOCKER).

.PHONY: docker-prep docker-build docker-up docker-dev docker-init docker-init-dev docker-clean

$(ARCHES_DOCKER):
	git clone https://github.com/fargeo/arches-docker.git $(ARCHES_DOCKER)

docker-prep: $(ARCHES_DOCKER)
	@mkdir -p docker/conf.d docker/nginx
	cp $(ARCHES_DOCKER)/entrypoint.sh docker/entrypoint.sh
	cp $(ARCHES_DOCKER)/supervisor.conf docker/supervisor.conf
	cp $(ARCHES_DOCKER)/conf.d/celeryd.conf docker/conf.d/celeryd.conf
	cp $(ARCHES_DOCKER)/conf.d/celerybeat.conf docker/conf.d/celerybeat.conf
	cp $(ARCHES_DOCKER)/nginx/default.conf docker/nginx/default.conf

docker-build: docker-prep
	docker compose build

docker-up: docker-prep
	docker compose up --build

docker-dev: docker-prep
	docker compose -f docker-compose.dev.yml up --build

docker-init: docker-prep
	docker compose run --rm --build arches-rascolls init_dev_database

docker-init-dev: docker-prep
	docker compose -f docker-compose.dev.yml run --rm --build arches-rascolls init_dev_database

docker-clean:
	rm -f docker/entrypoint.sh docker/supervisor.conf
	rm -f docker/conf.d/celeryd.conf docker/conf.d/celerybeat.conf
	rm -f docker/nginx/default.conf
