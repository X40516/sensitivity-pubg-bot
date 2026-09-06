"""
Asosiy menyu va umumiy (back/home) keyboardlar.
"""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings
from app.keyboards.callback_data import MenuCB
from app.services.i18n import t


def main_menu_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    items = [
        ("btn_create_sensitivity", "create_sensitivity"),
        ("btn_pro_players", "pro_players"),
        ("btn_my_phone", "my_phone"),
        ("btn_by_weapon", "by_weapon"),
        ("btn_pro_presets", "pro_presets"),
        ("btn_test", "test"),
        ("btn_saved", "saved"),
        ("btn_referral", "referral"),
        ("btn_premium", "premium"),
        ("btn_language", "language"),
        ("btn_help", "help"),
    ]
    for text_key, action in items:
        builder.button(text=t(text_key, locale), callback_data=MenuCB(action=action))
    builder.adjust(2)
    # Admin bilan bog'lanish tugmasi — alohida qatorda, to'liq kenglikda
    builder.row(InlineKeyboardButton(text=t("btn_contact_admin", locale), url=settings.admin_contact_url))
    return builder.as_markup()


def contact_admin_button(locale: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=t("btn_contact_admin", locale), url=settings.admin_contact_url)


def back_home_row(locale: str, back_action: str = "back", home_action: str = "home") -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text=t("btn_back", locale), callback_data=MenuCB(action=back_action).pack()),
        InlineKeyboardButton(text=t("btn_home", locale), callback_data=MenuCB(action=home_action).pack()),
    ]


def with_back_home(builder: InlineKeyboardBuilder, locale: str) -> InlineKeyboardMarkup:
    builder.row(*back_home_row(locale))
    return builder.as_markup()


def simple_back_home_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    return with_back_home(builder, locale)
