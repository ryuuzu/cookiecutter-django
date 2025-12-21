
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
	docker compose -f docker-compose.local.yml run --rm django bash -c "python manage.py shell -c 'from core_apps.academics.models import ReportCard, Student; from core_apps.users.models import User, Staff; from django.contrib.auth.models import Group, Permission; import code; code.interact(local=locals())'"

shell2:
	docker compose -f docker-compose.local.yml run --rm django python manage.py shell

localshell:
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
	docker compose -f docker-compose.local.yml run --rm django python manage.py $(cmd)

cs:
	docker compose -f docker-compose.local.yml exec django python manage.py collectstatic --noinput --clear
