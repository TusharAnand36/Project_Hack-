# Upcycle Compass — run targets (no CI). Assumes `make setup` was run once.
PY      ?= .venv/bin/python
API_URL ?= http://localhost:8000

.PHONY: setup api web test types snapshots lint data todo bench e2e

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
	cd web && npm ci

api:
	PYTHONPATH=engine:. $(PY) -m uvicorn api.main:app --reload --port 8000

web:
	cd web && npm run dev

test:
	$(PY) -m pytest -q
	cd web && npm test && npm run build

e2e:  # needs `make api` and `make web` running
	cd web && npm run e2e

types:
	API_URL=$(API_URL) ./scripts/gen_types.sh

snapshots:
	$(PY) scripts/build_snapshots.py

lint:
	$(PY) -m ruff check engine api
	$(PY) -m black --check engine api
	cd web && npm run lint

data:
	cd engine && ../$(PY) -m compass.data --report

todo:
	cd engine && ../$(PY) -m compass.data --todo ../DATA_TODO.md && ../$(PY) -m compass.data --schema ../data/schema

bench:
	PYTHONPATH=engine $(PY) scripts/bench_engine.py
