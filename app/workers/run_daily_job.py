import asyncio
from app.core.di import build_event_service

async def run_daily():
    print("🚀 Starting daily event flow...")
    service = build_event_service()
    print(f"📱 SMS will be sent to: {service.sms_recipient}")
    print(f"🔇 Dev SMS Mute: {service.dev_sms_mute}")
    summary = await service.run_daily_event_flow()
    print('✅ Daily summary:\n', summary)
    print("\n🎉 Job completed!")

if __name__ == '__main__':
    asyncio.run(run_daily())
