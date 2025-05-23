# Для сборки проекта
install:
	uv sync

# Для старта проекта
dev:
	uv run flask --debug --app page_analyzer:app run

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

check:
	uv run ruff check .

fix:
	uv run ruff check --fix .

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

.PHONY: install build lint test selfcheck check fix