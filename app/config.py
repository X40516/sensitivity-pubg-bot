"""
Konfiguratsiya moduli.
Barcha maxfiy ma'lumotlar (token, DB URL, admin ID'lar) faqat .env orqali o'qiladi.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(
            f"Muhim environment variable topilmadi: {name}. "
            f".env faylini tekshiring (.env.example asosida yarating)."
        )
    return value or ""


def _parse_admin_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            continue
    return ids


@dataclass(frozen=True)
class Settings:
    bot_token: str = field(default_factory=lambda: _get_env("BOT_TOKEN", required=True))
    database_url: str = field(default_factory=lambda: _get_env("DATABASE_URL", required=True))
    admin_ids: list[int] = field(default_factory=lambda: _parse_admin_ids(_get_env("ADMIN_IDS", "")))
    admin_contact_url: str = field(default_factory=lambda: _get_env("ADMIN_CONTACT_URL", "https://t.me/X40516"))
    ai_api_key: str = field(default_factory=lambda: _get_env("AI_API_KEY", ""))
    use_webhook: bool = field(default_factory=lambda: _get_env("USE_WEBHOOK", "false").lower() == "true")
    webhook_base_url: str = field(default_factory=lambda: _get_env("WEBHOOK_BASE_URL", ""))
    webhook_path: str = field(default_factory=lambda: _get_env("WEBHOOK_PATH", "/webhook"))
    web_server_host: str = field(default_factory=lambda: _get_env("WEB_SERVER_HOST", "0.0.0.0"))
    web_server_port: int = field(default_factory=lambda: int(_get_env("WEB_SERVER_PORT", "8080")))
    default_locale: str = field(default_factory=lambda: _get_env("DEFAULT_LOCALE", "uz"))
    log_level: str = field(default_factory=lambda: _get_env("LOG_LEVEL", "INFO"))
    referral_bonus_points: int = field(default_factory=lambda: int(_get_env("REFERRAL_BONUS_POINTS", "10")))
    free_saved_profiles_limit: int = field(default_factory=lambda: int(_get_env("FREE_SAVED_PROFILES_LIMIT", "3")))
    premium_saved_profiles_limit: int = field(default_factory=lambda: int(_get_env("PREMIUM_SAVED_PROFILES_LIMIT", "50")))


settings = Settings()
