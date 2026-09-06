"""
Til (i18n) tizimi. Tarjima topilmasa, o'zbek tiliga fallback qiladi.
"""
from __future__ import annotations

import json
from pathlib import Path

from app.config import settings

_LOCALES_DIR = Path(__file__).parent.parent / "locales"
SUPPORTED_LOCALES = ("uz", "ru", "en")
FALLBACK_LOCALE = "uz"

_cache: dict[str, dict[str, str]] = {}


def _load(locale: str) -> dict[str, str]:
    if locale not in _cache:
        path = _LOCALES_DIR / f"{locale}.json"
        if not path.exists():
            # Cheksiz rekursiyaning oldini olish: agar fallback faylning o'zi
            # ham topilmasa (masalan noto'g'ri deploy), bo'sh lug'at qaytaramiz.
            if locale == FALLBACK_LOCALE:
                _cache[locale] = {}
                return _cache[locale]
            return _load(FALLBACK_LOCALE)
        with open(path, encoding="utf-8") as f:
            _cache[locale] = json.load(f)
    return _cache[locale]


def t(key: str, locale: str | None = None, **kwargs) -> str:
    """Kalit bo'yicha tarjima qaytaradi, formatlash argumentlari bilan."""
    locale = locale or settings.default_locale
    if locale not in SUPPORTED_LOCALES:
        locale = FALLBACK_LOCALE

    translations = _load(locale)
    text = translations.get(key)

    if text is None:
        fallback = _load(FALLBACK_LOCALE)
        text = fallback.get(key, key)  # topilmasa, kalitning o'zini qaytaradi (debug uchun)

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def locale_display_name(locale: str) -> str:
    return {
        "uz": "🇺🇿 O'zbek",
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English",
    }.get(locale, locale)
