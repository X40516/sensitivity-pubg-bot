"""
👥 Do'st taklif qilish va ⭐ Premium bo'limlari.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.keyboards.callback_data import MenuCB
from app.keyboards.main_menu import simple_back_home_keyboard
from app.services.i18n import t
from app.services.user_service import get_referral_stats, is_premium

router = Router(name="referral_premium")


@router.callback_query(MenuCB.filter(F.action == "referral"))
async def show_referral(callback: CallbackQuery, locale: str, session: AsyncSession, db_user: User) -> None:
    count, bonus, code = await get_referral_stats(session, db_user.id)
    bot_username = (await callback.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=ref_{code}"
    text = f"{t('referral_title', locale)}\n\n{t('referral_stats', locale, count=count, bonus=bonus, link=link)}"
    await callback.message.edit_text(text, reply_markup=simple_back_home_keyboard(locale))
    await callback.answer()


@router.callback_query(MenuCB.filter(F.action == "premium"))
async def show_premium(callback: CallbackQuery, locale: str, session: AsyncSession, db_user: User) -> None:
    already_premium = await is_premium(session, db_user.id)
    lines = [t("premium_title", locale), ""]
    if already_premium:
        lines.append(t("premium_already", locale))
    else:
        lines += [
            t("premium_free_title", locale),
            t("premium_free_list", locale),
            "",
            t("premium_pro_title", locale),
            t("premium_pro_list", locale),
            "",
            t("premium_not_configured", locale),
        ]
    await callback.message.edit_text("\n".join(lines), reply_markup=simple_back_home_keyboard(locale))
    await callback.answer()
