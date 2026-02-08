.PHONY: add manage wipe-out

lint:
	docker compose -f docker-compose.local.yml run --rm django ruff check --fix

format:
	docker compose -f docker-compose.local.yml run --rm django ruff format

pytest:
	docker compose -f docker-compose.local.yml run --rm django pytest tests/

pytest-coverage:
	docker compose -f docker-compose.local.yml run --rm django pytest --cov=core_apps --cov-report=html tests/

bash:
	docker compose -f docker-compose.local.yml run --rm django bash

shell:
	docker compose -f docker-compose.local.yml run --rm django python manage.py shell

migrations:
	docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations

migrate:
	docker compose -f docker-compose.local.yml run --rm django python manage.py migrate

dev-server:
	docker compose -f docker-compose.local.yml up -d --remove-orphans
	docker compose -f docker-compose.local.yml logs django --follow

dev-server-build:
	docker compose -f docker-compose.local.yml up -d --build --remove-orphans
	docker compose -f docker-compose.local.yml logs django --follow

dev-server-build-only:
	docker compose -f docker-compose.local.yml build

remove-dev-server:
	docker compose -f docker-compose.local.yml down

docker-up:
	docker compose -f docker-compose.local.yml up django

manage:
	@docker compose -f docker-compose.local.yml run --rm django \
		python manage.py $(filter-out $@,$(MAKECMDGOALS))

migrate-shared:
	docker compose -f docker-compose.local.yml run --rm django python manage.py migrate_schemas --shared

migrate-tenants:
	docker compose -f docker-compose.local.yml run --rm django python manage.py migrate_schemas

wipe-out:
	@read -p "WARNING: This will delete ALL containers and volumes. Continue? [y/N] " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		docker compose -f docker-compose.local.yml down -v --remove-orphans; \
	else \
		echo "Aborted."; \
	fi

cs:
	docker compose -f docker-compose.local.yml exec django python manage.py collectstatic --noinput --clear

add:
	@docker compose -f docker-compose.local.yml run --rm django uv add $(filter-out $@,$(MAKECMDGOALS))

# Prevent make from treating the argument as a target
%:
	@:
