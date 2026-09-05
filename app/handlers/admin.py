"""
⚙️ Admin panel — statistika, foydalanuvchilarni boshqarish, broadcast.
Faqat ADMIN_IDS ro'yxatidagi Telegram ID'lar uchun ishlaydi.
"""
from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.states import AdminBroadcast, AdminUserAction
from app.keyboards.callback_data import AdminCB, ConfirmCB, MenuCB
from app.services.admin_stats_service import get_statistics
from app.services.i18n import t
from app.services.user_service import ban_user, get_all_active_user_ids, unban_user

router = Router(name="admin")


def admin_panel_keyboard(locale: str):
    builder = InlineKeyboardBuilder()
    items = [
        ("admin_statistics", "stats"),
        ("admin_pro_players", "pro_players"),
        ("admin_ban_user", "ban"),
        ("admin_unban_user", "unban"),
        ("admin_broadcast", "broadcast"),
    ]
    for text_key, action in items:
        builder.button(text=t(text_key, locale), callback_data=AdminCB(action=action))
    builder.adjust(2)
    builder.row(*_home_row(locale))
    return builder.as_markup()


def _home_row(locale: str):
    from aiogram.types import InlineKeyboardButton

    return [InlineKeyboardButton(text=t("btn_home", locale), callback_data=MenuCB(action="home").pack())]


@router.message(Command("admin"))
async def open_admin_panel(message: Message, locale: str, is_admin: bool) -> None:
    if not is_admin:
        await message.answer(t("admin_not_allowed", locale))
        return
    await message.answer(t("admin_panel_title", locale), reply_markup=admin_panel_keyboard(locale))


@router.callback_query(AdminCB.filter(F.action == "stats"))
async def show_stats(callback: CallbackQuery, locale: str, is_admin: bool, session: AsyncSession) -> None:
    if not is_admin:
        await callback.answer(t("admin_not_allowed", locale), show_alert=True)
        return
    stats = await get_statistics(session)
    text = t("admin_stats_text", locale, **stats)
    await callback.message.edit_text(text, reply_markup=admin_panel_keyboard(locale))
    await callback.answer()


@router.callback_query(AdminCB.filter(F.action == "ban"))
async def ask_ban_user_id(callback: CallbackQuery, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        await callback.answer(t("admin_not_allowed", locale), show_alert=True)
        return
    await state.set_state(AdminUserAction.waiting_user_id_ban)
    await callback.message.edit_text(t("admin_ask_user_id", locale))
    await callback.answer()


@router.message(AdminUserAction.waiting_user_id_ban)
async def do_ban_user(message: Message, state: FSMContext, locale: str, is_admin: bool, session: AsyncSession) -> None:
    if not is_admin:
        return
    await state.clear()
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer(t("admin_user_not_found", locale))
        return
    ok = await ban_user(session, target_id)
    if ok:
        await message.answer(t("admin_user_banned", locale, user_id=target_id))
    else:
        await message.answer(t("admin_user_not_found", locale))
    await message.answer(t("admin_panel_title", locale), reply_markup=admin_panel_keyboard(locale))


@router.callback_query(AdminCB.filter(F.action == "unban"))
async def ask_unban_user_id(callback: CallbackQuery, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        await callback.answer(t("admin_not_allowed", locale), show_alert=True)
        return
    await state.set_state(AdminUserAction.waiting_user_id_unban)
    await callback.message.edit_text(t("admin_ask_user_id", locale))
    await callback.answer()


@router.message(AdminUserAction.waiting_user_id_unban)
async def do_unban_user(
    message: Message, state: FSMContext, locale: str, is_admin: bool, session: AsyncSession
) -> None:
    if not is_admin:
        return
    await state.clear()
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer(t("admin_user_not_found", locale))
        return
    ok = await unban_user(session, target_id)
    if ok:
        await message.answer(t("admin_user_unbanned", locale, user_id=target_id))
    else:
        await message.answer(t("admin_user_not_found", locale))
    await message.answer(t("admin_panel_title", locale), reply_markup=admin_panel_keyboard(locale))


@router.callback_query(AdminCB.filter(F.action == "broadcast"))
async def ask_broadcast_text(callback: CallbackQuery, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        await callback.answer(t("admin_not_allowed", locale), show_alert=True)
        return
    await state.set_state(AdminBroadcast.waiting_text)
    await callback.message.edit_text(t("admin_ask_broadcast_text", locale))
    await callback.answer()


@router.message(AdminBroadcast.waiting_text)
async def confirm_broadcast(message: Message, state: FSMContext, locale: str, is_admin: bool, session: AsyncSession) -> None:
    if not is_admin:
        return
    await state.update_data(broadcast_text=message.text)
    user_ids = await get_all_active_user_ids(session)
    await state.update_data(broadcast_user_ids=user_ids)
    await state.set_state(AdminBroadcast.waiting_confirm)

    builder = InlineKeyboardBuilder()
    builder.button(
        text=t("btn_confirm_yes", locale), callback_data=ConfirmCB(action="yes", context="broadcast")
    )
    builder.button(
        text=t("btn_confirm_no", locale), callback_data=ConfirmCB(action="no", context="broadcast")
    )
    builder.adjust(2)
    await message.answer(t("admin_broadcast_confirm", locale, count=len(user_ids)), reply_markup=builder.as_markup())


@router.callback_query(AdminBroadcast.waiting_confirm, ConfirmCB.filter(F.context == "broadcast"))
async def run_broadcast(
    callback: CallbackQuery, callback_data: ConfirmCB, state: FSMContext, locale: str, is_admin: bool
) -> None:
    if not is_admin:
        await callback.answer(t("admin_not_allowed", locale), show_alert=True)
        return

    data = await state.get_data()
    await state.clear()

    if callback_data.action != "yes":
        await callback.message.edit_text(t("cancelled", locale), reply_markup=admin_panel_keyboard(locale))
        await callback.answer()
        return

    text = data.get("broadcast_text", "")
    user_ids: list[int] = data.get("broadcast_user_ids", [])
    await callback.message.edit_text(t("admin_broadcast_started", locale))

    sent, failed = 0, 0
    for user_id in user_ids:
        try:
            await callback.bot.send_message(user_id, text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # oddiy rate limiting

    await callback.message.answer(t("admin_broadcast_done", locale, sent=sent, failed=failed))
    await callback.message.answer(t("admin_panel_title", locale), reply_markup=admin_panel_keyboard(locale))
    await callback.answer()
