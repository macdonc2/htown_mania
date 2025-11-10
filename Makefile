DEV?=1
.PHONY: dev run job format lint pre-commit docker-build docker-run k-port-forward

dev:
	uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

run: dev

job:
	uv run python -m app.workers.run_daily_job

format:
	uv run black app

lint:
	uv run ruff check app

pre-commit:
	uv run pre-commit install

docker-build:
	docker build -f infra/docker/Dockerfile -t houston-event-mania:local .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env houston-event-mania:local

k-port-forward:
	kubectl -n events port-forward svc/houston-event-mania 8000:80
