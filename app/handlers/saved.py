"""
💾 Saqlangan sensitivity — ko'rish, nomini o'zgartirish, o'chirish.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.handlers.states import SavedProfileFlow
from app.keyboards.callback_data import ConfirmCB, MenuCB, SavedProfileCB
from app.keyboards.main_menu import main_menu_keyboard, simple_back_home_keyboard
from app.keyboards.misc import confirm_delete_keyboard, saved_profile_detail_keyboard, saved_profiles_keyboard
from app.services.formatting import format_sensitivity_result
from app.services.i18n import t
from app.services.profile_service import delete_profile, get_profile, list_profiles, rename_profile

router = Router(name="saved")


@router.callback_query(MenuCB.filter(F.action == "saved"))
async def show_saved_profiles(callback: CallbackQuery, locale: str, session: AsyncSession, db_user: User) -> None:
    profiles = await list_profiles(session, db_user.id)
    if not profiles:
        await callback.message.edit_text(t("no_saved_profiles", locale), reply_markup=simple_back_home_keyboard(locale))
    else:
        items = [(p.id, p.name) for p in profiles]
        await callback.message.edit_text(
            t("saved_profiles_title", locale), reply_markup=saved_profiles_keyboard(locale, items)
        )
    await callback.answer()


@router.callback_query(SavedProfileCB.filter(F.action == "view"))
async def view_profile(
    callback: CallbackQuery, callback_data: SavedProfileCB, locale: str, session: AsyncSession, db_user: User
) -> None:
    profile = await get_profile(session, callback_data.profile_id, db_user.id)
    if not profile:
        await callback.answer(t("error_generic", locale), show_alert=True)
        return
    text = f"💾 <b>{profile.name}</b>\n\n{format_sensitivity_result(profile.result_json, locale)}"
    await callback.message.edit_text(
        text, reply_markup=saved_profile_detail_keyboard(locale, profile.id)
    )
    await callback.answer()


@router.callback_query(SavedProfileCB.filter(F.action == "rename"))
async def ask_rename(
    callback: CallbackQuery, callback_data: SavedProfileCB, state: FSMContext, locale: str
) -> None:
    await state.set_state(SavedProfileFlow.renaming)
    await state.update_data(rename_profile_id=callback_data.profile_id)
    await callback.message.edit_text(t("ask_new_name", locale), reply_markup=simple_back_home_keyboard(locale))
    await callback.answer()


@router.message(SavedProfileFlow.renaming)
async def do_rename(message: Message, state: FSMContext, locale: str, session: AsyncSession, db_user: User) -> None:
    data = await state.get_data()
    profile_id = data.get("rename_profile_id")
    new_name = message.text.strip()[:64]
    ok = await rename_profile(session, profile_id, db_user.id, new_name)
    await state.clear()
    if ok:
        await message.answer(t("renamed_ok", locale, name=new_name))
    else:
        await message.answer(t("error_generic", locale))
    await message.answer(t("main_menu", locale), reply_markup=main_menu_keyboard(locale))


@router.callback_query(SavedProfileCB.filter(F.action == "delete"))
async def ask_delete_confirm(callback: CallbackQuery, callback_data: SavedProfileCB, locale: str) -> None:
    await callback.message.edit_text(
        t("confirm_delete", locale), reply_markup=confirm_delete_keyboard(locale, callback_data.profile_id)
    )
    await callback.answer()


@router.callback_query(ConfirmCB.filter(F.context == "delete_profile"))
async def confirm_delete(
    callback: CallbackQuery, callback_data: ConfirmCB, locale: str, session: AsyncSession, db_user: User
) -> None:
    if callback_data.action == "yes":
        await delete_profile(session, callback_data.ref_id, db_user.id)
        await callback.answer(t("deleted_ok", locale))
    else:
        await callback.answer(t("cancelled", locale))

    profiles = await list_profiles(session, db_user.id)
    if not profiles:
        await callback.message.edit_text(t("no_saved_profiles", locale), reply_markup=simple_back_home_keyboard(locale))
    else:
        items = [(p.id, p.name) for p in profiles]
        await callback.message.edit_text(
            t("saved_profiles_title", locale), reply_markup=saved_profiles_keyboard(locale, items)
        )
