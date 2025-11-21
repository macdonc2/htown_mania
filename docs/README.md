# 📚 Houston Event Mania - Documentation

**Complete documentation for the agentic event discovery and deep research system.**

---

## 📖 Quick Navigation

### 🚀 Getting Started
- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment to Kubernetes

### 🤖 Core Systems
- **[Agentic System](AGENTIC_SYSTEM.md)** - Multi-agent orchestration (REACT pattern, parallel execution, review swarm)
- **[Deep Research](DEEP_RESEARCH.md)** - AI-powered event research (entity extraction, query generation, synthesis)
- **[SerpAPI Setup](SERPAPI.md)** - Google Events & web search integration

### 🎤 Features
- **[Wrestling TTS Guide](WRESTLING_TTS_GUIDE.md)** - Generate Macho Man & Ultimate Warrior voice promos

### 📝 Reference
- **[Changelog](CHANGELOG.md)** - Version history and release notes

---

## 📁 Documentation Structure

```
docs/
├── README.md                          ← You are here
├── QUICK_START.md                     ← Start here!
├── DEPLOYMENT_GUIDE.md                ← Production deployment
├── AGENTIC_SYSTEM.md                  ← Complete agentic guide
├── DEEP_RESEARCH.md                   ← Deep research guide
├── SERPAPI.md                         ← SerpAPI setup
├── WRESTLING_TTS_GUIDE.md             ← Voice generation
├── CHANGELOG.md                       ← Version history
├── architecture_diagram.png           ← System architecture
├── process_flow_diagram.png           ← Process flow
├── deep_research_architecture.png     ← Research architecture
└── deep_research_flow.png             ← Research flow
```

---

## 🎯 By Use Case

### I want to...

**...get started quickly**
→ [Quick Start Guide](QUICK_START.md)

**...deploy to production**
→ [Deployment Guide](DEPLOYMENT_GUIDE.md)

**...understand the agentic system**
→ [Agentic System](AGENTIC_SYSTEM.md)

**...enable deep research**
→ [Deep Research](DEEP_RESEARCH.md)

**...set up SerpAPI**
→ [SerpAPI Setup](SERPAPI.md)

**...generate wrestling voices**
→ [Wrestling TTS Guide](WRESTLING_TTS_GUIDE.md)

**...see what's new**
→ [Changelog](CHANGELOG.md)

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    HOUSTON EVENT MANIA                       │
│                  Multi-Agent System                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │   Planning Agent (REACT)      │
        │   - Orchestrates workflow     │
        │   - Maintains scratchpad      │
        │   - Confidence scoring        │
        └───────────────┬───────────────┘
                        │
    ┌───────────────────┴───────────────────┐
    │                                       │
┌───┴────┐                          ┌──────┴───────┐
│ SEARCH │                          │    REVIEW    │
│ AGENTS │                          │    SWARM     │
│────────│                          │──────────────│
│ Serp   │ ───(parallel)───→        │ Relevance    │
│ Ticket │                          │ Date         │
│        │                          │ WebSearch    │
└───┬────┘                          │ Content      │
    │                               └──────┬───────┘
    │                                      │
    └──────────────┬───────────────────────┘
                   │
           ┌───────┴────────┐
           │    RESEARCH    │ (optional --deep-research)
           │────────────────│
           │ Entity Extract │
           │ Query Generate │
           │ Web Search     │
           │ Synthesize     │
           └───────┬────────┘
                   │
           ┌───────┴────────┐
           │  SYNTHESIZE    │
           │────────────────│
           │ Promo Agent    │
           │ (GPT-4o)       │
           └───────┬────────┘
                   │
           ┌───────┴────────┐
           │    NOTIFY      │
           │────────────────│
           │ Email/SMS      │
           │ Database Save  │
           └────────────────┘
```

### Key Technologies

- **PydanticAI**: Agent orchestration framework
- **GPT-4o**: LLM for reasoning and generation
- **SerpAPI**: Google Events & web search
- **PostgreSQL**: Event storage
- **Kubernetes**: Production deployment
- **Twilio/SMTP**: Notifications

---

## 📊 Quick Stats

### Agentic System
- **Agents**: 7 (1 planning, 2 search, 4 review)
- **Pattern**: REACT (Thought → Action → Observation)
- **Observations**: 100-150 per run
- **Events**: 20-30 discovered, 15-25 verified
- **Confidence**: 0.75-0.85 average

### Deep Research
- **Research Agents**: 5 (extraction, generation, search, wikipedia, synthesis)
- **Entities**: 80-100 per run
- **Queries**: 2-3 per event (~50 total)
- **Facts**: 250+ discovered
- **API Calls**: ~75 (under 100/hour limit)

---

## 🔄 Recent Updates

**v2.0.9** - Deep Research System (Nov 2025)
- ✅ Entity extraction & query generation
- ✅ Music-aware research queries
- ✅ Rate limit management (2-3 queries/event)
- ✅ 28/28 tests passing
- ✅ Production deployed

See [Changelog](CHANGELOG.md) for full history.

---

## 🆘 Getting Help

### Common Issues

**No events found?**
→ Check [SerpAPI Setup](SERPAPI.md) and API keys

**Rate limits hit?**
→ See [Deep Research - Rate Limits](DEEP_RESEARCH.md#rate-limits)

**Deployment failing?**
→ Check [Deployment Guide - Troubleshooting](DEPLOYMENT_GUIDE.md#troubleshooting)

**Promo not enriched?**
→ Verify `--deep-research` flag and review [Deep Research Guide](DEEP_RESEARCH.md)

### Support Channels

- **Issues**: Open a GitHub issue
- **Docs**: You're reading them!
- **Logs**: Check Kubernetes logs or local output

---

## 🎤 About

**Houston Event Mania** is a State-of-the-Art (SOTA) agentic system that:
1. Discovers events from multiple sources
2. Validates them through a 4-agent review swarm
3. Optionally researches them with AI-powered queries
4. Generates wrestling-style promos (Macho Man + Ultimate Warrior)
5. Sends daily email/SMS notifications

**Built with**: PydanticAI, GPT-4o, SerpAPI, FastAPI, PostgreSQL

---

**OHHH YEAHHH!** Your docs are **ORGANIZED**, BROTHER! 🎤📚

**DIG IT!**
