"""
Har bir update kelganda: foydalanuvchini bazadan olish/yaratish, ban tekshirish,
locale'ni context'ga qo'shish, last_active_at ni yangilash.
"""
from __future__ import annotations

import datetime as dt
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.i18n import t
from app.services.user_service import get_or_create_user, get_user


def _extract_referral_code(message: Message | None) -> str | None:
    if not message or not message.text:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) == 2 and parts[0] == "/start" and parts[1].startswith("ref_"):
        return parts[1][4:]
    return None


class UserContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]

        tg_user = None
        message: Message | None = None
        callback: CallbackQuery | None = None

        if isinstance(event, Message):
            message = event
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery):
            callback = event
            tg_user = event.from_user

        if tg_user is None:
            return await handler(event, data)

        referred_by_id: int | None = None
        ref_code = _extract_referral_code(message)
        if ref_code:
            from sqlalchemy import select

            from app.database.models import User as UserModel

            result = await session.execute(select(UserModel).where(UserModel.referral_code == ref_code))
            referrer = result.scalar_one_or_none()
            if referrer:
                referred_by_id = referrer.id

        user = await get_or_create_user(
            session,
            user_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            referred_by=referred_by_id,
        )

        user.last_active_at = dt.datetime.now(dt.timezone.utc)
        if tg_user.id in settings.admin_ids and not user.is_admin:
            user.is_admin = True
        await session.commit()

        if user.is_banned:
            text = t("banned_message", user.language_code)
            if message:
                await message.answer(text)
            elif callback:
                await callback.answer(text, show_alert=True)
            return None

        data["db_user"] = user
        data["locale"] = user.language_code
        data["is_admin"] = user.id in settings.admin_ids

        return await handler(event, data)
