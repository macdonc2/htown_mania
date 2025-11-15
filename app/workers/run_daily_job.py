import asyncio
import sys
from app.core.di import build_event_service, build_agentic_event_service


async def run_daily():
    """
    Run the daily event flow.
    
    Usage:
        python -m app.workers.run_daily_job           # Uses original service
        python -m app.workers.run_daily_job --agentic # Uses agentic service
    """
    # Check if --agentic flag is passed
    use_agentic = "--agentic" in sys.argv
    
    if use_agentic:
        print("🤖 Using AGENTIC multi-agent system\n")
        service = build_agentic_event_service()
    else:
        print("📋 Using ORIGINAL service\n")
        print("🚀 Starting daily event flow...")
        service = build_event_service()
        print(f"📱 SMS will be sent to: {service.sms_recipient}")
        print(f"🔇 Dev SMS Mute: {service.dev_sms_mute}")
    
    summary = await service.run_daily_event_flow()
    
    if not use_agentic:
        print('✅ Daily summary:\n', summary)
    
    print("\n🎉 Job completed!")


if __name__ == '__main__':
    asyncio.run(run_daily())
