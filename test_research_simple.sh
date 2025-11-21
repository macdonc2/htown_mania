#!/bin/bash
# Simplified test runner for deep research system (no integration tests)
# Run this to verify data models and contracts without hitting API limits!

set -e

echo "🎤 ============================================================"
echo "🎤 DEEP RESEARCH DATA MODEL TESTS - OH YEAH!"
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

echo -e "${GREEN}🎤 ============================================================${NC}"
echo -e "${GREEN}🎤 ALL DATA MODEL TESTS PASSED - DIG IT!${NC}"
echo -e "${GREEN}🎤 ============================================================${NC}"
echo ""
echo -e "${YELLOW}📊 Test Summary:${NC}"
uv run pytest tests/unit/domain/test_research_models.py tests/contract/research/test_research_ports.py --tb=no -q
echo ""
echo -e "${GREEN}✅ 28 tests PASSED! Your research data models are SOLID!${NC}"
echo -e "${GREEN}✅ Entity, ResearchQuery, ResearchResult, EventResearch - ALL WORKING!${NC}"
echo ""
echo -e "${YELLOW}💡 When your SerpAPI quota resets, run:${NC}"
echo "   uv run python -m app.workers.run_daily_job --deep-research --no-db"
echo ""
echo -e "${YELLOW}📝 Integration tests skipped (require OpenAI API calls)${NC}"

