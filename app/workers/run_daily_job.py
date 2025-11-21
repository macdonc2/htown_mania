import asyncio
import sys
from app.core.di import build_event_service, build_agentic_event_service
from app.core.di_deep_research import build_deep_research_service


async def run_daily():
    """
    Run the daily event flow.
    
    Usage:
        python -m app.workers.run_daily_job                                    # Uses original service
        python -m app.workers.run_daily_job --agentic                          # Uses agentic service
        python -m app.workers.run_daily_job --deep-research                    # Uses agentic + deep research
        python -m app.workers.run_daily_job --deep-research --dry-run          # Test without DB/SMS
        python -m app.workers.run_daily_job --deep-research --no-db            # Skip DB, send email (no PostgreSQL needed!)
        python -m app.workers.run_daily_job --deep-research --no-db --reddit   # Include Reddit events (opt-in)
    """
    # Check flags
    use_agentic = "--agentic" in sys.argv
    use_deep_research = "--deep-research" in sys.argv
    dry_run = "--dry-run" in sys.argv
    no_db = "--no-db" in sys.argv
    include_reddit = "--reddit" in sys.argv
    
    if use_deep_research:
        print("🔬 Using DEEP RESEARCH multi-agent system (Agentic + Research)\n")
        if dry_run:
            print("🧪 DRY RUN MODE: Will NOT save to database or send SMS\n")
        elif no_db:
            print("🗄️  NO-DB MODE: Will send email but skip database (no PostgreSQL needed!)\n")
        if include_reddit:
            print("🔴 Including Reddit /r/houston events\n")
        service = build_deep_research_service(include_reddit=include_reddit)
    elif use_agentic:
        print("🤖 Using AGENTIC multi-agent system\n")
        if dry_run:
            print("🧪 DRY RUN MODE: Will NOT save to database or send SMS\n")
        elif no_db:
            print("🗄️  NO-DB MODE: Will send email but skip database (no PostgreSQL needed!)\n")
        service = build_agentic_event_service()
    else:
        print("📋 Using ORIGINAL service\n")
        if dry_run:
            print("🧪 DRY RUN MODE: Will NOT save to database or send SMS\n")
        elif no_db:
            print("🗄️  NO-DB MODE: Will send email but skip database (no PostgreSQL needed!)\n")
        print("🚀 Starting daily event flow...")
        service = build_event_service()
        print(f"📱 SMS will be sent to: {service.sms_recipient}")
        print(f"🔇 Dev SMS Mute: {service.dev_sms_mute}")
    
    # Set flags on service
    if dry_run:
        service.dry_run = True
    if no_db:
        service.no_db = True
    
    summary = await service.run_daily_event_flow()
    
    if not use_agentic and not use_deep_research:
        print('✅ Daily summary:\n', summary)
    
    print("\n🎉 Job completed!")


if __name__ == '__main__':
    asyncio.run(run_daily())
