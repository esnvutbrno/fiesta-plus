DJANGO_ADMIN = docker-compose run --rm web python manage.py

CMD = help
ARG =

all: up

check: ## Runs all included lints/checks/reformats
	poetry run pre-commit run --all-files

migrate: CMD = migrate ## Runs manage.py migrate for all apps
migrate: da

.PHONY:
makemigrations: CMD = makemigrations ## Runs manage.py makemigrations for all apps
makemigrations: da

da: ## Invokes django-admin command stored in CMD
	$(DJANGO_ADMIN) $(CMD) $(ARG)

build: ## Builds docker images.
	docker-compose build

up: ## Runs all needed docker containers in non-deamon mode
	docker-compose up

help: ## Shows help
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST)|awk 'BEGIN {FS = ":.*?## "};{printf "\033[31m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: all check migrate makemigrations da build up help
