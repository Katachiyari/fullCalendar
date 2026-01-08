.PHONY: help up down restart logs ps test scan scan-container scan-python

COMPOSE ?= docker compose -f docker-compose.yml
PYTHON ?= ./venv/bin/python

help:
	@echo "Targets: up down restart logs ps test scan"

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

test:
	$(PYTHON) -m pytest -q tests

scan: scan-python scan-container

scan-python:
	bash scripts/security_scan.sh

scan-container:
	bash scripts/container_scan.sh
