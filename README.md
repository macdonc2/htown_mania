# HOUSTON EVENT MANIA — Full Power
Created by Cody *Macho Madness* MacDonald

Mission: 7:00 AM CST daily — scrape Houston events, summarize with OpenAI (cycling/outdoor first), SMS via Twilio, store in Postgres.  
Ingress: https://events.macdoncml.com  
Arch: Hex (ports/adapters), DI, FastAPI, SQLAlchemy (async), Twilio, OAuth, Cron, Helm.

## Quickstart (Local)
```bash
cp .env.example .env  # fill me
docker run --name hem-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=events -p 5432:5432 -d postgres:16
uv sync
uv run alembic upgrade head
uv run uvicorn app.api.main:app --reload
uv run python -m app.workers.run_daily_job
```

## Env (.env)
```
EVENTS_OPENAI_API_KEY=sk-...
EVENTS_OPENAI_MODEL=gpt-4o-mini
EVENTS_TWILIO_ACCOUNT_SID=AC...
EVENTS_TWILIO_AUTH_TOKEN=...
EVENTS_TWILIO_FROM_NUMBER=+1...
EVENTS_SMS_RECIPIENT=+1...
EVENTS_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/events
EVENTS_GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
EVENTS_GOOGLE_CLIENT_SECRET=xxx
EVENTS_ALLOWED_EMAILS="you@gmail.com"
EVENTS_APP_BASE_URL=http://localhost:8000
EVENTS_SESSION_SECRET=<openssl rand -hex 32>
DEV_SMS_MUTE=0
FRONTEND_MODE=html
```

## Dev UX
- HTML front at `/` (Jinja+HTMX).  
- React Neon (stub) at `/neon` as static bundle placeholder (no build step required for dev).  
- Cron @ 7AM CST via K8s CronJob (timeZone=America/Chicago).

## AKS (raw manifests)
```bash
kubectl create ns events || true
kubectl -n events create secret generic houston-event-mania-secrets --from-env-file=.env
kubectl -n events apply -f infra/k8s/
```

## Helm
```bash
helm upgrade --install hem charts/houston-event-mania   --namespace events --create-namespace   --set image.repository=ghcr.io/<you>/houston-event-mania   --set image.tag=latest   --set ingress.host=events.macdoncml.com   --set envFromSecret=houston-event-mania-secrets
```

## Make
```
make dev      # api
make job      # run daily worker
make lint     # ruff
make format   # black
make k-port-forward
```
