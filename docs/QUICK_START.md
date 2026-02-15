# Houston Event Mania - Quick Start Guide

**Get running in 5 minutes!** ⚡

---

## ⚡ Fastest Path (No Database!)

```bash
# 1. Clone & setup
git clone <repo>
cd htown_mania
cp .env.example .env

# 2. Add these to .env (minimum required):
EVENTS_OPENAI_API_KEY=sk-...        # Get from platform.openai.com
EVENTS_SERPAPI_KEY=...              # Get from serpapi.com (free tier)
EVENTS_GMAIL_ADDRESS=you@gmail.com  # For email delivery
EVENTS_GMAIL_APP_PASSWORD=...       # Generate in Google Account settings

# 3. Install & run
uv sync
uv run python -m app.workers.run_daily_job --deep-research --no-db
```

**Done!** You'll get an email with a wrestling promo for ~24 Houston events. 🎤

---

## 🔑 Required API Keys

### 1. OpenAI API Key
- **Get it**: https://platform.openai.com/api-keys
- **Cost**: ~$0.05-0.10 per run
- **Models used**: GPT-4o, GPT-4o-mini

### 2. SerpAPI Key  
- **Get it**: https://serpapi.com/users/sign_up
- **Free tier**: 100 searches/month
- **Cost**: First 100 free, then $50/5000 searches

### 3. Gmail App Password
- **Get it**: Google Account → Security → 2-Step Verification → App Passwords
- **Guide**: [SERPAPI_SETUP.md](./SERPAPI_SETUP.md)

---

## 📝 Minimal .env File

```bash
# Required
EVENTS_OPENAI_API_KEY=sk-...
EVENTS_SERPAPI_KEY=...
EVENTS_GMAIL_ADDRESS=your.email@gmail.com
EVENTS_GMAIL_APP_PASSWORD=your-app-password

# Optional (for Ticketmaster events)
EVENTS_TICKETMASTER_API_KEY=...

# Development
DEV_SMS_MUTE=1
EVENTS_OPENAI_MODEL=gpt-5.2-2025-12-11
EVENTS_OPENAI_TEMPERATURE=0.9
```

---

## 🎯 Common Use Cases

### Testing Locally (Recommended)
```bash
uv run python -m app.workers.run_daily_job --deep-research --no-db
```
- ✅ No database needed
- ✅ Get email with results
- ✅ Fast iteration

### Production (Full System)
```bash
# Setup PostgreSQL first
docker run --name hem-pg \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=events \
  -p 5432:5432 -d postgres:16

# Run migrations
uv run alembic upgrade head

# Run full system
uv run python -m app.workers.run_daily_job --deep-research
```

### Pure Testing (No Side Effects)
```bash
uv run python -m app.workers.run_daily_job --deep-research --dry-run
```
- ✅ Tests workflow
- ❌ No email
- ❌ No database

### More Events (Include Reddit)
```bash
uv run python -m app.workers.run_daily_job --deep-research --no-db --reddit
```
- ⚠️  Gets 150+ events (can be noisy)
- ⚠️  May hit SerpAPI rate limits

---

## 🐛 Troubleshooting

### "SerpAPI Error (Status 429): Rate limit exceeded"

**Problem**: You've used your 100 free searches for the hour.

**Solution**: 
1. Wait for reset (check https://serpapi.com/account)
2. Or use base agentic mode: `--agentic --no-db` (no research)

### "No email received"

**Check**:
1. Using `--dry-run`? (This skips email!)
2. Gmail app password correct?
3. Check spam folder

**Debug**:
```bash
uv run python -m app.workers.run_daily_job --deep-research --no-db 2>&1 | grep -i "email"
```

### "PostgreSQL connection failed"

**Problem**: Database not running or `.env` wrong.

**Solution**: Use `--no-db` flag to skip database entirely:
```bash
uv run python -m app.workers.run_daily_job --deep-research --no-db
```

---

## 📊 What to Expect

### Output (--no-db mode)
```
🔬 Using DEEP RESEARCH multi-agent system (Agentic + Research)
🗄️  NO-DB MODE: Will send email but skip database (no PostgreSQL needed!)

📧 Using Email for notifications

================================================================================
🔬 STARTING DEEP RESEARCH EVENT WORKFLOW (Agentic + Research)
================================================================================

============================================================
ITERATION 1: Phase = initializing
============================================================
...

📊 Stats:
  - Events found: 24
  - Events reviewed: 24
  - Entities extracted: 82
  - Research queries: 68
  - Facts gathered: 245

✅ Email sent to your.email@gmail.com
🎉 Job completed!
```

### Email Content
1. **Wrestling Promo** (~500 words)
   - Over-the-top, energetic style
   - Incorporates event research
   - Macho Man / Ultimate Warrior vibes

2. **Event Listing** 
   - Date, time, venue
   - Description
   - Ticket links

3. **Scratchpad** (Optional)
   - Full AI decision log
   - REACT pattern trace
   - Confidence scores

---

## 🚀 Next Steps

Once you're running successfully:

1. **Read the full docs**: [docs/README.md](./README.md)
2. **Understand the architecture**: [DEEP_RESEARCH_AGENT_DESIGN.md](./DEEP_RESEARCH_AGENT_DESIGN.md)
3. **Deploy to production**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
4. **Customize agents**: [DEEP_RESEARCH_IMPLEMENTATION_GUIDE.md](./DEEP_RESEARCH_IMPLEMENTATION_GUIDE.md)

---

## 💡 Pro Tips

1. **Start with `--no-db`**: Fastest way to test
2. **Watch your API costs**: ~$0.10-0.20 per run
3. **Monitor SerpAPI quota**: 100 searches/hour on free tier
4. **Skip Reddit initially**: Adds noise, use `--reddit` only if needed
5. **Use `--dry-run` for testing changes**: No side effects

---

## 🆘 Still Stuck?

1. Check [DEEP_RESEARCH_USAGE.md](./DEEP_RESEARCH_USAGE.md) for detailed usage
2. Review [SERPAPI_SETUP.md](./SERPAPI_SETUP.md) for API key setup
3. See [Common Issues](./DEEP_RESEARCH_USAGE.md#common-issues) section

---

**OHHH YEAHHH! Now you're ready to DIG IT!** 🎤💪🔥

