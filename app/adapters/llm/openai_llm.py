from typing import List
from app.core.domain.models import Event
from app.core.ports.llm_port import LLMPort
from app.config.settings import Settings
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from openai import AsyncOpenAI
import os


class OpenAILLMAdapter(LLMPort):
    def __init__(self, api_key: str = None, model: str = None, temperature: float = None):
        s = Settings()
        self.api_key = api_key or s.openai_api_key
        self.model = model or s.openai_model
        self.temperature = temperature if temperature is not None else s.openai_temperature
        self.client = AsyncOpenAI(api_key=self.api_key)
        tmpl_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(tmpl_dir))

    async def summarize_events(self, events: List[Event]) -> str:
        template = self.env.get_template("summary.j2")
        # Pass full date to make it crystal clear what "today" is
        today = datetime.now()
        date_str = today.strftime("%A, %B %d, %Y")  # e.g., "Sunday, November 10, 2025"
        rendered = template.render(events=events, date_str=date_str)
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": rendered}],
            temperature=self.temperature
        )
        return resp.choices[0].message.content
