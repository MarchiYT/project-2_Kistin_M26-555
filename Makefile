install:
	uv sync

run:
	uv run project

build:
	uv build

lint:
	uv run ruff check .

check:
	uvx twine check dist/*
