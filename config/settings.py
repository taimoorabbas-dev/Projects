"""
config/settings.py
────────────────────────────────────────────────────────────
Centralized application configuration.
Loads environment variables and exposes them safely.
"""

from __future__ import annotations

from dataclasses import dataclass

import os

from dotenv import load_dotenv


# Load .env variables
load_dotenv()


@dataclass
class Settings:

    OPENAI_API_KEY: str | None

    NEWS_API_KEY: str | None

    OPENAI_MODEL: str = "gpt-4o-mini"

    CACHE_TTL: int = 300


def get_settings() -> Settings:

    return Settings(

        OPENAI_API_KEY=os.getenv(
            "OPENAI_API_KEY"
        ),

        NEWS_API_KEY=os.getenv(
            "NEWS_API_KEY"
        ),

    )