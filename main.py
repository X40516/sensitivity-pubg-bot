"""
Botni ishga tushirish nuqtasi.

Polling: python main.py
Webhook (Railway/Render kabi platformalar uchun): .env da USE_WEBHOOK=true
"""
from __future__ import annotations

import asyncio
import logging

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.bot import create_bot, create_dispatcher, setup_logging
from app.config import settings
from app.database.db import init_models

logger = logging.getLogger(__name__)


async def _run_polling() -> None:
    bot = create_bot()
    dp = create_dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot polling rejimida ishga tushmoqda...")
    await dp.start_polling(bot)


async def _run_webhook() -> None:
    bot = create_bot()
    dp = create_dispatcher()

    webhook_url = settings.webhook_base_url.rstrip("/") + settings.webhook_path
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    logger.info("Webhook o'rnatildi: %s", webhook_url)

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.web_server_host, settings.web_server_port)
    await site.start()
    logger.info("Web server ishga tushdi: %s:%s", settings.web_server_host, settings.web_server_port)

    # Serverni doim ishlab turishi uchun
    await asyncio.Event().wait()


async def main() -> None:
    setup_logging()

    # Ishlab chiqishda tez boshlash uchun jadvallarni avtomatik yaratadi.
    # Productionda buning o'rniga Alembic migratsiyalaridan foydalaning:
    #   alembic upgrade head
    await init_models()

    if settings.use_webhook:
        await _run_webhook()
    else:
        await _run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
