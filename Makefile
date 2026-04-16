.DEFAULT_GOAL := help

COMPOSE := docker compose
BACKEND_SERVICE := backend
FRONTEND_SERVICE := frontend
ENV_FILE := .env

.PHONY: help init-env bootstrap up up-d down build logs ps shell be-shell fe-shell migrate superuser test test-be schema schema-validate worker validate-agents-manifest validate-backend-conventions ci

help: ## Zeigt verfügbare Make-Targets
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init-env: ## Legt lokale .env aus .env.example an (ohne overwrite)
	@if [ -f "$(ENV_FILE)" ]; then \
		echo "$(ENV_FILE) existiert bereits."; \
	else \
		cp .env.example $(ENV_FILE); \
		echo "$(ENV_FILE) wurde aus .env.example angelegt."; \
	fi

bootstrap: init-env up ## Initialisiert .env und startet den Stack

up: ## Startet den lokalen Stack (foreground)
	$(COMPOSE) up --build

up-d: ## Startet den lokalen Stack (detached)
	$(COMPOSE) up -d --build

down: ## Stoppt den lokalen Stack
	$(COMPOSE) down

build: ## Baut alle Images neu
	$(COMPOSE) build

logs: ## Folgt den Logs aller Services
	$(COMPOSE) logs -f

ps: ## Zeigt den Status der Services
	$(COMPOSE) ps

shell: be-shell ## Alias für Backend-Shell

be-shell: ## Öffnet eine Shell im Backend-Container
	$(COMPOSE) exec $(BACKEND_SERVICE) sh

fe-shell: ## Öffnet eine Shell im Frontend-Container
	$(COMPOSE) exec $(FRONTEND_SERVICE) sh

migrate: ## Führt Django-Migrationen aus (explizit)
	$(COMPOSE) exec $(BACKEND_SERVICE) python manage.py migrate

superuser: ## Erstellt einen Django-Superuser
	$(COMPOSE) exec $(BACKEND_SERVICE) python manage.py createsuperuser

test: test-be ## Standard-Testtarget (Backend)

test-be: ## Führt Backend-Tests aus
	$(COMPOSE) exec $(BACKEND_SERVICE) pytest

schema: ## Generiert OpenAPI-Schema im Backend
	$(COMPOSE) exec $(BACKEND_SERVICE) python manage.py spectacular --file schema.yaml

schema-validate: ## Validiert OpenAPI-Schema
	$(COMPOSE) exec $(BACKEND_SERVICE) python manage.py spectacular --validate --fail-on-warn

worker: ## Startet optional nur den Worker-Service
	$(COMPOSE) up worker

validate-agents-manifest: ## Validiert docs/engineering/agents/manifest.json und referenzierte Dateien
	python scripts/validate_agents_manifest.py

validate-backend-conventions: ## Prueft Backend-Struktur und Naming-Conventions gemaess Engineering-Regeln
	bash scripts/validate_backend_conventions.sh

ci: ## Führt einen lokalen CI-ähnlichen Lauf aus
	$(MAKE) validate-agents-manifest
	$(MAKE) validate-backend-conventions
	$(MAKE) test-be
