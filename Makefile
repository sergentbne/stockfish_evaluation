.PHONY: run clean install test lint fmt typecheck

run:
	uv run main.py

clean:
	rm -rf .cache .venv __pycache__ data

install:
	@echo "TODO"

test:
	@echo "TODO"

lint:
	uv run ruff check .

fmt:
	uv run ruff format .

typecheck:
	@echo "TODO"
