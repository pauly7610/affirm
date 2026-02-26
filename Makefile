.PHONY: dev dev-api dev-web db seed test lint eval

# Start everything (Postgres + API + Web)
dev: db dev-api dev-web

# Start just Postgres
db:
	docker compose up -d postgres

# Start backend API
dev-api:
	cd backend && pip install -r requirements.txt -q && uvicorn app.main:app --reload --port 8000

# Start frontend
dev-web:
	cd frontend && npm install --silent && npm run dev

# Seed mock data into Postgres
seed:
	cd backend && python -m app.seed

# Run backend tests
test:
	cd backend && python -m pytest tests/ -v

# Typecheck frontend
lint:
	cd frontend && npx tsc --noEmit

# Run search quality evals
eval:
	cd backend && python -m evals.run_eval

# Quick start: no Docker, in-memory mode
dev-mock:
	@echo "Starting in mock mode (no Postgres required)..."
	@set USE_MOCK_DB=true && cd backend && uvicorn app.main:app --reload --port 8000 &
	@cd frontend && npm run dev
