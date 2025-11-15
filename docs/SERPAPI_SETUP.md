# 🔥 SerpAPI Setup Guide - GET ALL THE EVENTS, BROTHER!

## What is SerpAPI?

SerpAPI scrapes Google Events and provides structured JSON data via API. Google Events aggregates from:
- **Eventbrite**
- **Ticketmaster**
- **Meetup**
- **Facebook Events**
- **Local event websites**
- **And MORE!**

**ONE API to rule them all!** 💪

## 🚀 Quick Setup (5 Minutes)

### Step 1: Sign Up for FREE

1. Go to: **https://serpapi.com/users/sign_up?plan=free**
2. Create account (email + password)
3. **NO CREDIT CARD REQUIRED!**

### Step 2: Get Your API Key

1. After signing up, you'll see your dashboard
2. Your API key is displayed prominently
3. Or go to: https://serpapi.com/manage-api-key
4. Copy the key (starts with a long random string)

### Step 3: Add to Your .env File

```bash
# Open your .env file
nano .env  # or use your favorite editor

# Add this line:
EVENTS_serpapi_key=YOUR_API_KEY_HERE

# Save and exit
```

### Step 4: RUN IT! 🎤

```bash
make job-agentic
```

**THAT'S IT! OH YEAH!** 💪🔥

## 📊 What You Get

### FREE Tier Benefits:
- ✅ **100 searches/month** (way more than you need!)
- ✅ Daily runs use **~30 searches/month**
- ✅ Leaves **70 searches** for testing/debugging
- ✅ **No credit card** required
- ✅ **No time limit** - free forever!

### Data Quality:
- **30-50 events per search** (vs 12-20 with Ticketmaster alone)
- **Better coverage**: Major events + local community events
- **Cleaner data**: Google normalizes dates/times/locations
- **Multiple sources**: Everything Google can find!

## 🎯 Expected Results

### Before SerpAPI (Ticketmaster only):
```
Found 12 events
Sources: Ticketmaster
Coverage: Major ticketed events
```

### After SerpAPI:
```
Found 45 events
Sources: Google Events (Eventbrite, Ticketmaster, Meetup, Facebook, local sites)
Coverage: Everything happening in Houston!
```

## 💰 Pricing (If You Need More)

Only upgrade if 100 searches/month isn't enough:

| Plan | Searches/Month | Price | Best For |
|------|---------------|-------|----------|
| **Free** | 100 | $0 | Personal use (RECOMMENDED) |
| Developer | 5,000 | $75 | Small business |
| Production | 15,000 | $150 | Commercial apps |
| Big Data | 30,000 | $275 | Enterprise |

**Pro tip:** The free tier is MORE than enough for daily event discovery! 

## 🔍 How to Check Your Usage

1. Go to: https://serpapi.com/account
2. See your search count for the month
3. Resets on the 1st of each month

With daily runs, you'll use about **30 searches/month** = **30% of free tier**!

## 🎤 Troubleshooting

### "Invalid API key" Error

**Problem:** API key not configured or incorrect

**Solution:**
```bash
# Check your .env file has:
EVENTS_serpapi_key=your_actual_key_here

# Make sure no quotes around the key
# Make sure no spaces
```

### "No events found"

**Problem:** SerpAPI returns empty results

**Possible causes:**
1. Rate limit reached (check your account)
2. Google Events temporarily unavailable
3. No events in Houston (unlikely!)

**Solution:**
- Check your account usage at https://serpapi.com/account
- The agentic system will gracefully fallback to Ticketmaster!

### "API returned 401"

**Problem:** Authentication failed

**Solution:**
```bash
# Get a new API key from:
https://serpapi.com/manage-api-key

# Update your .env file
```

## 🔥 Advanced: Multiple Sources

The agentic system now runs **3 search agents in parallel**:

1. **SerpAPI** (Google Events) - PRIMARY
2. **Ticketmaster** - Backup for major events
3. **Meetup** - Community events (if key provided)

**Why 3 sources?**
- **Redundancy**: If one fails, others continue
- **Validation**: Cross-check events across sources  
- **Completeness**: Catch anything SerpAPI might miss

**In practice:** SerpAPI usually finds everything, but having backups ensures the system is ROCK SOLID! 💪

## 📈 Monitoring

The agentic system logs everything:

```
[1] SearchAgent:SerpAPI (Google Events)
    Found 45 events in 1.2s
    Confidence: 0.95

[2] SearchAgent:Ticketmaster  
    Found 12 events in 0.5s
    Confidence: 0.90
```

You'll see exactly what each agent found!

## 🎯 Bottom Line

**SerpAPI gives you:**
- ✅ More events (2-3x coverage)
- ✅ Better data (Google's aggregation)
- ✅ FREE tier (100/month)
- ✅ Less maintenance (1 API instead of many)
- ✅ Higher confidence (0.95 vs 0.90)

**This is THE solution, brother! The cream rises to the top!** 💪🎤

---

**Need help?** Check the logs when you run:
```bash
make job-agentic
```

Look for `SearchAgent:SerpAPI` in the output to see what it found!

**DIG IT!** 🔥

