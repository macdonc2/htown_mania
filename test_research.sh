#!/bin/bash
# Test runner for deep research system
# Run this to verify all research components without hitting API limits!

set -e

echo "🎤 ============================================================"
echo "🎤 MACHO MAN'S RESEARCH SYSTEM TEST SUITE - OH YEAH!"
echo "🎤 ============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔬 Testing Deep Research Domain Models (Unit Tests)${NC}"
echo "================================================================"
uv run pytest tests/unit/domain/test_research_models.py -v -m unit
echo ""

echo -e "${BLUE}🔬 Testing Research Port Contracts (Contract Tests)${NC}"
echo "================================================================"
uv run pytest tests/contract/research/test_research_ports.py -v -m contract
echo ""

echo -e "${BLUE}🔬 Testing Full Research Workflow (Integration Tests)${NC}"
echo "================================================================"
uv run pytest tests/integration/research/test_deep_research_workflow.py -v -m integration
echo ""

echo -e "${GREEN}🎤 ============================================================${NC}"
echo -e "${GREEN}🎤 ALL TESTS COMPLETE - DIG IT!${NC}"
echo -e "${GREEN}🎤 ============================================================${NC}"
echo ""
echo -e "${YELLOW}📊 Test Summary:${NC}"
uv run pytest tests/unit/domain/test_research_models.py tests/contract/research/test_research_ports.py tests/integration/research/test_deep_research_workflow.py --tb=no -q
echo ""
echo -e "${GREEN}✅ Your research system is READY TO RUMBLE, BROTHER!${NC}"
echo -e "${YELLOW}💡 When your API quota resets, run:${NC}"
echo "   uv run python -m app.workers.run_daily_job --deep-research --no-db"

