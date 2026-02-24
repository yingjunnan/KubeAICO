.PHONY: backend-dev frontend-dev backend-test compose-up compose-down

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend-dev:
	cd frontend && npm run dev

backend-test:
	cd backend && python3 -m pytest -q

compose-up:
	docker compose up --build

compose-down:
	docker compose down
