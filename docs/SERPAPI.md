# 🔍 SerpAPI Setup & Usage Guide

**Google Events & Web Search Integration via SerpAPI**

---

## What is SerpAPI?

**SerpAPI** provides programmatic access to Google search results, including:
- **Google Events**: Event listings from Google Search
- **Organic Results**: Web search results
- **Local Results**: Location-based search

We use it for:
1. **Event Discovery**: Finding Houston events via Google Events
2. **Deep Research**: Web search for artist/venue facts

---

## Quick Start

### 1. Get API Key

```bash
# Sign up (free tier: 100 searches/month)
https://serpapi.com/users/sign_up

# Get your API key from dashboard
https://serpapi.com/manage-api-key
```

### 2. Add to Environment

```bash
# Local (.env file)
EVENTS_serpapi_key=your_key_here

# Kubernetes (secret)
kubectl create secret generic houston-event-mania-secrets \
  --from-literal=EVENTS_serpapi_key=your_key_here \
  -n houston-events
```

### 3. Test It

```bash
# Run agentic system (uses SerpAPI for events)
uv run python -m app.workers.run_daily_job --agentic

# Run deep research (uses SerpAPI for research too)
uv run python -m app.workers.run_daily_job --deep-research
```

---

## Usage in Our System

### Event Discovery (SerpAPI Agent)

**File**: `app/adapters/agents/search_agents.py`

```python
from serpapi import GoogleSearch

# Search for Houston events
params = {
    "engine": "google_events",
    "q": "Events in Houston",
    "location": "Houston, TX",
    "htichips": "date:next_3_days",
    "api_key": settings.serpapi_key
}

search = GoogleSearch(params)
results = search.get_dict()
events = results.get("events_results", [])
```

**Typical Response**:
```json
{
  "events_results": [
    {
      "title": "Hot Mulligan - SOLD OUT",
      "date": {
        "start_date": "Nov 16",
        "when": "Sat, 6:00 PM"
      },
      "address": ["House of Blues Houston", "1204 Caroline St"],
      "link": "https://www.houseofblues.com/houston",
      "ticket_info": [
        {"source": "Ticketmaster", "link": "..."}
      ]
    }
  ]
}
```

### Web Research (Deep Research Agent)

**File**: `app/adapters/agents/research/web_search_research_agent.py`

```python
# Research query
params = {
    "engine": "google",
    "q": "What are Hot Mulligan's biggest hit songs?",
    "num": 5,
    "api_key": settings.serpapi_key
}

search = GoogleSearch(params)
results = search.get_dict()
organic = results.get("organic_results", [])

# Extract facts from snippets
facts = [r["snippet"] for r in organic[:5]]
```

---

## API Limits

### Free Tier

- **Searches**: 100/month
- **Cost**: $0
- **Rate Limit**: ~100/hour (burst)

### Paid Plans

| Plan | Searches | Cost | Best For |
|------|----------|------|----------|
| Free | 100/mo | $0 | Testing |
| Hobby | 5,000/mo | $50 | Light production |
| Business | 30,000/mo | $250 | Heavy usage |

### Our Usage

**Without Deep Research** (`--agentic`):
- Event search: ~25 calls
- Total: ~25 calls/run
- **Daily**: 25 calls × 1 run = 25/day
- **Monthly**: ~750 calls → **Hobby plan ($50)**

**With Deep Research** (`--deep-research`):
- Event search: ~25 calls
- Research queries: ~50 calls (2-3 per event)
- Total: ~75 calls/run
- **Daily**: 75 calls × 1 run = 75/day
- **Monthly**: ~2,250 calls → **Hobby plan ($50)**

---

## Rate Limit Management

### Current Strategy

1. **Reduced Queries**: 2-3 per event (down from 3-6)
2. **Reddit Disabled**: Saves 10-20 calls (use `--reddit` to enable)
3. **Caching**: Results cached in DB (future enhancement)
4. **Retry Logic**: Exponential backoff on 429 errors

### If You Hit Limits

```
⚠️ SerpAPI Error (Status 429): Rate limit exceeded
```

**Solutions**:

1. **Wait**: Limits reset hourly
   ```bash
   # Wait 1 hour, then retry
   ```

2. **Reduce Usage**: Disable deep research temporarily
   ```bash
   uv run python -m app.workers.run_daily_job --agentic  # No research
   ```

3. **Upgrade Plan**: $50/mo for 5,000 searches
   ```bash
   # Visit: https://serpapi.com/pricing
   ```

4. **Check Quota**:
   ```bash
   # View dashboard
   https://serpapi.com/account
   ```

---

## Error Handling

### Common Errors

#### 1. Invalid API Key

```
Error 401: Invalid API key
```

**Fix**:
```bash
# Check key is set
echo $EVENTS_serpapi_key

# Verify key is valid
curl "https://serpapi.com/search?engine=google&q=test&api_key=$EVENTS_serpapi_key"
```

#### 2. Rate Limit

```
Error 429: Rate limit exceeded
```

**Fix**:
- Wait 1 hour for reset
- Or upgrade plan

#### 3. No Results

```
organic_results: []
```

**Fix**:
- Query might be too specific
- Try broader search terms
- Check if event/topic exists

---

## Best Practices

### 1. Specific Queries

❌ **Bad**: `"music"`  
✅ **Good**: `"What are Taylor Swift's biggest hit songs and chart performance?"`

### 2. Rate Limit Awareness

```python
# In query generation agent
prompt = """
⚠️ RATE LIMIT: Generate ONLY 2-3 queries (not more!)
to stay under 100 searches/hour limit.
"""
```

### 3. Error Logging

```python
try:
    results = search.get_dict()
except Exception as e:
    logger.error(f"SerpAPI error: {e}")
    if "429" in str(e):
        logger.error("⚠️ Rate limit hit! Wait 1 hour or upgrade plan.")
```

### 4. Confidence Scoring

```python
# Lower confidence if few results
if len(organic) < 3:
    confidence = 0.5  # Low confidence
else:
    confidence = 0.85  # Normal confidence
```

---

## Testing

### Manual Test

```python
from serpapi import GoogleSearch
import os

params = {
    "engine": "google",
    "q": "Houston events this weekend",
    "num": 5,
    "api_key": os.getenv("EVENTS_serpapi_key")
}

search = GoogleSearch(params)
results = search.get_dict()
print(results)
```

### Via Our System

```bash
# Test event discovery
uv run python -m app.workers.run_daily_job --agentic --no-db

# Test deep research
uv run python -m app.workers.run_daily_job --deep-research --no-db
```

---

## Alternatives

If SerpAPI doesn't work for you:

### 1. Google Custom Search API
- **Pros**: Official Google API
- **Cons**: No events support, complex setup
- **Cost**: 100 queries/day free

### 2. Bing Search API
- **Pros**: Microsoft-backed, generous free tier
- **Cons**: Lower quality results
- **Cost**: 1,000 queries/month free

### 3. Direct Scraping
- **Pros**: Free
- **Cons**: Against ToS, fragile, rate-limited
- **Risk**: IP bans

**Recommendation**: Stick with SerpAPI! It's reliable and worth the $50/mo for production.

---

## Monitoring

### Check Usage

```bash
# View dashboard
https://serpapi.com/account

# Shows:
# - Current month usage
# - Remaining searches
# - Plan details
```

### Log Analysis

```bash
# Count SerpAPI calls in logs
grep "SerpAPI" logs.txt | wc -l

# Check for rate limit errors
grep "429" logs.txt

# Check for failed searches
grep "SerpAPI Error" logs.txt
```

---

## Configuration

### Settings

**File**: `app/config/settings.py`

```python
class Settings(BaseSettings):
    serpapi_key: str  # Required for event discovery and research
```

### Dependency Injection

**File**: `app/core/di.py`

```python
serpapi_agent = SerpAPIAgent(
    api_key=settings.serpapi_key,
    location="Houston, TX",
    date_range="next_3_days"
)
```

---

## References

- **SerpAPI Docs**: https://serpapi.com/docs
- **Dashboard**: https://serpapi.com/account
- **Pricing**: https://serpapi.com/pricing
- **Codebase**: `app/adapters/agents/search_agents.py`
- **Deep Research**: [DEEP_RESEARCH.md](DEEP_RESEARCH.md)

---

**OHHH YEAHHH!** SerpAPI is **POWERING YOUR EVENT DISCOVERY**, BROTHER! 🔍🎤

**DIG IT!**

