install:
	uv sync

run:
	uv run database

build:
	uv build

lint:
	uv run ruff check .

check:
	uvx twine check dist/*
