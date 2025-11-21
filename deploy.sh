#!/bin/bash
# 🚀 Houston Event Mania - Deep Research Deployment Script
# UNLEASH THE POWER! 💪🔥

set -e  # Exit on error

echo "=========================================="
echo "🔬 HOUSTON EVENT MANIA - DEEP RESEARCH DEPLOYMENT"
echo "=========================================="
echo ""

# Configuration
ACR_NAME="htownmaniaacr"
ACR_REGISTRY="${ACR_NAME}.azurecr.io"
IMAGE_NAME="houston-event-mania"
IMAGE_TAG="${1:-latest}"  # Use arg or default to 'latest'
NAMESPACE="houston-events"

echo "📦 Image: ${ACR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
echo "🎯 Namespace: ${NAMESPACE}"
echo ""

# Step 1: Authenticate with Azure
echo "🔐 Step 1: Authenticating with Azure..."
if ! az account show &> /dev/null; then
    echo "⚠️  Not logged into Azure. Running 'az login'..."
    az login
else
    echo "✅ Already authenticated with Azure"
fi

# Step 2: Login to ACR
echo ""
echo "🔐 Step 2: Authenticating with Azure Container Registry..."
az acr login --name ${ACR_NAME}
echo "✅ Authenticated with ACR"

# Step 3: Build Docker image
echo ""
echo "🏗️  Step 3: Building Docker image..."
echo "   Platform: linux/amd64 (for Kubernetes compatibility)"
echo "   This may take a few minutes..."
docker build -f infra/docker/Dockerfile \
    --platform linux/amd64 \
    -t ${ACR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
    -t ${ACR_REGISTRY}/${IMAGE_NAME}:latest \
    .
echo "✅ Image built successfully"

# Step 4: Push to ACR
echo ""
echo "📤 Step 4: Pushing image to Azure Container Registry..."
docker push ${ACR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
if [ "${IMAGE_TAG}" != "latest" ]; then
    docker push ${ACR_REGISTRY}/${IMAGE_NAME}:latest
fi
echo "✅ Image pushed successfully"

# Step 5: Deploy to Kubernetes
echo ""
echo "🚀 Step 5: Deploying to Kubernetes..."

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ kubectl is not configured or cluster is not accessible"
    exit 1
fi

# Create namespace if it doesn't exist
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Check if using Helm or direct manifests
if [ -d "charts/houston-event-mania" ]; then
    echo "📊 Deploying with Helm..."
    helm upgrade --install houston-event-mania \
        ./charts/houston-event-mania/ \
        --namespace ${NAMESPACE} \
        --set image.tag=${IMAGE_TAG} \
        --wait
    echo "✅ Helm deployment complete"
else
    echo "📋 Deploying with kubectl..."
    kubectl apply -f infra/k8s/ --namespace ${NAMESPACE}
    echo "✅ Kubernetes manifests applied"
fi

# Step 6: Verify deployment
echo ""
echo "🔍 Step 6: Verifying deployment..."
echo ""
echo "📊 CronJob Status:"
kubectl get cronjob -n ${NAMESPACE}
echo ""
echo "🎯 Recent Jobs:"
kubectl get jobs -n ${NAMESPACE} --sort-by=.metadata.creationTimestamp | tail -5
echo ""

# Check if deployment exists (for API)
if kubectl get deployment -n ${NAMESPACE} &> /dev/null; then
    echo "🌐 API Deployment Status:"
    kubectl get deployment -n ${NAMESPACE}
    echo ""
fi

# Step 7: Provide next steps
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Verify secrets are configured:"
echo "   kubectl get secret houston-event-mania-secrets -n ${NAMESPACE}"
echo ""
echo "2. Trigger a manual test run:"
echo "   kubectl create job --from=cronjob/houston-event-mania-daily manual-test-\$(date +%s) -n ${NAMESPACE}"
echo ""
echo "3. Watch the logs:"
echo "   kubectl get jobs -n ${NAMESPACE}"
echo "   kubectl logs -f job/<job-name> -n ${NAMESPACE}"
echo ""
echo "4. View CronJob schedule:"
echo "   kubectl get cronjob houston-event-mania-daily -n ${NAMESPACE}"
echo ""
echo "📚 For more information, see docs/DEPLOYMENT_GUIDE.md"
echo ""
echo "OHHH YEAH! DIG IT! 💪🔥"

