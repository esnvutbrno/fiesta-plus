SHELL := /bin/bash
IN_FIESTA := @cd . &&

.PHONY:
all: install runserver

.PHONY:
check: ## Runs all included lints/checks/reformats
	$(IN_FIESTA) poetry run pre-commit run --all-files

.PHONY:
install: ./fiesta/pyproject.toml ./fiesta/poetry.lock ## Installs deps from pyproject.toml and poetry lockfile
	$(IN_FIESTA) poetry install

.PHONY:
runserver: ## Runs django server in development mode OUT of docker
	$(IN_FIESTA) poetry run python fiesta/manage.py runserver


build:
	docker-compose build

up:
	docker-compose up

.PHONY:
help: ## Shows help
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST)|awk 'BEGIN {FS = ":.*?## "};{printf "\033[31m%-20s\033[0m %s\n", $$1, $$2}'
