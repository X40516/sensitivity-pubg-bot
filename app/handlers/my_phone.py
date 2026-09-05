"""
📱 Telefonim bo'limi.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.handlers.states import MyPhoneFlow
from app.keyboards.callback_data import MenuCB, PhoneBrandCB
from app.keyboards.main_menu import with_back_home
from app.keyboards.sensitivity_flow import phone_brand_keyboard
from app.services.i18n import t
from app.services.user_service import get_user_settings, update_phone

router = Router(name="my_phone")


def _phone_view_keyboard(locale: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_change_phone", locale), callback_data=MenuCB(action="my_phone_change"))
    builder.adjust(1)
    return with_back_home(builder, locale)


@router.callback_query(MenuCB.filter(F.action == "my_phone"))
async def show_my_phone(callback: CallbackQuery, locale: str, session: AsyncSession, db_user: User) -> None:
    user_settings = await get_user_settings(session, db_user.id)
    if user_settings and user_settings.phone_model:
        text = t("phone_current", locale, model=user_settings.phone_model)
    else:
        text = t("phone_none", locale)
    await callback.message.edit_text(text, reply_markup=_phone_view_keyboard(locale))
    await callback.answer()


@router.callback_query(MenuCB.filter(F.action == "my_phone_change"))
async def change_phone_start(callback: CallbackQuery, state: FSMContext, locale: str) -> None:
    await state.set_state(MyPhoneFlow.phone_brand)
    await callback.message.edit_text(t("ask_phone_model", locale), reply_markup=phone_brand_keyboard(locale))
    await callback.answer()


@router.callback_query(MyPhoneFlow.phone_brand, PhoneBrandCB.filter())
async def change_phone_brand(
    callback: CallbackQuery, callback_data: PhoneBrandCB, state: FSMContext, locale: str
) -> None:
    await state.update_data(phone_brand=callback_data.brand)
    await state.set_state(MyPhoneFlow.phone_model_text)
    from app.keyboards.main_menu import simple_back_home_keyboard

    await callback.message.edit_text(t("ask_phone_model_text", locale), reply_markup=simple_back_home_keyboard(locale))
    await callback.answer()


@router.message(MyPhoneFlow.phone_model_text)
async def change_phone_model_text(
    message: Message, state: FSMContext, locale: str, session: AsyncSession, db_user: User
) -> None:
    data = await state.get_data()
    brand = data.get("phone_brand", "")
    model_name = message.text.strip()[:128]
    full_model = f"{brand} {model_name}".strip()
    await update_phone(session, db_user.id, brand, full_model)
    await state.clear()
    await message.answer(t("phone_saved", locale, model=full_model))
    from app.keyboards.main_menu import main_menu_keyboard

    await message.answer(t("main_menu", locale), reply_markup=main_menu_keyboard(locale))
