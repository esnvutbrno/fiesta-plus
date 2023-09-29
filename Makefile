include .env

export DOCKER_BUILDKIT=1

MATCH_LOCAL_USER = --entrypoint 'sh -c' --user $(shell id -u):$(shell id -g)
DCRUNFLAGS = --rm $(MATCH_LOCAL_USER)
DCFLAGS =

DC = docker compose $(DCFLAGS)

WEB_CMD = $(DC) run $(DCRUNFLAGS) web
DJANGO_ADMIN = $(WEB_CMD) python manage.py

cmd ?= help
DA_CMD = $(cmd)
DC_CMD = $(cmd)
ARG =

MODELS_PNG = models.png
GRAPH_MODELS_CMD = graph_models accounts plugins auth sections \
	universities esncards buddy_system \
	--verbose-names --disable-sort-fields \
	--pydot -X 'ContentType|Base*Model' \
	 -g -o $(MODELS_PNG)

all: up

pre-commit: ## Runs all included lints/checks/reformats
	poetry run pre-commit run --all-files

seed: DA_CMD = seed ## Seed database with fake data.
seed: da

clean_unlinked: DA_CMD = clean_unlinked ## Cleans all unlinked data from database.
clean_unlinked: da

startplugin: DA_CMD = startplugin ## Create plugin in project with name=
startplugin: ARG = $(name)
startplugin: da

shell_plus: DA_CMD = shell_plus ## Starts django shell_plus
shell_plus: da

migrate: DA_CMD = migrate ## Runs manage.py migrate for all apps
migrate: da

optimizemigration: DA_CMD = optimizemigration ## Optimize last migration by optimizemigration: app= migration=
optimizemigration: ARG = $(name) $(migration)
optimizemigration: da

check: DA_CMD = check ## Runs all Django checks.
check: da

makemigrations: DA_CMD = makemigrations ## Runs manage.py makemigrations for all apps
makemigrations: da

loadlegacydata: DA_CMD = loadlegacydata  ## Loads all data from legacydb run from ./legacy.sql.
loadlegacydata: DCFLAGS = --profile migration
loadlegacydata: da

dumpdata: DA_CMD = dumpdata --exclude auth --exclude contenttypes --exclude sessions --exclude sites --exclude admin --natural-foreign
dumpdata: da

fixture ?=
loaddata: DA_CMD = loaddata $(subst fiesta/fiesta,fiesta,$(fixture)) ## Loads all fixtures data from fixture= file
loaddata: da

test: DA_CMD = test --keepdb --parallel --verbosity 1 ## Runs django test cases.
test: da

graph_models: DA_CMD = $(GRAPH_MODELS_CMD)
graph_models: da ## Plot all Django models into models.png
	@mv ./fiesta/$(MODELS_PNG) .

da: ## Invokes django-admin command stored in cmd=
	$(DC) run web "python manage.py $(DA_CMD) $(ARG)"

dc: ## Invokes docker compose command stored in cmd=
	$(DC) $(DC_CMD)

build: DC_CMD = build
build: dc ## Builds docker images for development.

upb: DC_CMD = up --build
upb: dc ## Build and runs all needed docker containers in non-deamon mode

uppd: DC_CMD = up --build --detach
upbd: dc ## Build and runs all needed docker containers in detached mode

upd: DC_CMD = up --detach
upd: dc ## Runs all needed docker containers in detached mode

up: DC_CMD = up
up: dc ## Runs all needed docker containers

produp: ## Runs fiesta in (local)production mode.
	$(DC) -f docker-compose.yml -f docker-compose.prod.yml --profile prod up --build

psql: DC_CMD = run --entrypoint bash db -c "PGPASSWORD=fiesta psql --host db --user fiesta --dbname fiesta"
psql: dc  ## Runs psql shell in database

dumpdb: DC_CMD = run --entrypoint bash db -c "PGPASSWORD=fiesta pg_dump --host db --user fiesta" > dump-`date +%Y-%m-%d-%H:%M:%S`.sql
dumpdb: dc ## Dumps database to .sql

loaddb: DC_CMD = run -T --entrypoint bash db -c "PGPASSWORD=fiesta psql --host db --user fiesta --dbname fiesta" < $(dump)
loaddb: dc ## Loads database from dump=

help: ## Shows help
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST)|awk 'BEGIN {FS = ":.*?## "};{printf "\033[31m%-32s\033[0m %s\n",$$1, $$2}'

generate-local-certs: ## Generates self-signed *.$ROOT_DOMAIN certs for working HTTPS.
generate-local-certs: \
	conf/certs/${ROOT_DOMAIN}.crt \
	conf/certs/*.${ROOT_DOMAIN}.crt \
	conf/certs/web.${ROOT_DOMAIN}.crt \
	conf/certs/webpack.${ROOT_DOMAIN}.crt \
	conf/certs/kibana.${ROOT_DOMAIN}.crt \
	conf/certs/elastic.${ROOT_DOMAIN}.crt


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

	$(DC) run -d --name buena-fiesta-elastic-setup-run --rm elastic
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
