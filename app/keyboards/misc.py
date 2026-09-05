"""
Qolgan bo'limlar uchun keyboardlar: saqlangan profillar, test feedback,
til, pro players, presetlar, referral, premium.
"""
from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.callback_data import (
    ConfirmCB,
    LanguageCB,
    MenuCB,
    PresetCB,
    ProPlayerCB,
    SavedProfileCB,
    TestFeedbackCB,
    WeaponCB,
)
from app.keyboards.main_menu import with_back_home
from app.keyboards.sensitivity_flow import WEAPONS
from app.services.i18n import locale_display_name, t

PRESETS = [
    ("preset_rush", "rush"),
    ("preset_spray", "spray"),
    ("preset_sniper", "sniper"),
    ("preset_fast_aim", "fast_aim"),
    ("preset_full_gyro", "full_gyro"),
    ("preset_balanced", "balanced"),
]


def saved_profiles_keyboard(locale: str, profiles: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for profile_id, name in profiles:
        builder.button(text=f"💾 {name}", callback_data=SavedProfileCB(action="view", profile_id=profile_id))
    builder.adjust(1)
    return with_back_home(builder, locale)


def saved_profile_detail_keyboard(locale: str, profile_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_rename", locale), callback_data=SavedProfileCB(action="rename", profile_id=profile_id))
    builder.button(text=t("btn_delete", locale), callback_data=SavedProfileCB(action="delete", profile_id=profile_id))
    builder.adjust(2)
    return with_back_home(builder, locale)


def confirm_delete_keyboard(locale: str, profile_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t("btn_confirm_yes", locale),
        callback_data=ConfirmCB(action="yes", context="delete_profile", ref_id=profile_id),
    )
    builder.button(
        text=t("btn_confirm_no", locale),
        callback_data=ConfirmCB(action="no", context="delete_profile", ref_id=profile_id),
    )
    builder.adjust(2)
    return builder.as_markup()


def test_aim_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("aim_too_fast", locale), callback_data=TestFeedbackCB(category="aim", value="too_fast"))
    builder.button(text=t("aim_too_slow", locale), callback_data=TestFeedbackCB(category="aim", value="too_slow"))
    builder.button(text=t("aim_good", locale), callback_data=TestFeedbackCB(category="aim", value="good"))
    builder.adjust(1)
    return with_back_home(builder, locale)


def test_recoil_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("recoil_up", locale), callback_data=TestFeedbackCB(category="recoil", value="goes_up"))
    builder.button(text=t("recoil_down", locale), callback_data=TestFeedbackCB(category="recoil", value="goes_down"))
    builder.button(text=t("recoil_good", locale), callback_data=TestFeedbackCB(category="recoil", value="good"))
    builder.adjust(1)
    return with_back_home(builder, locale)


def test_scope_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("scope_shaky", locale), callback_data=TestFeedbackCB(category="scope", value="shaky"))
    builder.button(text=t("scope_slow", locale), callback_data=TestFeedbackCB(category="scope", value="slow"))
    builder.button(text=t("scope_fast", locale), callback_data=TestFeedbackCB(category="scope", value="fast"))
    builder.button(text=t("scope_good", locale), callback_data=TestFeedbackCB(category="scope", value="good"))
    builder.adjust(2)
    return with_back_home(builder, locale)


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code in ("uz", "ru", "en"):
        builder.button(text=locale_display_name(code), callback_data=LanguageCB(code=code))
    builder.adjust(1)
    return builder.as_markup()


def pro_players_menu_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_top10", locale), callback_data=ProPlayerCB(action="top10"))
    builder.button(text=t("btn_filter", locale), callback_data=ProPlayerCB(action="filter"))
    builder.adjust(1)
    return with_back_home(builder, locale)


def pro_players_list_keyboard(locale: str, players: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for player_id, nickname in players:
        builder.button(text=f"👤 {nickname}", callback_data=ProPlayerCB(action="view", player_id=player_id))
    builder.adjust(2)
    return with_back_home(builder, locale)


def weapons_menu_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for weapon in WEAPONS:
        builder.button(text=f"🔫 {weapon}", callback_data=WeaponCB(name=weapon))
    builder.adjust(3)
    return with_back_home(builder, locale)


def presets_menu_keyboard(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text_key, name in PRESETS:
        builder.button(text=t(text_key, locale), callback_data=PresetCB(name=name))
    builder.adjust(2)
    return with_back_home(builder, locale)
