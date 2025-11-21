# Changelog

All notable changes to the Houston Event Mania project.

---

## [2.1.0] - 2025-11-21 - WrestleMania Email Design 🏆

### 🎨 Major Feature: HTML Email Notifications

#### Added
- **WrestleMania-Themed HTML Email Template**
  - Championship color scheme: Gold (#FFD700), Red (#FF0000), Black (#000)
  - Animated pulsing header with gold gradient
  - Event cards styled like wrestling match cards
  - Category badges with red/gold styling
  - Responsive design (desktop and mobile)
  - Email client compatible (Gmail, Outlook, Apple Mail)
  - Plain text fallback for HTML-disabled clients

#### Technical Changes
- **Email Adapter** (`app/adapters/sms/email_sms.py`)
  - Now uses Jinja2 template engine for HTML rendering
  - Sends multipart emails (HTML + plain text)
  - Accepts structured data: `events`, `promo_text`, `scratchpad_text`
  - Enhanced logging for template rendering

- **SMS Port Interface** (`app/core/ports/sms_port.py`)
  - Added optional parameters for rich email content
  - Backward compatible with existing implementations

- **Service Layer**
  - `agentic_event_service.py`: Passes events/promo to email adapter
  - `event_service.py`: Passes events/promo to email adapter
  - Both services now enable HTML email rendering

#### Documentation
- **Created**: `docs/EMAIL_WRESTLEMANIA.md`
  - Complete design guide
  - Color palette and typography reference
  - Email client compatibility matrix
  - Customization instructions
  - Troubleshooting tips
  - Performance metrics

#### Testing
- **Created**: `test_email_template.py`
  - Validates template rendering with mock data
  - Generates `test_email_output.html` for browser preview
  - Outputs 18KB HTML for visual inspection

#### Configuration
- **Updated**: `.gitignore` to exclude test files
- **Updated**: `docs/README.md` with email design link

### 🎯 Impact
- ✅ **18KB HTML emails** with championship styling
- ✅ **100% backward compatible** with plain text fallback
- ✅ **Mobile responsive** design
- ✅ **Zero API changes** required for existing code

---

## [2.0.9] - 2025-11-16 - Deployment: Deep Research Mode Production Ready

### 🚀 Deployment Updates

#### Production Configuration
- **Updated**: Kubernetes CronJob to use `--deep-research` mode
- **Updated**: Helm chart templates for deep research
- **Disabled**: Reddit events agent (too many API calls)
- **Command**: `python -m app.workers.run_daily_job --deep-research`

#### macOS / Apple Silicon Compatibility
- **Added**: `--platform linux/amd64` flag to Docker build
- **Purpose**: Ensures images built on macOS (including Apple Silicon M1/M2/M3) are compatible with Linux Kubernetes clusters
- **Impact**: Prevents architecture mismatch errors in production

#### Deployment Files Updated
- `infra/k8s/cronjob.yaml` - Direct K8s manifest
- `charts/houston-event-mania/templates/cronjob.yaml` - Helm template
- `deploy.sh` - Deployment script with platform flag and docs
- `DEPLOYMENT_DEEP_RESEARCH.md` - Added macOS compatibility notes and troubleshooting

#### Documentation
- **Created**: `DEPLOYMENT_DEEP_RESEARCH.md` - Complete deployment guide
  - Configuration details
  - Required secrets
  - Deployment steps
  - Post-deployment verification
  - Troubleshooting guide
  - Expected performance metrics

### 🎯 Production Features

✅ Multi-agent event discovery  
✅ Deep research with entity extraction  
✅ AI-powered query generation (2-3/event)  
✅ Web search integration  
✅ Knowledge synthesis  
✅ Research-enriched wrestling promos  
✅ Rate limit management (50-75 calls)  
❌ Reddit events (disabled to save API quota)

### 📊 Expected Performance
- **Events**: ~25 per run
- **Entities**: 50-75 extracted
- **Queries**: 50-75 executed
- **Facts**: 300-600 discovered
- **SerpAPI calls**: 75-100 total
- **Runtime**: 2-3 minutes

---

## [2.0.8] - 2025-11-16 - Feature: Mock Test Suite Complete

### ✨ New Features

#### Comprehensive Mock Test Suite
- **Created**: Full test suite for deep research system without hitting API rate limits
- **Unit Tests**: 13 tests for domain models (`Entity`, `ResearchQuery`, `ResearchResult`, `EventResearch`)
- **Contract Tests**: 15 tests for port interfaces (extraction, generation, research, synthesis)
- **Test Scripts**: 
  - `test_research_simple.sh` - Quick verification (no API calls)
  - `test_research.sh` - Full suite including integration tests

### ✅ Test Results
```
✅ Unit Tests:     13/13 PASSED
✅ Contract Tests: 15/15 PASSED
📊 Total:          28/28 PASSED
```

### 📁 Files Created
- `tests/unit/domain/test_research_models.py` - Domain model tests
- `tests/contract/research/test_research_ports.py` - Port contract tests
- `tests/integration/research/test_deep_research_workflow.py` - Integration tests with mocked APIs
- `test_research_simple.sh` - Quick test runner
- `test_research.sh` - Full test suite runner
- `TESTS_COMPLETE.md` - Test documentation

### 🐛 Fixes Applied During Testing
- Fixed all entity types to match actual model (`artist`, `venue`, `organizer`, `topic`, `genre`)
- Fixed ResearchResult to use `ResearchQuery` object instead of string
- Fixed EventResearch to use `overall_confidence` instead of `confidence`
- Added `sources` field requirements to ResearchResult creation

---

## [2.0.7] - 2025-11-16 - Critical Fix: Rate Limit Management

### 🐛 Bug Fixes

#### SerpAPI Rate Limit Exceeded
- **Issue**: Generating 3-6 queries per event * 25 events = 75-150 API calls, exceeding 100/hour free tier limit
- **Solution**: Reduced query generation from 3-6 to **2-3 queries per event**
  - 25 events * 2-3 queries = 50-75 API calls (under 100 limit!)
  - Added explicit rate limit warning in prompts
  - Changed system prompt from "Generate 3-6" to "Generate ONLY 2-3"
  - Added ⚠️ RATE LIMIT CONSTRAINT banner in query generation prompt
- **Impact**: Will stay under SerpAPI free tier limits while still gathering quality research

#### Query Type Validation: 'awards'
- **Fixed**: Agent was generating `'awards'` query type which wasn't allowed
- **Solution**: Added `'awards'` to the Literal type list (10 total query types now)
- **Usage**: For Grammy wins, Tony awards, Emmy achievements, etc.

### 📝 Files Changed
- `app/core/domain/research_models.py` - Added 'awards' query type
- `app/adapters/agents/research/query_generation_agent.py` - Reduced to 2-3 queries, added rate limit warnings

---

## [2.0.6] - 2025-11-16 - Enhancement: Music-Aware Query Generation

### ✨ Enhancements

#### Music Event Query Specialization
- **Enhanced**: Query Generation Agent now detects music events and generates music-specific queries
- **Detection**: Automatically identifies music events via:
  - `'music'` category
  - Keywords in title: concert, tour, show, live music, orchestra, band, singer, rapper, dj
- **Music-Specific Queries**: For music events, prioritizes:
  - **Hit songs and chart performance** - "What are [Artist]'s biggest hit songs and their chart positions?"
  - **Albums and discography** - "What are [Artist]'s most critically acclaimed albums?"
  - **Current tours** - "What is [Artist]'s current tour schedule and recent performances?"
  - **Awards and accolades** - "What major music awards has [Artist] won?"
  - **Collaborations** - "What notable collaborations has [Artist] done?"
  - **Music style evolution** - "How has [Artist]'s sound evolved over their career?"
  - **Genre influence** - "What impact has [Artist] had on the [genre] scene?"
- **Requirement**: For music events, at least 2-3 queries must focus on hits, albums, tours, or awards
- **Examples**: System prompt now includes music-specific query examples (ASTN, Hot Mulligan, Wynton Marsalis, etc.)

### 📝 Files Changed
- `app/adapters/agents/research/query_generation_agent.py` - Added music event detection and specialized prompting

---

## [2.0.5] - 2025-11-16 - Enhancement: More Detail, Better Characters

### ✨ Enhancements

#### Promo Quality Improvements
- **Enhanced**: Template now pushes GPT-4o to use research MUCH more extensively
- **Character Authenticity**: Made Macho Man and Ultimate Warrior MORE in-character
  - **Macho Man**: Added "nothing means nothing!", "too hot to handle, too cold to hold!", gravelly voice, SNORT, mid-sentence intensity changes, excessive metaphors, getting sidetracked
  - **Ultimate Warrior**: Added DESTRUCITY, rocket fuel, crash the plane, no fear no pain, always believe, rapid breathing, veins throbbing, cosmic rage, speaking in bursts
- **Length**: Increased target from ~1000 words to 2000-3000 words total
  - Macho Man: 1500-2000 words (was ~800)
  - Ultimate Warrior: 800-1200 words (was ~400)
- **Detail**: Now requires SPECIFIC facts in every event mention
  - Must quote numbers, awards, achievements
  - Must mention venue capacity, founding dates
  - Must drop artist career highlights, albums, collaborations
  - Instructions: Don't say "this artist is great" - say "this artist who SOLD 5 MILLION ALBUMS and won 3 GRAMMY AWARDS"!
- **Coverage**: Increased from 18-20 events to 20-22 events minimum
- **Depth per event**:
  - High priority (7+): 5-12 sentences with research facts (was 3-8)
  - Mid priority: 3-6 sentences with key insights (was 2-4)
  - Low priority: 1-3 sentences with at least ONE research fact (was 1-2)

### 📝 Files Changed
- `app/adapters/llm/templates/summary.j2` - Extensive character and detail enhancements

---

## [2.0.4] - 2025-11-16 - Bug Fix: Historical Query Type

### 🐛 Bug Fixes

#### Query Type Validation Error: 'historical'
- **Fixed**: Agent was generating `'historical'` query type which wasn't allowed
- **Solution**: Added `'historical'` to the Literal type list (9 total query types now)
- **Files**: `research_models.py`, `query_generation_agent.py`

---

## [2.0.3] - 2025-11-16 - Critical Fix: Research Actually Used Now!

### 🐛 Bug Fixes

#### Deep Research STILL Not Being Used in Promos (v2.0.2 didn't fully work)
- **Fixed**: Research was passed to promo but appended AFTER template, so GPT-4o ignored it!
- **Root Cause**: Template is very prescriptive (123 lines), tells GPT-4o to use event list. Research was added as afterthought at the end.
- **Solution**: 
  - **Inject research INTO each event** in the template (not after!)
  - Each event now shows: `🔬 DEEP RESEARCH (X facts discovered)`, narrative, key insights
  - Added explicit instruction to GPT-4o to USE the research in instruction #10
  - Added banner at top: "DEEP RESEARCH MODE ENABLED!"
- **Impact**: Promos will now be MUCH longer, more detailed, with REAL FACTS!
  - Before: Generic mentions like "ASTN is hitting the stage"
  - After: "ASTN with tracks that hit BILLBOARD charts, collaborations with industry LEGENDS, bringing R&B fusion that critics RAVE about!"

### 📝 Files Changed (v2.0.3)
- `app/adapters/agents/promo_agent.py` - Inject research into event items BEFORE template render
- `app/adapters/llm/templates/summary.j2` - Display research narratives and insights in event list, add instruction #10

---

## [2.0.2] - 2025-11-16 - Partial Fix: Research Integration

### 🐛 Bug Fixes

#### Deep Research Not Being Used in Promos
- **Fixed**: Research results were gathered but never passed to the promo generator!
- **Issue**: 600+ facts collected but promos didn't use them
- **Solution**: 
  - Pass `research_results` from `state.events_researched` to promo generator
  - Enhanced promo agent to inject research insights into prompt (BUT appended after template - didn't work!)
- **Impact**: Partial fix - research was passed but not used (fixed in v2.0.3)

#### Truncated Thoughts in Scratchpad
- **Fixed**: Query text and event titles truncated to 40-50 characters in scratchpad
- **Issue**: `"Researching 'What are Mac Miller's most ico..."` (cut off)
- **Solution**: Removed `[:40]` and `[:50]` truncation from observation logging
- **Impact**: Full transparency in agent reasoning trace

### 📝 Files Changed (v2.0.2)
- `app/adapters/agents/planning_agent.py` - Pass research to promo, remove truncation
- `app/adapters/agents/promo_agent.py` - Accept research_results parameter
- `app/core/ports/agent_port.py` - Updated PromoAgentPort interface

---

## [2.0.1] - 2025-11-16 - Bug Fix: Query Types

### 🐛 Bug Fixes

#### Query Generation Validation Error
- **Fixed**: `ResearchQuery` validation errors for creative query types
- **Issue**: Agent was generating `'cultural_impact'` and `'venue_history'` query types that weren't in the allowed Literal
- **Solution**: Expanded allowed query types from 4 to 8:
  - Added: `cultural_impact`, `venue_history`, `genre_overview`, `collaboration`
  - Kept: `biographical`, `contextual`, `current`, `relational`
- **Files changed**: 
  - `app/core/domain/research_models.py`
  - `app/adapters/agents/research/query_generation_agent.py`

---

## [2.0.0] - 2025-11-16 - Deep Research Agent System

### 🎯 Major Features

#### Deep Research Agent System
- **NEW**: Complete deep research pipeline for intelligent event enrichment
- **NEW**: Entity Extraction Agent (GPT-4o-mini) - Extracts artists, venues, topics, genres
- **NEW**: Query Generation Agent (GPT-4o-mini) - Generates intelligent research queries
- **NEW**: Web Search Research Agent (SerpAPI) - Researches entities via Google
- **NEW**: Knowledge Synthesis Agent (GPT-4o) - Synthesizes findings into narratives
- **NEW**: Reddit Events Agent - Scrapes /r/houston weekly threads (opt-in)

#### Command Line Interface
- **NEW**: `--deep-research` - Full agentic system with research pipeline
- **NEW**: `--no-db` - Skip database, send email (local testing without PostgreSQL)
- **NEW**: `--dry-run` - Skip all side effects (pure testing mode)
- **NEW**: `--reddit` - Include Reddit events (opt-in, default: OFF)

### 🏗️ Architecture Changes

#### New Phase: RESEARCHING
- Added between REVIEWING and SYNTHESIZING phases
- Processes all verified events through research pipeline
- Runs in parallel with concurrency control (semaphore)

#### Enhanced Planning Agent
- Now supports optional research components via dependency injection
- Manages RESEARCHING phase with transparent logging
- Improved REACT loop with research observations

#### New Ports & Adapters
- `EntityExtractionPort` - Interface for entity extraction
- `QueryGenerationPort` - Interface for query generation  
- `ResearchAgentPort` - Interface for research agents
- `KnowledgeSynthesisPort` - Interface for synthesis
- Implementations in `app/adapters/agents/research/`

### 🔧 Technical Improvements

#### Service Layer
- `AgenticEventService` now supports `dry_run` and `no_db` flags
- Enhanced error reporting for SerpAPI rate limits
- Better logging for research pipeline failures

#### Configuration
- Added `newsapi_key` to Settings (for future News research)
- Improved error messages for missing API keys
- Better validation error handling

#### Bug Fixes
- Fixed `entity_type` → `type` attribute error in Entity model
- Fixed `venue_name` → `location` attribute error in Event model
- Improved query generation JSON parsing with fallback

### 📚 Documentation

#### New Documentation
- **[DEEP_RESEARCH_USAGE.md](./DEEP_RESEARCH_USAGE.md)** - Complete usage guide
- **[docs/README.md](./README.md)** - Comprehensive documentation index
- Updated main README with new features and architecture

#### Existing Docs Updated
- DEEP_RESEARCH_AGENT_DESIGN.md - Reflects current implementation
- Architecture diagrams updated with Query Generation Agent
- All command references updated with new flags

### 🎯 Event Discovery Changes

#### Default Sources (No Reddit)
- SerpAPI (Google Events): ~10-15 events
- Ticketmaster: ~10-15 events
- **Total: ~24 clean, curated events**

#### With Reddit (--reddit flag)
- Adds /r/houston weekly threads: ~100+ events
- **Warning**: Can be noisy and duplicative
- **Recommendation**: Use sparingly

### 📊 Performance & Costs

#### Typical Run (--deep-research --no-db)
- Events discovered: 24
- Entities extracted: 80-100
- Research queries generated: 60-80
- Facts gathered: 200-300 (depends on SerpAPI quota)
- Execution time: 2-3 minutes
- Cost: ~$0.10-0.20 (OpenAI + SerpAPI)

#### With Reddit (--reddit)
- Events discovered: 150-200
- Entities extracted: 400-600
- Research queries: 400-600
- Execution time: 8-15 minutes
- **Warning**: May hit SerpAPI rate limits

### ⚠️ Breaking Changes

#### Command Line
- Old: `python -m app.workers.run_daily_job` (still works)
- New recommended: `uv run python -m app.workers.run_daily_job --deep-research --no-db`

#### Dependency Injection
- `build_deep_research_service()` now accepts `include_reddit: bool = False`
- Planning Agent constructor expanded with optional research components

### 🔮 Future Enhancements

Planned but not yet implemented:
- [ ] News Research Agent (NewsAPI integration)
- [ ] Wikipedia Research Agent improvements
- [ ] MusicBrainz Research Agent for artist metadata
- [ ] Bing Search fallback when SerpAPI rate limited
- [ ] Research result caching to avoid duplicate searches
- [ ] Configurable research depth (light/medium/deep)

---

## [1.0.0] - 2024-11-15 - Agentic System Launch

### Major Features
- Multi-agent AI system with Planning Agent orchestration
- Search agents: SerpAPI, Ticketmaster, Meetup
- Review swarm: Relevance, Date Verification, Web Enrichment, Content Enrichment
- Promo generation with wrestling style (Macho Man / Ultimate Warrior)
- REACT pattern implementation with scratchpad logging
- Hexagonal architecture with ports & adapters
- FastAPI web interface with HTMX
- PostgreSQL storage with SQLAlchemy
- Email/SMS delivery via Gmail/Twilio
- Kubernetes deployment with Helm charts

---

## [0.9.0] - Initial Implementation

### Features
- Basic event scraping (Houston Chronicle, VisitHouston)
- OpenAI summarization
- SMS delivery via Twilio
- PostgreSQL storage
- Cron job scheduling

---

**Legend**:
- 🎯 Major Feature
- 🏗️ Architecture
- 🔧 Technical
- 📚 Documentation
- ⚠️ Breaking Change
- 🔮 Future

