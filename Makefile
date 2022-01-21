SHELL := /bin/bash

.PHONY:
all: install runserver

.PHONY:
install: pyproject.toml poetry.lock ## Installs deps from pyproject.toml and poetry lockfile
	poetry install

.PHONY:
runserver: ## Runs django server in development mode
	poetry run python fiesta/manage.py runserver

.PHONY:
help: ## Shows help
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST)|awk 'BEGIN {FS = ":.*?## "};{printf "\033[31m%-20s\033[0m %s\n", $$1, $$2}'

