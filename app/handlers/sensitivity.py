"""
🎯 Sensitivity yaratish — asosiy oqim.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.handlers.states import SensitivityFlow
from app.keyboards.callback_data import FlowCB, MenuCB, PhoneBrandCB, ResultCB
from app.keyboards.main_menu import main_menu_keyboard
from app.keyboards.sensitivity_flow import (
    fps_keyboard,
    gyroscope_keyboard,
    level_keyboard,
    phone_brand_keyboard,
    play_style_keyboard,
    result_actions_keyboard,
    scope_keyboard,
    weapon_keyboard,
)
from app.services.formatting import format_plain_copy_text, format_sensitivity_result
from app.services.i18n import t
from app.services.profile_service import add_history, can_save_more, save_profile
from app.services.sensitivity_generator import SensitivityInput, generate_sensitivity
from app.services.user_service import get_user_settings

router = Router(name="sensitivity")


@router.callback_query(MenuCB.filter(F.action == "create_sensitivity"))
async def start_sensitivity_flow(
    callback: CallbackQuery, state: FSMContext, locale: str, session: AsyncSession, db_user: User
) -> None:
    await state.clear()

    # Agar foydalanuvchi telefon modelini oldin saqlagan bo'lsa, shu qadamni o'tkazib yuboramiz
    user_settings = await get_user_settings(session, db_user.id)
    if user_settings and user_settings.phone_model:
        await state.update_data(phone_model=user_settings.phone_model)
        await state.set_state(SensitivityFlow.fps)
        await callback.message.edit_text(t("ask_fps", locale), reply_markup=fps_keyboard(locale))
    else:
        await state.set_state(SensitivityFlow.phone_brand)
        await callback.message.edit_text(t("ask_phone_model", locale), reply_markup=phone_brand_keyboard(locale))
    await callback.answer()


@router.callback_query(SensitivityFlow.phone_brand, PhoneBrandCB.filter())
async def choose_phone_brand(
    callback: CallbackQuery, callback_data: PhoneBrandCB, state: FSMContext, locale: str
) -> None:
    await state.update_data(phone_brand=callback_data.brand)
    await state.set_state(SensitivityFlow.phone_model_text)
    from app.keyboards.main_menu import simple_back_home_keyboard

    await callback.message.edit_text(t("ask_phone_model_text", locale), reply_markup=simple_back_home_keyboard(locale))
    await callback.answer()


@router.message(SensitivityFlow.phone_model_text)
async def enter_phone_model_text(message: Message, state: FSMContext, locale: str) -> None:
    data = await state.get_data()
    brand = data.get("phone_brand", "")
    model_name = message.text.strip()[:128]
    full_model = f"{brand} {model_name}".strip()
    await state.update_data(phone_model=full_model)
    await state.set_state(SensitivityFlow.fps)
    await message.answer(t("ask_fps", locale), reply_markup=fps_keyboard(locale))


@router.callback_query(SensitivityFlow.fps, FlowCB.filter(F.step == "fps"))
async def choose_fps(callback: CallbackQuery, callback_data: FlowCB, state: FSMContext, locale: str) -> None:
    await state.update_data(fps=int(callback_data.value))
    await state.set_state(SensitivityFlow.gyroscope)
    await callback.message.edit_text(t("ask_gyroscope", locale), reply_markup=gyroscope_keyboard(locale))
    await callback.answer()


@router.callback_query(SensitivityFlow.gyroscope, FlowCB.filter(F.step == "gyro"))
async def choose_gyroscope(callback: CallbackQuery, callback_data: FlowCB, state: FSMContext, locale: str) -> None:
    await state.update_data(gyroscope_enabled=(callback_data.value == "on"))
    await state.set_state(SensitivityFlow.play_style)
    await callback.message.edit_text(t("ask_play_style", locale), reply_markup=play_style_keyboard(locale))
    await callback.answer()


@router.callback_query(SensitivityFlow.play_style, FlowCB.filter(F.step == "style"))
async def choose_play_style(callback: CallbackQuery, callback_data: FlowCB, state: FSMContext, locale: str) -> None:
    await state.update_data(play_style=callback_data.value)
    await state.set_state(SensitivityFlow.weapon)
    await callback.message.edit_text(t("ask_weapon", locale), reply_markup=weapon_keyboard(locale))
    await callback.answer()


@router.callback_query(SensitivityFlow.weapon, FlowCB.filter(F.step == "weapon"))
async def choose_weapon(callback: CallbackQuery, callback_data: FlowCB, state: FSMContext, locale: str) -> None:
    await state.update_data(weapon=callback_data.value)
    await state.set_state(SensitivityFlow.scope)
    await callback.message.edit_text(t("ask_scope", locale), reply_markup=scope_keyboard(locale))
    await callback.answer()


@router.callback_query(SensitivityFlow.scope, FlowCB.filter(F.step == "scope"))
async def choose_scope(callback: CallbackQuery, callback_data: FlowCB, state: FSMContext, locale: str) -> None:
    await state.update_data(scope=callback_data.value)
    await state.set_state(SensitivityFlow.level)
    await callback.message.edit_text(t("ask_level", locale), reply_markup=level_keyboard(locale))
    await callback.answer()


async def _generate_and_show(
    callback: CallbackQuery, state: FSMContext, locale: str, session: AsyncSession, db_user: User
) -> None:
    data = await state.get_data()
    sensitivity_input = SensitivityInput(
        phone_model=data.get("phone_model"),
        fps=data["fps"],
        gyroscope_enabled=data["gyroscope_enabled"],
        play_style=data["play_style"],
        weapon=data["weapon"],
        scope=data["scope"],
        level=data["level"],
    )
    await callback.message.edit_text(t("generating", locale))
    result = generate_sensitivity(sensitivity_input)
    await add_history(session, db_user.id, sensitivity_input.__dict__, result)

    await state.update_data(last_result=result)
    await state.set_state(SensitivityFlow.result)

    text = f"{t('ready', locale)}\n\n{format_sensitivity_result(result, locale)}"
    await callback.message.edit_text(text, reply_markup=result_actions_keyboard(locale))


@router.callback_query(SensitivityFlow.level, FlowCB.filter(F.step == "level"))
async def choose_level_and_generate(
    callback: CallbackQuery,
    callback_data: FlowCB,
    state: FSMContext,
    locale: str,
    session: AsyncSession,
    db_user: User,
) -> None:
    await state.update_data(level=callback_data.value)
    await _generate_and_show(callback, state, locale, session, db_user)
    await callback.answer()


@router.callback_query(SensitivityFlow.result, ResultCB.filter(F.action == "regenerate"))
async def regenerate(
    callback: CallbackQuery, state: FSMContext, locale: str, session: AsyncSession, db_user: User
) -> None:
    await _generate_and_show(callback, state, locale, session, db_user)
    await callback.answer()


@router.callback_query(SensitivityFlow.result, ResultCB.filter(F.action == "copy"))
async def copy_result(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    result = data.get("last_result")
    if not result:
        await callback.answer()
        return
    plain = format_plain_copy_text(result)
    await callback.message.answer(f"<pre>{plain}</pre>")
    await callback.answer()


@router.callback_query(SensitivityFlow.result, ResultCB.filter(F.action == "send_friend"))
async def send_to_friend(callback: CallbackQuery, state: FSMContext, locale: str) -> None:
    data = await state.get_data()
    result = data.get("last_result")
    if not result:
        await callback.answer()
        return
    text = format_sensitivity_result(result, locale)
    await callback.message.answer(
        f"{t('ready', locale)}\n\n{text}\n\n🤖 @sensitivitypubgbot orqali yaratildi."
    )
    await callback.answer()


@router.callback_query(SensitivityFlow.result, ResultCB.filter(F.action == "save"))
async def ask_save_name(
    callback: CallbackQuery, state: FSMContext, locale: str, session: AsyncSession, db_user: User
) -> None:
    if not await can_save_more(session, db_user.id):
        from app.config import settings

        await callback.answer(
            t("saved_limit_reached", locale, limit=settings.free_saved_profiles_limit), show_alert=True
        )
        return
    await state.set_state(SensitivityFlow.saving_name)
    from app.keyboards.main_menu import simple_back_home_keyboard

    await callback.message.edit_text(t("ask_save_name", locale), reply_markup=simple_back_home_keyboard(locale))
    await callback.answer()


@router.message(SensitivityFlow.saving_name)
async def save_with_name(
    message: Message, state: FSMContext, locale: str, session: AsyncSession, db_user: User
) -> None:
    data = await state.get_data()
    result = data.get("last_result")
    name = message.text.strip()[:64]
    if not result or not name:
        await message.answer(t("error_generic", locale))
        return
    await save_profile(session, db_user.id, name, result)
    await state.clear()
    await message.answer(t("saved_ok", locale, name=name))
    await message.answer(t("main_menu", locale), reply_markup=main_menu_keyboard(locale))
