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

    # MUHIM: dp.update.outer_middleware() ga o'rnatilsa, "event" argumenti
    # Message/CallbackQuery emas, balki xom Update obyekti bo'ladi — shu sabab
    # middleware ichidagi isinstance(event, Message) tekshiruvi hech qachon
    # to'g'ri kelmay, foydalanuvchi (db_user/locale) hech qachon o'rnatilmas edi.
    # To'g'ri yechim: middlewarelarni message va callback_query observerlariga
    # alohida-alohida ulash kerak. Middleware tartibi muhim: avval DB session,
    # keyin user context.
    db_session_mw = DBSessionMiddleware()
    user_context_mw = UserContextMiddleware()

    dp.message.outer_middleware(db_session_mw)
    dp.message.outer_middleware(user_context_mw)

    dp.callback_query.outer_middleware(db_session_mw)
    dp.callback_query.outer_middleware(user_context_mw)

    register_all_routers(dp)
    return dp


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
