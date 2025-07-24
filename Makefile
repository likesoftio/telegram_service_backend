COMPOSE_LOCAL=docker-compose.yml

# default service name for Django
SERVICE=api

# --- up commands ---
local:
	docker compose -f $(COMPOSE_LOCAL) up --build -d

# --- down commands ---
down-local:
	docker compose -f $(COMPOSE_LOCAL) down

# --- migrations ---
makemigrate-local:
	docker compose -f docker-compose.yml exec $(SERVICE) sh -c "cd src && alembic revision --autogenerate"

migrate-local:
	docker compose -f $(COMPOSE_LOCAL) exec $(SERVICE) sh -c "cd src && alembic upgrade head"