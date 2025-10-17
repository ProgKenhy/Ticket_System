THIS_FILE := $(lastword $(MAKEFILE_LIST))
.PHONY: help build up start down destroy stop restart logs logs-api ps login-timescale login-api db-shell migrate create upgrade current

help:
	@echo "Available targets:"
	@echo "  build        - Build the Docker images"
	@echo "  up           - Start the containers in detached mode"
	@echo "  start        - Start existing containers"
	@echo "  down         - Stop and remove containers and networks"
	@echo "  destroy      - Stop and remove containers, networks, images, and volumes"
	@echo "  stop         - Stop running containers"
	@echo "  restart      - Restart containers"
	@echo "  logs         - View container logs (last 100 lines)"
	@echo "  logs-api     - View API container logs (last 100 lines)"
	@echo "  ps           - List running containers"
	@echo "  login-timescale - Open a bash shell in the timescale container"
	@echo "  login-api    - Open a bash shell in the API container"
	@echo "  db-shell     - Open a PostgreSQL shell in the timescale container"
build:
	docker-compose -f docker-compose.yml build $(c)
up:
	docker-compose -f docker-compose.yml up -d $(c)
start:
	docker-compose -f docker-compose.yml start $(c)
down:
	docker-compose -f docker-compose.yml down $(c) && docker network prune --force

destroy:
	docker-compose -f docker-compose.yml down -v $(c)
stop:
	docker-compose -f docker-compose.yml stop $(c)
restart:
	docker-compose -f docker-compose.yml stop $(c)
	docker-compose -f docker-compose.yml up -d $(c)
logs:
	docker-compose -f docker-compose.yml logs --tail=50 -f $(c)
logs-api:
	docker-compose -f docker-compose.yml logs --tail=50 -f api
ps:
	docker-compose -f docker-compose.yml ps
login-timescale:
	docker-compose -f docker-compose.yml exec timescale /bin/bash
login-api:
	docker-compose -f docker-compose.yml exec api /bin/bash
db-shell:
	docker-compose -f docker-compose.yml exec timescale psql -Upostgres
migrate:
	docker-compose exec app bash -c "cd /app && alembic revision --autogenerate -m $(message)"
create:
	docker-compose exec app bash -c "cd /app && alembic revision --autogenerate -m $(message)"
upgrade:
	docker-compose exec app bash -c "cd /app && alembic upgrade head"
downgrade:
	docker-compose exec app bash -c "cd /app && alembic downgrade -1"
current:
	docker-compose exec app bash -c "cd /app && alembic current"
history:
	docker-compose exec app bash -c "cd /app && alembic history --verbose"