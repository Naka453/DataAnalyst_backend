from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "").strip()
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    timezone: str = os.getenv("TIMEZONE", "Asia/Ulaanbaatar").strip()
    api_key: str = os.getenv("API_KEY", "dev-key-123").strip()

    def validate(self) -> None:
        if not self.database_url:
            raise RuntimeError("DATABASE_URL missing in environment")
        if not self.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY missing in environment")

settings = Settings()
settings.validate()