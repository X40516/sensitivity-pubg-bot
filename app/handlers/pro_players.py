"""
🏆 Pro Players bo'limi. Faqat admin kiritgan real ma'lumotlar ko'rsatiladi.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.callback_data import MenuCB, ProFilterCB, ProPlayerCB
from app.keyboards.main_menu import simple_back_home_keyboard, with_back_home
from app.keyboards.misc import pro_players_list_keyboard, pro_players_menu_keyboard
from app.services.i18n import t
from app.services.pro_player_service import (
    filter_players,
    get_latest_sensitivity,
    get_player,
    list_players,
    top10_players,
)

router = Router(name="pro_players")


class ProFilterFlow(StatesGroup):
    waiting_value = State()


FILTER_FIELDS = [
    ("filter_by_region", "region"),
    ("filter_by_team", "team"),
    ("filter_by_device", "device"),
    ("filter_by_fps", "fps"),
    ("filter_by_gyro", "gyro"),
    ("filter_by_style", "style"),
]


@router.callback_query(ProPlayerCB.filter(F.action == "filter"))
async def show_filter_menu(callback: CallbackQuery, locale: str) -> None:
    builder = InlineKeyboardBuilder()
    for text_key, field in FILTER_FIELDS:
        builder.button(text=t(text_key, locale), callback_data=ProFilterCB(field=field))
    builder.adjust(2)
    await callback.message.edit_text(t("btn_filter", locale), reply_markup=with_back_home(builder, locale))
    await callback.answer()


@router.callback_query(ProFilterCB.filter(F.value == ""))
async def ask_filter_value(callback: CallbackQuery, callback_data: ProFilterCB, state: FSMContext, locale: str) -> None:
    await state.set_state(ProFilterFlow.waiting_value)
    await state.update_data(filter_field=callback_data.field)
    await callback.message.edit_text(
        f"🔍 {callback_data.field}: qiymatni kiriting", reply_markup=simple_back_home_keyboard(locale)
    )
    await callback.answer()


@router.message(ProFilterFlow.waiting_value)
async def apply_filter(message: Message, state: FSMContext, locale: str, session: AsyncSession) -> None:
    data = await state.get_data()
    field = data.get("filter_field")
    value = message.text.strip()
    await state.clear()

    kwargs: dict = {}
    if field == "region":
        kwargs["region"] = value
    elif field == "team":
        kwargs["team"] = value
    elif field == "device":
        kwargs["device"] = value
    elif field == "fps":
        try:
            kwargs["fps"] = int(value)
        except ValueError:
            pass
    elif field == "gyro":
        kwargs["gyroscope_enabled"] = value.lower() in ("ha", "yes", "on", "да")
    elif field == "style":
        kwargs["play_style"] = value.lower()

    players = await filter_players(session, **kwargs)
    if not players:
        await message.answer(t("no_pro_players", locale), reply_markup=simple_back_home_keyboard(locale))
    else:
        items = [(p.id, p.nickname) for p in players]
        await message.answer(t("pro_players_title", locale), reply_markup=pro_players_list_keyboard(locale, items))


@router.callback_query(MenuCB.filter(F.action == "pro_players"))
async def show_pro_players_menu(callback: CallbackQuery, locale: str) -> None:
    await callback.message.edit_text(t("pro_players_title", locale), reply_markup=pro_players_menu_keyboard(locale))
    await callback.answer()


@router.callback_query(ProPlayerCB.filter(F.action == "top10"))
async def show_top10(callback: CallbackQuery, locale: str, session: AsyncSession) -> None:
    players = await top10_players(session)
    if not players:
        await callback.message.edit_text(t("no_pro_players", locale), reply_markup=simple_back_home_keyboard(locale))
        await callback.answer()
        return
    medals = ["🥇", "🥈", "🥉"] + [f"{i}️⃣" for i in range(4, 10)] + ["🔟"]
    items = []
    for idx, player in enumerate(players):
        prefix = medals[idx] if idx < len(medals) else f"{idx + 1}."
        items.append((player.id, f"{prefix} {player.nickname}"))
    await callback.message.edit_text(
        t("btn_top10", locale), reply_markup=pro_players_list_keyboard(locale, items)
    )
    await callback.answer()


@router.callback_query(ProPlayerCB.filter(F.action == "list"))
async def show_all_players(callback: CallbackQuery, locale: str, session: AsyncSession) -> None:
    players = await list_players(session)
    if not players:
        await callback.message.edit_text(t("no_pro_players", locale), reply_markup=simple_back_home_keyboard(locale))
    else:
        items = [(p.id, p.nickname) for p in players]
        await callback.message.edit_text(
            t("pro_players_title", locale), reply_markup=pro_players_list_keyboard(locale, items)
        )
    await callback.answer()


def _format_sensitivity_block(title: str, values: dict | None, locale: str) -> str:
    if not values:
        return f"{title}\n{t('sensitivity_not_found', locale)}"
    lines = [title] + [f"{k}: {v}%" for k, v in values.items()]
    return "\n".join(lines)


@router.callback_query(ProPlayerCB.filter(F.action == "view"))
async def view_player(callback: CallbackQuery, callback_data: ProPlayerCB, locale: str, session: AsyncSession) -> None:
    player = await get_player(session, callback_data.player_id)
    if not player:
        await callback.answer(t("error_generic", locale), show_alert=True)
        return

    sensitivity = await get_latest_sensitivity(session, player.id)

    lines = [
        f"👤 <b>{player.nickname}</b>",
        f"👥 {player.team or '-'}",
        f"🌍 {player.region or '-'}",
        f"📱 {player.device or '-'}",
        f"⚡ {player.fps or '-'} FPS" if player.fps else "⚡ -",
        f"🔄 {'ON' if player.gyroscope_enabled else 'OFF' if player.gyroscope_enabled is not None else '-'}",
        f"🎮 {player.play_style or '-'}",
        "",
    ]

    if sensitivity:
        lines.append(_format_sensitivity_block(t("result_camera", locale), sensitivity.camera_sensitivity, locale))
        lines.append("")
        lines.append(_format_sensitivity_block(t("result_ads", locale), sensitivity.ads_sensitivity, locale))
        lines.append("")
        lines.append(
            _format_sensitivity_block(t("result_gyro", locale), sensitivity.gyroscope_sensitivity, locale)
        )
        lines.append("")
        lines.append(
            _format_sensitivity_block(t("result_ads_gyro", locale), sensitivity.ads_gyroscope_sensitivity, locale)
        )
        lines.append("")
        badge = t("verified", locale) if sensitivity.verified else t("unverified", locale)
        lines.append(badge)
        if sensitivity.source_url:
            lines.append(f"{t('source_label', locale)}: {sensitivity.source_url}")
        lines.append(f"{t('last_updated_label', locale)}: {sensitivity.last_updated.strftime('%Y-%m-%d')}")
    else:
        lines.append(t("sensitivity_not_found", locale))

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    await callback.message.edit_text("\n".join(lines), reply_markup=with_back_home(builder, locale))
    await callback.answer()
