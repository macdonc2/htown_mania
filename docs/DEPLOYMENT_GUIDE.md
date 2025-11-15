# 🚀 Houston Event Mania - Deployment Guide

## UNLEASH THE AGENTIC POWERHOUSE! 💪🔥

This guide will help you deploy the new multi-agent system to your Azure Kubernetes environment.

## Prerequisites

- ✅ Azure Container Registry (ACR) access: `htownmaniaacr.azurecr.io`
- ✅ Kubernetes cluster with namespace `houston-events`
- ✅ `kubectl` configured with cluster access
- ✅ Docker installed locally for building images
- ✅ Azure CLI installed and authenticated

## Step 1: Authenticate with Azure Container Registry

```bash
# Login to Azure
az login

# Authenticate Docker with ACR
az acr login --name htownmaniaacr
```

## Step 2: Build the Docker Image

The updated Dockerfile includes all new dependencies (PydanticAI, etc.):

```bash
# Build the image
docker build -f infra/docker/Dockerfile -t htownmaniaacr.azurecr.io/houston-event-mania:latest .

# Tag with version (optional but recommended)
docker tag htownmaniaacr.azurecr.io/houston-event-mania:latest \
  htownmaniaacr.azurecr.io/houston-event-mania:v2.0-agentic
```

## Step 3: Push to Azure Container Registry

```bash
# Push latest
docker push htownmaniaacr.azurecr.io/houston-event-mania:latest

# Push versioned tag
docker push htownmaniaacr.azurecr.io/houston-event-mania:v2.0-agentic
```

## Step 4: Update Kubernetes Secrets

Make sure your secrets include the new SerpAPI key:

```bash
# Create or update the secret
kubectl create secret generic houston-event-mania-secrets \
  --from-literal=EVENTS_openai_api_key='your-openai-key' \
  --from-literal=EVENTS_serpapi_key='your-serpapi-key' \
  --from-literal=EVENTS_twilio_account_sid='your-twilio-sid' \
  --from-literal=EVENTS_twilio_auth_token='your-twilio-token' \
  --from-literal=EVENTS_twilio_from_number='+1234567890' \
  --from-literal=EVENTS_sms_recipient='+1234567890' \
  --from-literal=EVENTS_db_host='your-db-host' \
  --from-literal=EVENTS_db_name='events' \
  --from-literal=EVENTS_db_user='postgres' \
  --from-literal=EVENTS_db_password='your-db-password' \
  --from-literal=EVENTS_gmail_address='your-email@gmail.com' \
  --from-literal=EVENTS_gmail_app_password='your-gmail-app-password' \
  --namespace houston-events \
  --dry-run=client -o yaml | kubectl apply -f -
```

**Important:** Get your SerpAPI key from https://serpapi.com/manage-api-key (100 free searches/month!)

## Step 5: Deploy to Kubernetes

### Option A: Using kubectl (Direct K8s Manifests)

```bash
# Apply all manifests
kubectl apply -f infra/k8s/ --namespace houston-events

# Verify deployment
kubectl get cronjob -n houston-events
kubectl get deployment -n houston-events
kubectl get pods -n houston-events
```

### Option B: Using Helm (Recommended)

```bash
# Install or upgrade with Helm
helm upgrade --install houston-event-mania \
  ./charts/houston-event-mania/ \
  --namespace houston-events \
  --create-namespace \
  --values charts/houston-event-mania/values.yaml

# Check status
helm status houston-event-mania -n houston-events
```

## Step 6: Verify the Deployment

### Check CronJob Configuration

```bash
# View the CronJob
kubectl get cronjob houston-event-mania-daily -n houston-events -o yaml

# Verify it has the --agentic flag
kubectl describe cronjob houston-event-mania-daily -n houston-events | grep command
```

You should see: `command: ["python", "-m", "app.workers.run_daily_job", "--agentic"]`

### Trigger a Manual Test Run

```bash
# Create a one-off job from the CronJob
kubectl create job --from=cronjob/houston-event-mania-daily manual-test-1 -n houston-events

# Watch the logs
kubectl logs -f job/manual-test-1 -n houston-events
```

### Check the Logs

```bash
# View CronJob runs
kubectl get jobs -n houston-events

# Get logs from the latest job
LATEST_JOB=$(kubectl get jobs -n houston-events --sort-by=.metadata.creationTimestamp -o name | tail -1)
kubectl logs -f $LATEST_JOB -n houston-events
```

You should see:
```
🤖 Using AGENTIC multi-agent system
🔍 Running search agents in parallel...
🔬 Running review swarm on X events...
✅ AGENTIC WORKFLOW COMPLETE
📊 Stats:
  - Events found: XX
  - Events reviewed: XX
  - Verified events: XX/XX
```

## Step 7: Monitor the System

### Check CronJob Schedule

The CronJob runs at **7:00 AM Central Time** every day:

```bash
kubectl get cronjob houston-event-mania-daily -n houston-events
```

### View Recent Job History

```bash
# List recent jobs
kubectl get jobs -n houston-events --sort-by=.metadata.creationTimestamp

# Check if any failed
kubectl get jobs -n houston-events | grep -v "1/1"
```

### View Application Logs

```bash
# For the web API (if deployed)
kubectl logs -f deployment/houston-event-mania -n houston-events

# For recent CronJob runs
kubectl get jobs -n houston-events -o json | \
  jq -r '.items[] | select(.status.succeeded==1) | .metadata.name' | \
  tail -1 | \
  xargs -I {} kubectl logs job/{} -n houston-events
```

## Architecture Overview

### What Gets Deployed

1. **CronJob**: Runs daily at 7 AM CT with `--agentic` flag
2. **API Deployment** (optional): FastAPI web interface
3. **Secrets**: All API keys and credentials
4. **Ingress** (if enabled): Public access to API

### The Agentic Workflow

When the CronJob runs, it:

1. 🔍 **Search Phase**: Parallel agents query SerpAPI (Google Events), Ticketmaster, and Meetup
2. 🔬 **Review Phase**: Agent swarm validates and enriches events
   - WebSearchEnricherAgent: Uses SerpAPI to verify events
   - RelevanceScoreAgent: Scores events for your preferences
   - DateVerificationAgent: Ensures events are within 7 days
   - ContentEnricherAgent: Scrapes event pages for details
3. 🎤 **Synthesis Phase**: PromoGeneratorAgent creates wrestling-style promo
4. 📧 **Delivery**: Sends email/SMS with promo + event listing + agent reasoning trace

## Troubleshooting

### Image Pull Errors

```bash
# Check if pods can pull the image
kubectl describe pod <pod-name> -n houston-events

# Verify ACR access
az acr repository list --name htownmaniaacr
```

### Secret Issues

```bash
# Verify secret exists and has correct keys
kubectl get secret houston-event-mania-secrets -n houston-events -o yaml

# Check if pods can read secrets
kubectl exec -it <pod-name> -n houston-events -- env | grep EVENTS_
```

### Job Failures

```bash
# Check job status
kubectl describe job <job-name> -n houston-events

# View logs from failed jobs
kubectl logs job/<job-name> -n houston-events
```

### Common Issues

1. **"No module named pydantic_ai"**: Rebuild Docker image with updated Dockerfile
2. **"SerpAPI key not configured"**: Add `EVENTS_serpapi_key` to secrets
3. **Low verification rate**: Check SerpAPI quota at https://serpapi.com/manage-api-key
4. **No events found**: Verify search agents have valid API keys

## Rollback Plan

If something goes wrong:

```bash
# Rollback to previous image tag
kubectl set image cronjob/houston-event-mania-daily \
  worker=htownmaniaacr.azurecr.io/houston-event-mania:previous-tag \
  -n houston-events

# Or switch back to non-agentic mode
kubectl patch cronjob houston-event-mania-daily -n houston-events --type='json' \
  -p='[{"op": "replace", "path": "/spec/jobTemplate/spec/template/spec/containers/0/command", "value": ["python", "-m", "app.workers.run_daily_job"]}]'
```

## Performance Metrics

After deployment, expect:

- **Event Discovery**: 20-30 events from SerpAPI + Ticketmaster
- **Verification Rate**: ~70-75% (vs 18% before)
- **Execution Time**: ~30-45 seconds total
  - Search: 3-5 seconds
  - Review: 20-30 seconds (web searches take time!)
  - Promo: 15-20 seconds
- **Coverage**: 18-20+ events mentioned in promo

## Cost Considerations

### SerpAPI Usage
- Free tier: 100 searches/month
- Daily job uses: ~22 searches (1 per event for enrichment)
- Should last 4-5 days on free tier
- Paid plans start at $50/month for 5,000 searches

### Azure Resources
- Container storage: ~500MB for image
- Job execution: <1 minute compute time/day
- Minimal cost increase vs non-agentic version

## Next Steps

1. ✅ Monitor first few runs to ensure stability
2. ✅ Check email/SMS output for quality
3. ✅ Review agent reasoning traces
4. ✅ Adjust CronJob schedule if needed
5. ✅ Consider adding Meetup API key for more events

## Support & Documentation

- Architecture: `docs/AGENTIC_ARCHITECTURE.md`
- Usage Guide: `docs/AGENTIC_USAGE_GUIDE.md`
- SerpAPI Setup: `docs/SERPAPI_SETUP.md`
- Testing: Run `make test-agentic` locally

---

**DIG IT! OHHH YEAH!** 💪🔥

Your agentic system is now LIVE and ready to deliver BANGING wrestling promos every morning!

