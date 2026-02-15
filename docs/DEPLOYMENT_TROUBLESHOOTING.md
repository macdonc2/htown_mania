# Deployment Troubleshooting Guide

## Docker Push Failures (Broken Pipe / Network Connection Issues)

### Problem
When running `./deploy.sh`, you encounter errors like:
```
failed to copy: write tcp ... broken pipe
failed to copy: write tcp ... use of closed network connection
```

### Solutions

#### 1. Updated deploy.sh with Retry Logic (v2.2.0+)
The latest `deploy.sh` includes automatic retry logic with exponential backoff:
- 5 retry attempts per image
- 10s initial delay, doubling each retry
- Automatic recovery from transient network issues

#### 2. Check Docker Desktop Settings
If retries still fail, check your Docker Desktop configuration:

**macOS Docker Desktop:**
1. Open Docker Desktop → Settings → Resources
2. Increase CPUs to 4+ and Memory to 8GB+ if available
3. Go to Docker Desktop → Settings → Docker Engine
4. Check if you have proxy settings that might be causing issues
5. Restart Docker Desktop

**Network Proxy Issues:**
If you're behind a corporate proxy or VPN:
```bash
# Check if proxy is causing issues
docker info | grep -i proxy

# If needed, configure Docker to bypass proxy for Azure
# Add to ~/.docker/config.json:
{
  "proxies": {
    "default": {
      "noProxy": "*.azurecr.io,*.azure.com"
    }
  }
}
```

#### 3. Manual Push with Lower Concurrency
If automatic retries still fail, try manually pushing with reduced concurrency:

```bash
# Build the image first
docker build -f infra/docker/Dockerfile \
    --platform linux/amd64 \
    -t htownmaniaacr.azurecr.io/houston-event-mania:latest \
    .

# Push with limited concurrent uploads (reduces network load)
docker push --max-concurrent-uploads 1 htownmaniaacr.azurecr.io/houston-event-mania:latest
```

#### 4. Check Network Stability
```bash
# Test connection to Azure Container Registry
curl -v https://htownmaniaacr.azurecr.io/v2/

# Check for packet loss
ping -c 10 htownmaniaacr.azurecr.io
```

#### 5. Alternative: Use Azure CLI
If Docker push continues to fail, use Azure CLI:

```bash
# Build and push in one command
az acr build --registry htownmaniaacr \
    --image houston-event-mania:latest \
    --platform linux/amd64 \
    --file infra/docker/Dockerfile \
    .
```

### After Successful Push

Once the image is pushed, continue with Kubernetes deployment:

```bash
# Deploy with Helm
helm upgrade --install houston-event-mania \
    ./charts/houston-event-mania/ \
    --namespace houston-events \
    --set image.tag=latest \
    --wait

# Force pod restart to use new image
kubectl rollout restart deployment houston-event-mania-api -n houston-events
kubectl delete jobs -l app=houston-event-mania -n houston-events
```

## Other Common Issues

### Image Pull Policy Issues
If CronJob uses old image despite new push:

```bash
# Ensure pullPolicy is Always (done in v2.1.5+)
grep pullPolicy charts/houston-event-mania/values.yaml

# Should show: pullPolicy: Always
```

### Helm Conflicts
If Helm shows ownership conflicts:

```bash
# Delete conflicting resources
kubectl delete deployment/houston-event-mania-api -n houston-events
kubectl delete cronjob/houston-event-mania-daily -n houston-events

# Then rerun deploy.sh
./deploy.sh
```

### Check Deployment Status
```bash
# View CronJob
kubectl get cronjob -n houston-events

# View recent jobs
kubectl get jobs -n houston-events --sort-by=.metadata.creationTimestamp

# View logs from latest job
kubectl logs -f job/$(kubectl get jobs -n houston-events -o jsonpath='{.items[-1].metadata.name}') -n houston-events
```

## Need More Help?

- Check logs: `kubectl logs -n houston-events -l app=houston-event-mania`
- Verify secrets: `kubectl get secret houston-event-mania-secrets -n houston-events`
- Check ACR connection: `az acr login --name htownmaniaacr`

**OHHH YEAH, BROTHER!** 💪🔥
