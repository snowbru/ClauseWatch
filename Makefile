.PHONY: setup bootstrap migrate seed lint test ci clean reset

setup:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt

bootstrap:
	python scripts/bootstrap.py

migrate:
	python scripts/apply_migrations.py

seed:
	python scripts/seed_sources.py

lint:
	ruff check .

test:
	pytest -q || true

ci: lint test

clean:
	rm -f storage/db.sqlite

reset:
	rm -f storage/db.sqlite
	python scripts/bootstrap.py