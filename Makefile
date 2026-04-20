.DEFAULT_GOAL := help

COMPOSE := docker compose
BACKEND_SERVICE := backend
FRONTEND_SERVICE := frontend
ENV_FILE := .env

.PHONY: help init-env bootstrap up up-d down build logs logs-frontend logs-fe logs-backend logs-be ps shell be-shell fe-shell restart-frontend restart-fe restart-backend restart-be recreate-frontend recreate-fe recreate-backend recreate-be makemigrations migrate create-superuser createsuperuser superuser test test-be schema schema-validate worker beat validate-agents-manifest validate-backend-conventions validate-text-encoding ci

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

logs-frontend: ## Folgt den Logs des Frontend-Services
	$(COMPOSE) logs -f $(FRONTEND_SERVICE)

logs-fe: logs-frontend ## Alias für Frontend-Logs

logs-backend: ## Folgt den Logs des Backend-Services
	$(COMPOSE) logs -f $(BACKEND_SERVICE)

logs-be: logs-backend ## Alias für Backend-Logs

ps: ## Zeigt den Status der Services
	$(COMPOSE) ps

shell: be-shell ## Alias für Backend-Shell

be-shell: ## Öffnet eine Shell im Backend-Container
	$(COMPOSE) exec $(BACKEND_SERVICE) sh

fe-shell: ## Öffnet eine Shell im Frontend-Container
	$(COMPOSE) exec $(FRONTEND_SERVICE) sh

restart-frontend: ## Restart des Frontend-Services
	$(COMPOSE) restart $(FRONTEND_SERVICE)

restart-fe: restart-frontend ## Alias für Frontend-Restart

restart-backend: ## Restart des Backend-Services
	$(COMPOSE) restart $(BACKEND_SERVICE)

restart-be: restart-backend ## Alias für Backend-Restart

recreate-frontend: ## Recreate des Frontend-Services (z. B. nach Port-/Compose-Aenderungen)
	$(COMPOSE) up -d --force-recreate --no-deps $(FRONTEND_SERVICE)

recreate-fe: recreate-frontend ## Alias fuer Frontend-Recreate

recreate-backend: ## Recreate des Backend-Services (z. B. nach Compose-Aenderungen)
	$(COMPOSE) up -d --force-recreate --no-deps $(BACKEND_SERVICE)

recreate-be: recreate-backend ## Alias fuer Backend-Recreate

makemigrations: ## Erzeugt neue Django-Migrationsdateien
	$(COMPOSE) exec $(BACKEND_SERVICE) python manage.py makemigrations

migrate: ## Führt Django-Migrationen aus (explizit)
	$(COMPOSE) exec $(BACKEND_SERVICE) python manage.py migrate

create-superuser: ## Erstellt einen Django-Superuser
	$(COMPOSE) exec $(BACKEND_SERVICE) python manage.py createsuperuser

createsuperuser: create-superuser ## Alias fuer create-superuser

superuser: create-superuser ## Alias fuer create-superuser

test: test-be ## Standard-Testtarget (Backend)

test-be: ## Führt Backend-Tests aus
	$(COMPOSE) exec $(BACKEND_SERVICE) pytest

schema: ## Generiert OpenAPI-Schema im Backend
	$(COMPOSE) exec $(BACKEND_SERVICE) python manage.py spectacular --file schema.yaml

schema-validate: ## Validiert OpenAPI-Schema
	$(COMPOSE) exec $(BACKEND_SERVICE) python manage.py spectacular --validate --fail-on-warn

worker: ## Startet optional nur den Worker-Service
	$(COMPOSE) up worker

beat: ## Startet optional nur den Celery-Beat-Service
	$(COMPOSE) up beat

validate-agents-manifest: ## Validiert docs/engineering/agents/manifest.json und referenzierte Dateien
	python3 scripts/validate_agents_manifest.py

validate-backend-conventions: ## Prueft Backend-Struktur und Naming-Conventions gemaess Engineering-Regeln
	bash scripts/validate_backend_conventions.sh

validate-text-encoding: ## Prueft Textdateien auf gueltiges UTF-8 ohne Null-Bytes
	python3 scripts/check_text_encoding.py

ci: ## Führt einen lokalen CI-ähnlichen Lauf aus
	$(MAKE) validate-agents-manifest
	$(MAKE) validate-backend-conventions
	$(MAKE) validate-text-encoding
	$(MAKE) test-be
