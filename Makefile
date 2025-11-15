DEV?=1
.PHONY: dev run job job-agentic format lint pre-commit docker-build docker-run k-port-forward test test-agentic test-unit test-integration

dev:
	uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

run: dev

job:
	uv run python -m app.workers.run_daily_job

job-agentic:
	@echo "🤖 Running AGENTIC multi-agent system..."
	uv run python -m app.workers.run_daily_job --agentic

format:
	uv run black app

lint:
	uv run ruff check app

test:
	uv run pytest -q

test-agentic:
	@echo "🧪 Testing agentic system..."
	uv run pytest tests/unit/agents tests/contract/agents tests/integration/agents -v

test-unit:
	uv run pytest -m unit -q

test-integration:
	uv run pytest -m integration -q

pre-commit:
	uv run pre-commit install

docker-build:
	docker build -f infra/docker/Dockerfile -t houston-event-mania:local .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env houston-event-mania:local

k-port-forward:
	kubectl -n events port-forward svc/houston-event-mania 8000:80
