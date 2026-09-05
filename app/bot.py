"""
Bot va Dispatcher obyektlarini yaratish, middlewarelarni ulash.
"""
from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.handlers import register_all_routers
from app.middlewares.db_session import DBSessionMiddleware
from app.middlewares.user_context import UserContextMiddleware

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware tartibi muhim: avval DB session, keyin user context
    dp.update.outer_middleware(DBSessionMiddleware())
    dp.update.outer_middleware(UserContextMiddleware())

    register_all_routers(dp)
    return dp


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
