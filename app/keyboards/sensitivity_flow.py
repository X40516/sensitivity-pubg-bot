"""
Sensitivity yaratish oqimidagi har bir qadam uchun keyboardlar.
"""
from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.callback_data import FlowCB, PhoneBrandCB, ResultCB
from app.keyboards.main_menu import with_back_home
from app.services.i18n import t

PHONE_BRANDS = [
    "Apple", "Samsung", "Xiaomi", "Redmi", "POCO",
    "OnePlus", "Huawei", "Realme", "OPPO", "Vivo", "Boshqa",
]

FPS_OPTIONS = [60, 90, 120]

WEAPONS = [
    "M416", "AKM", "M762", "SCAR-L", "AUG", "UMP45", "Vector",
    "DP-28", "MG3", "AWM", "M24", "Kar98k", "Mini14", "MK14",
]

SCOPES = [
    ("Red Dot", "red_dot"),
    ("2x", "2x"),
    ("3x", "3x"),
    ("4x", "4x"),
    ("6x", "6x"),
    ("8x", "8x"),
]

LEVELS = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]

PLAY_STYLES = [
    ("rush", "Rush"),
    ("spray", "Spray"),
    ("balanced", "Balanced"),
    ("sniper", "Sniper"),
]


def phone_brand_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for brand in PHONE_BRANDS:
        builder.button(text=brand, callback_data=PhoneBrandCB(brand=brand))
    builder.adjust(3)
    return with_back_home(builder, locale)


def fps_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for fps in FPS_OPTIONS:
        builder.button(text=f"{fps} FPS", callback_data=FlowCB(step="fps", value=str(fps)))
    builder.adjust(3)
    return with_back_home(builder, locale)


def gyroscope_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="ON", callback_data=FlowCB(step="gyro", value="on"))
    builder.button(text="OFF", callback_data=FlowCB(step="gyro", value="off"))
    builder.adjust(2)
    return with_back_home(builder, locale)


def play_style_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for value, label in PLAY_STYLES:
        builder.button(text=label, callback_data=FlowCB(step="style", value=value))
    builder.adjust(2)
    return with_back_home(builder, locale)


def weapon_keyboard(locale: str, step: str = "weapon") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for weapon in WEAPONS:
        builder.button(text=weapon, callback_data=FlowCB(step=step, value=weapon))
    builder.adjust(3)
    return with_back_home(builder, locale)


def scope_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, value in SCOPES:
        builder.button(text=label, callback_data=FlowCB(step="scope", value=value))
    builder.adjust(3)
    return with_back_home(builder, locale)


def level_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for value, label in LEVELS:
        builder.button(text=label, callback_data=FlowCB(step="level", value=value))
    builder.adjust(3)
    return with_back_home(builder, locale)


def result_actions_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_copy", locale), callback_data=ResultCB(action="copy"))
    builder.button(text=t("btn_save", locale), callback_data=ResultCB(action="save"))
    builder.button(text=t("btn_regenerate", locale), callback_data=ResultCB(action="regenerate"))
    builder.button(text=t("btn_test_it", locale), callback_data=ResultCB(action="test"))
    builder.button(text=t("btn_send_friend", locale), callback_data=ResultCB(action="send_friend"))
    builder.adjust(2, 2, 1)
    return with_back_home(builder, locale)
