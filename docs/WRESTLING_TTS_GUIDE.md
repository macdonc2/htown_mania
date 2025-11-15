# 🎤 Wrestling Promo TTS Feature - Implementation Guide

## 🎯 Project Goal

Add realistic text-to-speech audio generation to the daily Houston events email using cloned voices of:
- **Macho Man Randy Savage** - The main hype man
- **Ultimate Warrior** - The cosmic intensity
- **Mean Gene Okerlund** - The interviewer/narrator

**Status**: Personal fan project, non-commercial, for fun! 🎉

---

## 📋 Prerequisites Checklist

### 1. ElevenLabs Account Setup
- [ ] Sign up at https://elevenlabs.io (free tier: 10k chars/month)
- [ ] Note your API key from Settings
- [ ] Understand free tier limits (may need paid tier for daily use)

### 2. Voice Cloning Setup (User Must Do This First!)

For each wrestler, you need:
- [ ] Collect 3-10 minutes of clean audio samples
- [ ] Create voice clone in ElevenLabs Voice Lab
- [ ] Get the `voice_id` for each character

**Voice Sample Collection Guide** (see section below)

### 3. Environment Variables

Add to `.env`:
```bash
# ElevenLabs TTS
EVENTS_elevenlabs_api_key=your_api_key_here
EVENTS_macho_man_voice_id=voice_id_from_elevenlabs
EVENTS_warrior_voice_id=voice_id_from_elevenlabs
EVENTS_mean_gene_voice_id=voice_id_from_elevenlabs
EVENTS_enable_audio=1  # Set to 0 to disable audio generation
```

---

## 🎙️ Step-by-Step: Collecting Voice Samples

### Tools Needed

1. **yt-dlp** - Download YouTube audio
```bash
brew install yt-dlp  # macOS
# or
pip install yt-dlp
```

2. **Audacity** - Audio editing (free)
- Download from: https://www.audacityteam.org/

### Finding Good Audio Sources

**Macho Man Randy Savage:**
- Search YouTube: "Macho Man Randy Savage promo"
- Look for: Clean interviews, promos, no music
- Good examples: WWF interviews, Slim Jim commercials

**Ultimate Warrior:**
- Search YouTube: "Ultimate Warrior promo"
- Look for: Solo promos, backstage interviews
- Good examples: WWF backstage segments

**Mean Gene Okerlund:**
- Search YouTube: "Mean Gene Okerlund interview"
- Look for: Him speaking alone or introducing wrestlers
- Good examples: WrestleMania segments, backstage interviews

### Extracting Audio from YouTube

```bash
# Download audio only
yt-dlp -x --audio-format mp3 "YOUTUBE_URL_HERE"

# Example:
yt-dlp -x --audio-format mp3 "https://www.youtube.com/watch?v=example"
```

### Cleaning Audio in Audacity

1. **Import audio file** into Audacity
2. **Select segments** where ONLY the target person speaks (no music, no crowd)
3. **Remove noise:**
   - Select a few seconds of "silence" (background noise)
   - Effect → Noise Reduction → Get Noise Profile
   - Select all → Effect → Noise Reduction → OK
4. **Normalize:** Effect → Normalize
5. **Export as MP3:** File → Export → Export as MP3

**Goal**: 3-10 minutes of clean, isolated speech

### Upload to ElevenLabs

1. Go to https://elevenlabs.io/voice-lab
2. Click "Add Voice" → "Instant Voice Cloning"
3. Upload your cleaned audio files
4. Name the voice (e.g., "Macho Man")
5. Copy the `voice_id` (looks like: `21m00Tcm4TlvDq8ikWAM`)
6. Repeat for all 3 voices

---

## 🏗️ Technical Architecture

### New Components to Build

```
app/
├── adapters/
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── elevenlabs_tts.py       # NEW - ElevenLabs API adapter
│   │   └── audio_storage.py        # NEW - Azure Blob or local storage
├── core/
│   ├── ports/
│   │   └── tts_port.py              # NEW - TTS interface
│   └── domain/
│       └── dialogue.py              # NEW - Parse promo into dialogue
└── config/
    └── settings.py                  # UPDATE - Add TTS settings
```

### Data Flow

```
1. Generate text promo (existing OpenAI LLM)
   ↓
2. Parse promo into dialogue segments (NEW)
   - Identify who's speaking (Macho Man, Warrior, Mean Gene)
   - Split into chunks
   ↓
3. Generate audio for each segment (NEW - ElevenLabs)
   - Macho Man segments → macho_man_voice_id
   - Warrior segments → warrior_voice_id
   - Mean Gene segments → mean_gene_voice_id
   ↓
4. Combine audio files into single MP3 (NEW)
   - Use pydub or ffmpeg
   ↓
5. Store audio file (NEW)
   - Azure Blob Storage (public URL)
   - OR local storage + attach to email
   ↓
6. Add audio link/attachment to email (UPDATE)
```

---

## 💻 Implementation Steps

### Step 1: Update Dependencies

Add to `pyproject.toml` and `requirements.txt`:
```
elevenlabs==1.40.0  # ElevenLabs API client
pydub==0.25.1       # Audio manipulation
```

Also need `ffmpeg` system dependency:
```bash
brew install ffmpeg  # macOS
# or in Dockerfile
apt-get install -y ffmpeg
```

### Step 2: Create TTS Port

**File**: `app/core/ports/tts_port.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict

class TTSPort(ABC):
    @abstractmethod
    async def generate_audio(self, dialogue: List[Dict[str, str]]) -> bytes:
        """
        Generate audio from dialogue segments.
        
        Args:
            dialogue: List of {
                "speaker": "macho_man" | "warrior" | "mean_gene",
                "text": "The actual dialogue"
            }
        
        Returns:
            bytes: MP3 audio data
        """
        pass
```

### Step 3: Implement ElevenLabs Adapter

**File**: `app/adapters/tts/elevenlabs_tts.py`

```python
from elevenlabs import ElevenLabs
from pydub import AudioSegment
import io
from typing import List, Dict
from app.core.ports.tts_port import TTSPort
from app.config.settings import Settings

class ElevenLabsTTSAdapter(TTSPort):
    def __init__(self, api_key: str = None, voice_ids: Dict[str, str] = None):
        s = Settings()
        self.api_key = api_key or s.elevenlabs_api_key
        self.voice_ids = voice_ids or {
            "macho_man": s.macho_man_voice_id,
            "warrior": s.warrior_voice_id,
            "mean_gene": s.mean_gene_voice_id,
        }
        self.client = ElevenLabs(api_key=self.api_key)
    
    async def generate_audio(self, dialogue: List[Dict[str, str]]) -> bytes:
        """Generate audio from dialogue segments and combine them."""
        combined_audio = AudioSegment.empty()
        
        for segment in dialogue:
            speaker = segment["speaker"]
            text = segment["text"]
            voice_id = self.voice_ids.get(speaker)
            
            if not voice_id:
                print(f"Warning: No voice_id for {speaker}, skipping")
                continue
            
            # Generate audio for this segment
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_turbo_v2",  # Faster, cheaper
                # model_id="eleven_multilingual_v2",  # Higher quality
            )
            
            # Collect audio bytes
            audio_bytes = b"".join(audio_generator)
            
            # Load as AudioSegment
            segment_audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            
            # Add slight pause between speakers (500ms)
            pause = AudioSegment.silent(duration=500)
            
            # Combine
            combined_audio += segment_audio + pause
        
        # Export to MP3 bytes
        mp3_io = io.BytesIO()
        combined_audio.export(mp3_io, format="mp3", bitrate="128k")
        return mp3_io.getvalue()
```

### Step 4: Create Dialogue Parser

**File**: `app/core/domain/dialogue.py`

```python
from typing import List, Dict
import re

def parse_promo_to_dialogue(promo_text: str) -> List[Dict[str, str]]:
    """
    Parse the promo text into dialogue segments.
    
    Strategy:
    - Intro/opening is often Mean Gene or Macho Man
    - Text before "And NOW..." is Macho Man
    - Text after "And NOW..." is Ultimate Warrior
    - Look for explicit markers or patterns
    
    Returns:
        List of {"speaker": str, "text": str}
    """
    dialogue = []
    
    # Split on the Warrior transition
    warrior_marker = re.search(r"And NOW\.\.\.", promo_text, re.IGNORECASE)
    
    if warrior_marker:
        # Everything before is Macho Man
        macho_text = promo_text[:warrior_marker.start()].strip()
        # Everything from "And NOW..." onwards is Warrior
        warrior_text = promo_text[warrior_marker.start():].strip()
        
        # Optional: Add Mean Gene intro (can be enhanced)
        # For now, just split between Macho and Warrior
        
        if macho_text:
            dialogue.append({
                "speaker": "macho_man",
                "text": macho_text
            })
        
        if warrior_text:
            dialogue.append({
                "speaker": "warrior",
                "text": warrior_text
            })
    else:
        # Fallback: entire promo is Macho Man
        dialogue.append({
            "speaker": "macho_man",
            "text": promo_text
        })
    
    return dialogue
```

**Enhancement Ideas:**
- Add Mean Gene intro: "Ladies and gentlemen, I'm standing here with..."
- Split long segments into smaller chunks (ElevenLabs has char limits)
- Detect emotional cues and adjust voice settings

### Step 5: Update Settings

**File**: `app/config/settings.py`

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # ElevenLabs TTS
    elevenlabs_api_key: str = ""
    macho_man_voice_id: str = ""
    warrior_voice_id: str = ""
    mean_gene_voice_id: str = ""
    enable_audio: int = 0  # Feature flag
    
    # Audio storage
    azure_blob_connection_string: str = ""  # Optional
    azure_blob_container: str = "audio"     # Optional
```

### Step 6: Update Event Service

**File**: `app/core/services/event_service.py`

```python
from app.core.ports.tts_port import TTSPort
from app.core.domain.dialogue import parse_promo_to_dialogue
from datetime import datetime

class EventService:
    def __init__(
        self, 
        scraper: ScraperPort, 
        llm: LLMPort, 
        sms: SMSPort, 
        repository: EventRepositoryPort,
        tts: TTSPort = None,  # NEW - Optional TTS
        sms_recipient: str = None,
        dev_sms_mute: int = 0
    ):
        self.scraper = scraper
        self.llm = llm
        self.sms = sms
        self.repository = repository
        self.tts = tts  # NEW
        self.sms_recipient = sms_recipient
        self.dev_sms_mute = dev_sms_mute
    
    async def run_daily_event_flow(self) -> str:
        events = await self.scraper.scrape_events()
        if not events:
            return "No events found today."
        
        prioritized = prioritize_events(events)
        summary = await self.llm.summarize_events(prioritized)
        
        # NEW - Generate audio if enabled
        audio_url = None
        if self.tts:
            try:
                print("🎤 Generating audio promo...")
                dialogue = parse_promo_to_dialogue(summary)
                audio_bytes = await self.tts.generate_audio(dialogue)
                
                # Save audio (implement storage)
                audio_url = await self._save_audio(audio_bytes)
                print(f"✅ Audio generated: {audio_url}")
            except Exception as e:
                print(f"❌ Audio generation failed: {e}")
        
        await self.repository.save_events(prioritized)
        
        # Send notification with audio link
        notification_text = summary
        if audio_url:
            notification_text += f"\n\n🎤 Listen to the promo: {audio_url}"
        
        if not self.dev_sms_mute:
            await self.sms.send_sms(self.sms_recipient, notification_text)
        else:
            print("[DEV_SMS_MUTE=1] SMS would be sent to", self.sms_recipient)
            print(notification_text)
        
        return summary
    
    async def _save_audio(self, audio_bytes: bytes) -> str:
        """
        Save audio to storage and return URL.
        Options:
        1. Azure Blob Storage (public URL)
        2. Local file system + attach to email
        3. S3 or other cloud storage
        """
        # TODO: Implement based on your preference
        # For now, save locally
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"promo_{timestamp}.mp3"
        filepath = f"/tmp/{filename}"
        
        with open(filepath, "wb") as f:
            f.write(audio_bytes)
        
        return filepath  # Or return public URL if using cloud storage
```

### Step 7: Update Dependency Injection

**File**: `app/core/di.py`

```python
from app.adapters.tts.elevenlabs_tts import ElevenLabsTTSAdapter
from app.config.settings import Settings

def build_event_service() -> EventService:
    s = Settings()
    
    # ... existing adapters ...
    
    # NEW - TTS adapter (only if enabled)
    tts = None
    if s.enable_audio and s.elevenlabs_api_key:
        tts = ElevenLabsTTSAdapter()
    
    return EventService(
        scraper=scraper,
        llm=llm,
        sms=sms,
        repository=repo,
        tts=tts,  # NEW
        sms_recipient=s.sms_recipient,
        dev_sms_mute=s.dev_sms_mute
    )
```

### Step 8: Update Dockerfile

**File**: `infra/docker/Dockerfile`

Add after the existing `apt-get install`:
```dockerfile
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

---

## 🧪 Testing Plan

### 1. Local Testing (Before Deployment)

```bash
# Set environment variables
export EVENTS_elevenlabs_api_key="your_key"
export EVENTS_macho_man_voice_id="voice_id"
export EVENTS_warrior_voice_id="voice_id"
export EVENTS_mean_gene_voice_id="voice_id"
export EVENTS_enable_audio=1

# Run locally
python -m app.workers.run_daily_job
```

**Expected output:**
- Text promo generates
- "🎤 Generating audio promo..." message
- Audio file created
- "✅ Audio generated: /path/to/file.mp3"

### 2. Manual Audio Test

Create test script `test_tts.py`:
```python
import asyncio
from app.adapters.tts.elevenlabs_tts import ElevenLabsTTSAdapter

async def test_tts():
    tts = ElevenLabsTTSAdapter()
    
    dialogue = [
        {
            "speaker": "macho_man",
            "text": "OOOOOH YEAH! Mean Gene, let me tell you something, brother! The cream rises to the top!"
        },
        {
            "speaker": "warrior",
            "text": "And NOW... I feel the cosmic power flowing through the WARRIORS of Houston! OHHHHH!"
        }
    ]
    
    audio_bytes = await tts.generate_audio(dialogue)
    
    with open("test_promo.mp3", "wb") as f:
        f.write(audio_bytes)
    
    print("✅ Test audio generated: test_promo.mp3")

if __name__ == "__main__":
    asyncio.run(test_tts())
```

Run it:
```bash
python test_tts.py
# Listen to test_promo.mp3
```

### 3. Kubernetes Deployment Testing

After deploying to AKS:
```bash
# Update secrets
kubectl create secret generic houston-tts-secrets \
  --from-literal=EVENTS_elevenlabs_api_key="your_key" \
  --from-literal=EVENTS_macho_man_voice_id="voice_id" \
  --from-literal=EVENTS_warrior_voice_id="voice_id" \
  --from-literal=EVENTS_mean_gene_voice_id="voice_id" \
  -n houston-events

# Update deployment to use secrets
# (See deployment update section below)

# Test with manual job
kubectl create job --from=cronjob/houston-event-mania-daily test-audio-promo -n houston-events

# Check logs
kubectl logs -f -n houston-events -l job-name=test-audio-promo
```

---

## 📦 Kubernetes Updates

### Update Deployment to Include TTS Secrets

**File**: `infra/k8s/deployment.yaml`

Add to `env` section:
```yaml
- name: EVENTS_elevenlabs_api_key
  valueFrom:
    secretKeyRef:
      name: houston-tts-secrets
      key: EVENTS_elevenlabs_api_key
- name: EVENTS_macho_man_voice_id
  valueFrom:
    secretKeyRef:
      name: houston-tts-secrets
      key: EVENTS_macho_man_voice_id
- name: EVENTS_warrior_voice_id
  valueFrom:
    secretKeyRef:
      name: houston-tts-secrets
      key: EVENTS_warrior_voice_id
- name: EVENTS_mean_gene_voice_id
  valueFrom:
    secretKeyRef:
      name: houston-tts-secrets
      key: EVENTS_mean_gene_voice_id
- name: EVENTS_enable_audio
  value: "1"
```

Apply:
```bash
kubectl apply -f infra/k8s/deployment.yaml
```

---

## 💰 Cost Estimates

### ElevenLabs Pricing

**Free Tier:**
- 10,000 characters/month
- Instant voice cloning (unlimited)

**Starter Plan ($5/month):**
- 30,000 characters/month
- ~10-15 daily promos (assuming 2,000-3,000 chars each)

**Creator Plan ($22/month):**
- 100,000 characters/month
- ~30+ daily promos
- Professional voice cloning

**Typical Daily Promo:**
- Length: 2,000-4,000 characters
- Cost on Starter: ~$0.33-$0.67 per promo
- **Monthly**: ~$10-20 for daily promos

**Recommendation**: Start with free tier for testing, upgrade to Starter ($5/mo) for daily use.

---

## 🎯 Enhancement Ideas

### Phase 1 (MVP - described above)
- ✅ Generate audio from text promo
- ✅ Split between Macho Man and Warrior
- ✅ Combine into single MP3
- ✅ Attach to email

### Phase 2
- Add Mean Gene intro/outro
- Better dialogue parsing (detect emotional beats)
- Add background music/sound effects
- Adjust voice settings per emotion (excited, intense, etc.)

### Phase 3
- Store audio in Azure Blob with public URLs
- Create web player on frontend
- Archive of past promos
- User can trigger regeneration with different temperature

### Phase 4
- Multiple voice styles per character
- Interactive web UI to customize promo
- Social media sharing (private only!)

---

## 🐛 Troubleshooting

### "API key invalid"
- Check `.env` has correct `EVENTS_elevenlabs_api_key`
- Verify key in ElevenLabs dashboard

### "Voice ID not found"
- Verify voice IDs are correct in `.env`
- Check voice is properly cloned in ElevenLabs Voice Lab
- Voice IDs look like: `21m00Tcm4TlvDq8ikWAM`

### "Audio quality is poor"
- Use higher quality model: `eleven_multilingual_v2`
- Provide better voice samples (cleaner audio)
- Try Professional Voice Cloning (needs 30+ min audio)

### "Audio is too long/expensive"
- Reduce promo length (fewer events)
- Split into multiple shorter promos
- Use `eleven_turbo_v2` model (faster, cheaper)

### "ffmpeg not found"
- Install ffmpeg: `brew install ffmpeg` (macOS)
- Add to Dockerfile for Kubernetes

---

## ✅ Checklist for Cursor Agent

**Before starting:**
- [ ] User has ElevenLabs account
- [ ] User has collected voice samples
- [ ] User has cloned 3 voices in ElevenLabs
- [ ] User has voice IDs ready
- [ ] User has added env vars to `.env`

**Implementation:**
- [ ] Add dependencies (`elevenlabs`, `pydub`)
- [ ] Install `ffmpeg` system dependency
- [ ] Create TTS port interface
- [ ] Implement ElevenLabs adapter
- [ ] Create dialogue parser
- [ ] Update settings with TTS config
- [ ] Update event service to generate audio
- [ ] Update DI to wire TTS adapter
- [ ] Update Dockerfile with ffmpeg
- [ ] Test locally with sample dialogue
- [ ] Update Kubernetes secrets/deployment
- [ ] Deploy and test in AKS
- [ ] Verify daily email includes audio

**Post-deployment:**
- [ ] Monitor ElevenLabs usage/costs
- [ ] Listen to generated audio quality
- [ ] Iterate on dialogue parsing
- [ ] Add error handling/fallbacks

---

## 🎤 Final Notes

This is an AWESOME feature that will make your daily emails LEGENDARY! 

**Remember:**
- This is a personal fan project
- Keep it private
- Be respectful of the wrestlers' legacies
- Have fun with it!

**THE CREAM WILL RISE TO THE TOP, AND IT WILL SOUND AMAZING! DIG IT!** 💪🔥

---

**Questions?** Check the ElevenLabs docs: https://elevenlabs.io/docs

