DC = docker-compose
DCRUNFLAGS = --rm $(MATCH_LOCAL_USER)
MATCH_LOCAL_USER = --entrypoint 'sh -c' --user $(shell id -u):$(shell id -g)

WEB_CMD = $(DC) run $(DCRUNFLAGS) web
DJANGO_ADMIN =  $(WEB_CMD) python manage.py

cmd ?= help
DA_CMD = $(cmd)
ARG =

MODELS_PNG = models.png
GRAPH_MODELS_CMD = graph_models accounts plugins auth sections universities esncards \
	--verbose-names --disable-sort-fields \
	--pydot -X 'ContentType|Base*Model' \
	 -g -o $(MODELS_PNG)

all: up

pre-commit: ## Runs all included lints/checks/reformats
	poetry run pre-commit run --all-files

startplugin: DA_CMD = startplugin ## Create plugin in project with name=
startplugin: ARG = $(name)
startplugin: da

migrate: DA_CMD = migrate ## Runs manage.py migrate for all apps
migrate: da

check: DA_CMD = check ## Runs all Django checks.
check: da

makemigrations: DA_CMD = makemigrations ## Runs manage.py makemigrations for all apps
makemigrations: da

graph_models: DA_CMD = $(GRAPH_MODELS_CMD)
graph_models: da ## Plot all Django models into models.png
	@mv ./fiesta/$(MODELS_PNG) .

da: ## Invokes django-admin command stored in cmd=
	$(DC) run $(DCRUNFLAGS) web "python manage.py $(DA_CMD) $(ARG)"

build: ## Builds docker images.
	docker-compose build

upb: ## Build and runs all needed docker containers in non-deamon mode
	docker-compose up --build

upbd: ## Build and runs all needed docker containers in detached mode
	docker-compose up --build --detach

upd: ## Runs all needed docker containers in detached mode
	docker-compose up --detach

up: ## Runs all needed docker containers
	docker-compose up

produp: export DJANGO_CONFIGURATION = LocalProduction ## Runs fiesta in production mode.
produp:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up --build

help: ## Shows help
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST)|awk 'BEGIN {FS = ":.*?## "};{printf "\033[31m%-32s\033[0m %s\n",$$1, $$2}'

generate-localhost-certs: ## Generates self-signed localhost certs for working HTTPS.
generate-localhost-certs: \
	conf/certs/fiesta.localhost.crt \
	conf/certs/*.fiesta.localhost.crt \
	conf/certs/web.localhost.crt \
	conf/certs/webpack.localhost.crt \
	conf/certs/kibana.localhost.crt \
	conf/certs/elastic.crt


# based on https://github.com/vishnudxb/docker-mkcert/blob/master/Dockerfile
.ONESHELL:
conf/certs/%.crt: TARGET = $@
conf/certs/%.crt: DOMAIN = "$(TARGET:conf/certs/%.crt=%)"
conf/certs/%.crt:
	@mkdir -p conf/certs
	docker run \
		--rm \
		--name mkcert \
		--volume `pwd`/conf/certs:/root/.local/share/mkcert \
		vishnunair/docker-mkcert \
		sh -c "mkcert -install && \
			mkcert $(DOMAIN) && \
			chown -R `id -u`:`id -g` ./ && \
			mv $(DOMAIN).pem $(DOMAIN).crt && \
			mv $(DOMAIN)-key.pem $(DOMAIN).key"

.ONESHELL:
setup-elastic: ## Starts elasticsearch standalone an generates keystore and passwords for all users.
	docker run \
		-i -t --rm \
		--volume $(shell pwd)/conf/elastic/:/usr/share/elasticsearch/config/ \
		elasticsearch:7.17.0 \
		sh -c "elasticsearch-keystore create auto"
	sudo chown -v 1000 ./conf/elastic/elasticsearch.keystore

	docker container stop buena-fiesta-elastic-setup-run | true
	docker container rm buena-fiesta-elastic-setup-run | true

	docker-compose run -d --name buena-fiesta-elastic-setup-run --rm elastic
	docker container exec -it buena-fiesta-elastic-setup-run bash -c \
	'sleep 25 && elasticsearch-setup-passwords interactive'
	docker stop buena-fiesta-elastic-setup-run
	docker rm buena-fiesta-elastic-setup-run


# chrome://settings/certificates
trust-localhost-ca: ## Copies generted CA cert to trusted CA certs and updates database -- requires sudo.
	mkdir -p /usr/local/share/ca-certificates/localhost
	cp conf/certs/rootCA.pem /usr/local/share/ca-certificates/localhost/rootCA.crt
	update-ca-certificates

.PHONY: all check migrate makemigrations da build up help generate-localhost-certs
