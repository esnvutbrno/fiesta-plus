DJANGO_ADMIN = docker-compose run --rm web python manage.py

CMD = help
ARG =

MODELS_PNG = models.png
GRAPH_MODELS_CMD = graph_models accounts plugins auth \
	--arrow-shape normal \
	--pydot -X 'ContentType|Base*Model'\
	 -g -o $(MODELS_PNG)


all: up

check: ## Runs all included lints/checks/reformats
	poetry run pre-commit run --all-files

migrate: CMD = migrate ## Runs manage.py migrate for all apps
migrate: da

makemigrations: CMD = makemigrations ## Runs manage.py makemigrations for all apps
makemigrations: da

graph_models: CMD = $(GRAPH_MODELS_CMD)
graph_models: da ## Plot all Django models into models.png
	@mv ./fiesta/$(MODELS_PNG) .

da: ## Invokes django-admin command stored in CMD
	$(DJANGO_ADMIN) $(CMD) $(ARG)

build: ## Builds docker images.
	docker-compose build

up: ## Runs all needed docker containers in non-deamon mode
	docker-compose up --build

help: ## Shows help
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST)|awk 'BEGIN {FS = ":.*?## "};{printf "\033[31m%-20s\033[0m %s\n", $$1, $$2}'

DOMAIN = fiesta.localhost

.ONESHELL:
generate-localhost-certs:
	# based on https://github.com/vishnudxb/docker-mkcert/blob/master/Dockerfile
	@mkdir -p .conf/certs
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

trust-localhost-ca:
	mkdir -p /usr/local/share/ca-certificates/localhost
	cp conf/certs/rootCA.pem /usr/local/share/ca-certificates/localhost/rootCA.crt
	update-ca-certificates

.PHONY: all check migrate makemigrations da build up help generate-localhost-certs
