"""
/start, bosh menyu, yordam, til tanlash handlerlari.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.keyboards.callback_data import LanguageCB, MenuCB
from app.keyboards.main_menu import main_menu_keyboard
from app.keyboards.misc import language_keyboard
from app.services.i18n import t
from app.services.user_service import set_language

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, locale: str, db_user: User) -> None:
    await state.clear()
    await message.answer(t("start_message", locale))
    await message.answer(t("main_menu", locale), reply_markup=main_menu_keyboard(locale))


@router.callback_query(MenuCB.filter(F.action == "home"))
async def go_home(callback: CallbackQuery, state: FSMContext, locale: str) -> None:
    await state.clear()
    await callback.message.edit_text(t("main_menu", locale), reply_markup=main_menu_keyboard(locale))
    await callback.answer()


@router.callback_query(MenuCB.filter(F.action == "back"))
async def go_back(callback: CallbackQuery, state: FSMContext, locale: str) -> None:
    # Soddalashtirilgan navigatsiya: "Orqaga" bosilganda bosh menyuga qaytariladi
    # (har bir oqim o'z ichida oldingi qadamga qaytarish logikasini alohida belgilashi mumkin).
    await state.clear()
    await callback.message.edit_text(t("main_menu", locale), reply_markup=main_menu_keyboard(locale))
    await callback.answer()


@router.callback_query(MenuCB.filter(F.action == "help"))
async def show_help(callback: CallbackQuery, locale: str) -> None:
    from app.keyboards.main_menu import simple_back_home_keyboard

    await callback.message.edit_text(t("help_text", locale), reply_markup=simple_back_home_keyboard(locale))
    await callback.answer()


@router.callback_query(MenuCB.filter(F.action == "language"))
async def show_language(callback: CallbackQuery, locale: str) -> None:
    await callback.message.edit_text(t("language_title", locale), reply_markup=language_keyboard())
    await callback.answer()


@router.callback_query(LanguageCB.filter())
async def set_user_language(
    callback: CallbackQuery, callback_data: LanguageCB, session: AsyncSession, db_user: User
) -> None:
    await set_language(session, db_user.id, callback_data.code)
    new_locale = callback_data.code
    await callback.answer(t("language_changed", new_locale))
    await callback.message.edit_text(t("main_menu", new_locale), reply_markup=main_menu_keyboard(new_locale))
