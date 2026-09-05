"""
🔫 Qurol bo'yicha va 🔥 Pro Presetlar bo'limlari.

MUHIM: bu yerdagi qiymatlar generator formulasi asosida hisoblangan tavsiyalar,
haqiqiy pro o'yinchining sozlamalari sifatida taqdim etilmaydi.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.callback_data import MenuCB, PresetCB, WeaponCB
from app.keyboards.main_menu import with_back_home
from app.keyboards.misc import presets_menu_keyboard, weapons_menu_keyboard
from app.services.formatting import format_sensitivity_result
from app.services.i18n import t
from app.services.sensitivity_generator import SensitivityInput, generate_sensitivity

router = Router(name="weapon_presets")

# Har bir preset uchun standart parametrlar (barqaror, ma'lum formula asosida)
PRESET_DEFAULTS: dict[str, dict] = {
    "rush": dict(play_style="rush", weapon="Vector", scope="red_dot", level="high"),
    "spray": dict(play_style="spray", weapon="M416", scope="2x", level="medium"),
    "sniper": dict(play_style="sniper", weapon="AWM", scope="8x", level="low"),
    "fast_aim": dict(play_style="rush", weapon="UMP45", scope="red_dot", level="high"),
    "full_gyro": dict(play_style="balanced", weapon="M416", scope="2x", level="medium"),
    "balanced": dict(play_style="balanced", weapon="M416", scope="3x", level="medium"),
}
DEFAULT_FPS = 90
DEFAULT_GYRO = True


@router.callback_query(MenuCB.filter(F.action == "by_weapon"))
async def show_weapon_menu(callback: CallbackQuery, locale: str) -> None:
    await callback.message.edit_text(t("weapon_presets_title", locale), reply_markup=weapons_menu_keyboard(locale))
    await callback.answer()


@router.callback_query(WeaponCB.filter())
async def show_weapon_preset(callback: CallbackQuery, callback_data: WeaponCB, locale: str) -> None:
    sensitivity_input = SensitivityInput(
        phone_model=None,
        fps=DEFAULT_FPS,
        gyroscope_enabled=DEFAULT_GYRO,
        play_style="balanced",
        weapon=callback_data.name,
        scope="red_dot",
        level="medium",
    )
    result = generate_sensitivity(sensitivity_input)
    text = f"🔫 <b>{callback_data.name}</b>\n\n{format_sensitivity_result(result, locale)}"

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    await callback.message.edit_text(text, reply_markup=with_back_home(builder, locale))
    await callback.answer()


@router.callback_query(MenuCB.filter(F.action == "pro_presets"))
async def show_presets_menu(callback: CallbackQuery, locale: str) -> None:
    await callback.message.edit_text(t("pro_presets_title", locale), reply_markup=presets_menu_keyboard(locale))
    await callback.answer()


@router.callback_query(PresetCB.filter())
async def show_preset_result(callback: CallbackQuery, callback_data: PresetCB, locale: str) -> None:
    defaults = PRESET_DEFAULTS.get(callback_data.name)
    if not defaults:
        await callback.answer(t("error_generic", locale), show_alert=True)
        return

    sensitivity_input = SensitivityInput(
        phone_model=None,
        fps=DEFAULT_FPS,
        gyroscope_enabled=(callback_data.name == "full_gyro") or DEFAULT_GYRO,
        play_style=defaults["play_style"],
        weapon=defaults["weapon"],
        scope=defaults["scope"],
        level=defaults["level"],
    )
    result = generate_sensitivity(sensitivity_input)
    preset_label = t(f"preset_{callback_data.name}", locale)
    text = f"{preset_label}\n\n{format_sensitivity_result(result, locale)}"

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    await callback.message.edit_text(text, reply_markup=with_back_home(builder, locale))
    await callback.answer()
