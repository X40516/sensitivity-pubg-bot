"""
Admin: Pro Player qo'shish/o'chirish. 21-band talabiga ko'ra, hech qanday
uydirma ma'lumot avtomatik yaratilmaydi — admin har bir maydonni qo'lda kiritadi.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.admin import admin_panel_keyboard
from app.handlers.states import AdminProPlayerFlow
from app.keyboards.callback_data import AdminCB, AdminProPlayerCB
from app.services.i18n import t
from app.services.pro_player_service import add_player, count_players, delete_player, list_players

router = Router(name="admin_pro_players")


def _pro_admin_menu_keyboard(locale: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=t("admin_add_pro_player", locale), callback_data=AdminProPlayerCB(action="add"))
    builder.button(text=t("admin_delete_pro_player", locale), callback_data=AdminProPlayerCB(action="delete"))
    builder.adjust(1)
    from app.keyboards.callback_data import MenuCB
    from aiogram.types import InlineKeyboardButton

    builder.row(InlineKeyboardButton(text=t("btn_home", locale), callback_data=MenuCB(action="home").pack()))
    return builder.as_markup()


@router.callback_query(AdminCB.filter(F.action == "pro_players"))
async def show_pro_admin_menu(callback: CallbackQuery, locale: str, is_admin: bool, session: AsyncSession) -> None:
    if not is_admin:
        await callback.answer(t("admin_not_allowed", locale), show_alert=True)
        return
    total = await count_players(session)
    await callback.message.edit_text(
        f"{t('admin_pro_players', locale)} ({total})", reply_markup=_pro_admin_menu_keyboard(locale)
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# ADD PRO PLAYER FLOW
# ---------------------------------------------------------------------------


@router.callback_query(AdminProPlayerCB.filter(F.action == "add"))
async def start_add_player(callback: CallbackQuery, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        await callback.answer(t("admin_not_allowed", locale), show_alert=True)
        return
    await state.set_state(AdminProPlayerFlow.nickname)
    await callback.message.edit_text(t("admin_ask_player_nickname", locale))
    await callback.answer()


@router.message(AdminProPlayerFlow.nickname)
async def get_nickname(message: Message, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        return
    await state.update_data(nickname=message.text.strip())
    await state.set_state(AdminProPlayerFlow.team)
    await message.answer(t("admin_ask_player_team", locale))


@router.message(AdminProPlayerFlow.team)
async def get_team(message: Message, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        return
    value = message.text.strip()
    await state.update_data(team=None if value == "-" else value)
    await state.set_state(AdminProPlayerFlow.region)
    await message.answer(t("admin_ask_player_region", locale))


@router.message(AdminProPlayerFlow.region)
async def get_region(message: Message, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        return
    value = message.text.strip()
    await state.update_data(region=None if value == "-" else value)
    await state.set_state(AdminProPlayerFlow.device)
    await message.answer(t("admin_ask_player_device", locale))


@router.message(AdminProPlayerFlow.device)
async def get_device(message: Message, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        return
    value = message.text.strip()
    await state.update_data(device=None if value == "-" else value)
    await state.set_state(AdminProPlayerFlow.fps)
    await message.answer(t("admin_ask_player_fps", locale))


@router.message(AdminProPlayerFlow.fps)
async def get_fps(message: Message, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        return
    try:
        fps_value = int(message.text.strip())
    except ValueError:
        fps_value = None
    await state.update_data(fps=fps_value)
    await state.set_state(AdminProPlayerFlow.gyro)
    await message.answer(t("admin_ask_player_gyro", locale))


@router.message(AdminProPlayerFlow.gyro)
async def get_gyro(message: Message, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        return
    value = message.text.strip().lower()
    await state.update_data(gyro=value in ("ha", "yes", "да"))
    await state.set_state(AdminProPlayerFlow.style)
    await message.answer(t("admin_ask_player_style", locale))


@router.message(AdminProPlayerFlow.style)
async def get_style(message: Message, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        return
    await state.update_data(style=message.text.strip().lower())
    await state.set_state(AdminProPlayerFlow.source)
    await message.answer(t("admin_ask_player_source", locale))


@router.message(AdminProPlayerFlow.source)
async def get_source(message: Message, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        return
    value = message.text.strip()
    await state.update_data(source=None if value == "-" else value)
    await state.set_state(AdminProPlayerFlow.verified)
    await message.answer(t("admin_ask_player_verified", locale))


@router.message(AdminProPlayerFlow.verified)
async def get_verified_and_save(
    message: Message, state: FSMContext, locale: str, is_admin: bool, session: AsyncSession
) -> None:
    if not is_admin:
        return
    verified = message.text.strip().lower() in ("ha", "yes", "да")
    data = await state.get_data()
    await state.clear()

    player = await add_player(
        session,
        nickname=data["nickname"],
        team=data.get("team"),
        region=data.get("region"),
        device=data.get("device"),
        fps=data.get("fps"),
        gyroscope_enabled=data.get("gyro"),
        play_style=data.get("style"),
        source_url=data.get("source"),
        verified=verified,
    )
    await message.answer(t("admin_player_added", locale, nickname=player.nickname))
    await message.answer(t("admin_panel_title", locale), reply_markup=admin_panel_keyboard(locale))


# ---------------------------------------------------------------------------
# DELETE PRO PLAYER FLOW
# ---------------------------------------------------------------------------


@router.callback_query(AdminProPlayerCB.filter(F.action == "delete"))
async def start_delete_player(callback: CallbackQuery, state: FSMContext, locale: str, is_admin: bool) -> None:
    if not is_admin:
        await callback.answer(t("admin_not_allowed", locale), show_alert=True)
        return
    await state.set_state(AdminProPlayerFlow.delete_nickname)
    await callback.message.edit_text(t("admin_ask_player_nickname", locale))
    await callback.answer()


@router.message(AdminProPlayerFlow.delete_nickname)
async def do_delete_player(
    message: Message, state: FSMContext, locale: str, is_admin: bool, session: AsyncSession
) -> None:
    if not is_admin:
        return
    nickname = message.text.strip()
    await state.clear()
    ok = await delete_player(session, nickname)
    if ok:
        await message.answer(t("admin_player_deleted", locale, nickname=nickname))
    else:
        await message.answer(t("admin_user_not_found", locale))
    await message.answer(t("admin_panel_title", locale), reply_markup=admin_panel_keyboard(locale))
