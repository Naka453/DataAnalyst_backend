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
    api_key: str = os.getenv("API_KEY", "").strip()

    def validate(self) -> None:
        missing: list[str] = []
        if not self.database_url:
            missing.append("DATABASE_URL")
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.api_key:
            missing.append("API_KEY")

        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


settings = Settings()