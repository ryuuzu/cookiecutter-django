.PHONY: lint format pytest pytest-coverage bash shell migrations migrate \
        dev-server dev-server-build dev-server-build-only remove-dev-server \
        docker-up manage migrate-shared migrate-tenants wipe-out cs add logs

IMAGE_NAME={{ cookiecutter.project_slug }}_local_django

COMPOSE_LOCAL = docker compose -f docker-compose.local.yml
COMPOSE_BUILD = docker compose -f docker-compose.local.build.yml

# Get running django container (prefer service-based, safer)
RUNNING_DJANGO = $(shell $(COMPOSE_LOCAL) ps -q django)

# Smart runner: exec if running, else run --rm
define RUN_SMART
@if [ -n "$(RUNNING_DJANGO)" ]; then \
	echo "Using running django container"; \
	docker exec -it $(RUNNING_DJANGO) $(1); \
else \
	echo "No running container found. Using run --rm"; \
	$(COMPOSE_LOCAL) run --rm django $(1); \
fi
endef

# -------------------------
# Dev helpers
# -------------------------

lint:
	$(call RUN_SMART,ruff check --fix)

format:
	$(call RUN_SMART,ruff format)

pytest:
	$(call RUN_SMART,pytest tests/)

pytest-coverage:
	$(call RUN_SMART,pytest --cov=core_apps --cov-report=html tests/)

bash:
	$(call RUN_SMART,bash)

shell:
	$(call RUN_SMART,python manage.py shell)

migrations:
	$(call RUN_SMART,python manage.py makemigrations)

migrate:
	$(call RUN_SMART,python manage.py migrate)


cs:
	$(call RUN_SMART,python manage.py collectstatic --noinput --clear)

createsuperuser:
	$(call RUN_SMART,python manage.py createsuperuser)

add:
	@$(call RUN_SMART,uv add $(filter-out $@,$(MAKECMDGOALS)))

# -------------------------
# Dev server
# -------------------------

dev-server:
	@if [ -z "$$(docker images -q $(IMAGE_NAME))" ]; then \
		echo "Image missing. Building..."; \
		$(COMPOSE_BUILD) build; \
	fi
	$(COMPOSE_LOCAL) up -d --remove-orphans
	$(COMPOSE_LOCAL) logs django --follow

dev-server-build:
	$(COMPOSE_BUILD) build
	$(COMPOSE_LOCAL) up -d --remove-orphans
	$(COMPOSE_LOCAL) logs django --follow

dev-server-build-only:
	$(COMPOSE_BUILD) build

remove-dev-server:
	$(COMPOSE_LOCAL) down

docker-up:
	$(COMPOSE_LOCAL) up django

logs:
	$(COMPOSE_LOCAL) logs django --follow

# -------------------------
# Management
# -------------------------

manage:
	@$(call RUN_SMART,python manage.py $(filter-out $@,$(MAKECMDGOALS)))

# -------------------------
# Dangerous stuff ☠️
# -------------------------

wipe-out:
	@echo "Type 'yes' to confirm:"; \
	read ans; \
	if [ "$$ans" = "yes" ]; then \
		$(COMPOSE_LOCAL) down -v --remove-orphans; \
	else \
		echo "Aborted."; \
	fi

# Prevent make from treating args as targets
%:
	@:
