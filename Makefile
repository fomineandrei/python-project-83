install:
	uv sync

run:
	uv run page_analyzer

local-test:
	uv run pytest

test-coverage:
	uv run pytest --cov=page_analyzer --cov-report lcov

lint:
	uv run ruff check

check: test lint

build:
	./build.sh

dev:
	uv run flask --debug --app page_analyzer:app run

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

.PHONY: install test lint check build
