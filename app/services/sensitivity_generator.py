"""
Sensitivity generatsiya algoritmi.

MUHIM: Bu yerdagi qiymatlar HAQIQIY pro o'yinchining sozlamalari emas — bu
FPS, gyroscope holati, o'yin uslubi, qurol va scope asosida hisoblab chiqilgan
formulaviy tavsiya (heuristic). Pro Players bo'limidagi ma'lumotlar esa faqat
admin tomonidan kiritilgan, manbali (sourced) real ma'lumotlar bo'lishi kerak —
ular bu modulda ARALASHTIRILMAYDI.
"""
from __future__ import annotations

from dataclasses import dataclass

# Scope bo'yicha bazaviy multiplikatorlar (uzoqroq scope -> pastroq sezgirlik)
SCOPE_MULTIPLIERS: dict[str, float] = {
    "red_dot": 1.00,
    "2x": 0.85,
    "3x": 0.70,
    "4x": 0.55,
    "6x": 0.40,
    "8x": 0.30,
}

# Qurol turi bo'yicha recoil-pattern koeffitsienti (tik/yon otish tezligi ta'siri)
WEAPON_RECOIL_FACTOR: dict[str, float] = {
    "M416": 1.00,
    "AKM": 0.90,
    "M762": 0.90,
    "SCAR-L": 1.02,
    "AUG": 1.03,
    "UMP45": 1.05,
    "Vector": 1.10,
    "DP-28": 0.85,
    "MG3": 0.80,
    "AWM": 0.60,
    "M24": 0.60,
    "Kar98k": 0.60,
    "Mini14": 0.75,
    "MK14": 0.78,
}

PLAY_STYLE_FACTOR: dict[str, float] = {
    "rush": 1.15,      # tezroq burilish kerak
    "spray": 0.95,     # barqarorlik muhimroq
    "balanced": 1.00,
    "sniper": 0.75,    # aniqlik uchun pastroq sezgirlik
}

LEVEL_FACTOR: dict[str, float] = {
    "low": 0.80,
    "medium": 1.00,
    "high": 1.25,
}

# FPS qanchalik yuqori bo'lsa, kamera shunchalik silliq harakatlanadi ->
# sezgirlikni biroz oshirish mumkin, chunki frame-time qisqaradi.
FPS_FACTOR: dict[int, float] = {
    60: 0.92,
    90: 1.00,
    120: 1.08,
}

BASE_CAMERA_SENSITIVITY = 55.0  # % (No Scope, TPP)
BASE_ADS_SENSITIVITY = 45.0
BASE_GYRO_SENSITIVITY = 180.0  # gyroscope % odatda 0-300 orasida beriladi PUBGM da
BASE_FREE_LOOK = 65.0

ALL_SCOPES = ["red_dot", "2x", "3x", "4x", "6x", "8x"]
SCOPE_LABELS = {
    "red_dot": "Red Dot",
    "2x": "2x",
    "3x": "3x",
    "4x": "4x",
    "6x": "6x",
    "8x": "8x",
}


def _clamp(value: float, low: float = 1.0, high: float = 300.0) -> float:
    return max(low, min(high, value))


@dataclass
class SensitivityInput:
    phone_model: str | None
    fps: int
    gyroscope_enabled: bool
    play_style: str  # rush | spray | balanced | sniper
    weapon: str
    scope: str  # red_dot | 2x | 3x | 4x | 6x | 8x
    level: str  # low | medium | high


def generate_sensitivity(data: SensitivityInput) -> dict:
    """Barcha kategoriyalar (camera/ads/gyro/ads_gyro/free_look) uchun to'liq jadval qaytaradi."""
    fps_factor = FPS_FACTOR.get(data.fps, 1.0)
    style_factor = PLAY_STYLE_FACTOR.get(data.play_style, 1.0)
    weapon_factor = WEAPON_RECOIL_FACTOR.get(data.weapon, 1.0)
    level_factor = LEVEL_FACTOR.get(data.level, 1.0)

    overall_factor = fps_factor * style_factor * weapon_factor * level_factor

    def scope_table(base: float, extra_factor: float = 1.0) -> dict[str, int]:
        table: dict[str, int] = {}
        # TPP/FPP No Scope alohida hisoblanadi (scope multiplikatorisiz, faqat umumiy factor)
        table["TPP No Scope"] = round(_clamp(base * overall_factor * extra_factor))
        table["FPP No Scope"] = round(_clamp(base * overall_factor * extra_factor * 1.05))
        for scope_key in ALL_SCOPES:
            mult = SCOPE_MULTIPLIERS[scope_key]
            table[SCOPE_LABELS[scope_key]] = round(_clamp(base * overall_factor * extra_factor * mult))
        return table

    camera = scope_table(BASE_CAMERA_SENSITIVITY)
    ads = scope_table(BASE_ADS_SENSITIVITY)

    if data.gyroscope_enabled:
        gyro = scope_table(BASE_GYRO_SENSITIVITY, extra_factor=1.0)
        ads_gyro = scope_table(BASE_GYRO_SENSITIVITY, extra_factor=0.85)
    else:
        # Gyroscope o'chiq bo'lsa, bu jadvallar 0 qiymat bilan qaytariladi (ishlatilmaydi)
        gyro = {k: 0 for k in camera}
        ads_gyro = {k: 0 for k in camera}

    free_look = {
        "TPP Camera": round(_clamp(BASE_FREE_LOOK * style_factor)),
        "FPP Camera": round(_clamp(BASE_FREE_LOOK * style_factor * 1.05)),
        "Parachuting Camera": round(_clamp(BASE_FREE_LOOK * 1.10)),
    }

    return {
        "input": {
            "phone_model": data.phone_model,
            "fps": data.fps,
            "gyroscope_enabled": data.gyroscope_enabled,
            "play_style": data.play_style,
            "weapon": data.weapon,
            "scope": data.scope,
            "level": data.level,
        },
        "camera_sensitivity": camera,
        "ads_sensitivity": ads,
        "gyroscope_sensitivity": gyro,
        "ads_gyroscope_sensitivity": ads_gyro,
        "free_look": free_look,
    }


# ---------------------------------------------------------------------------
# AI Sensitivity Adjustment (foydalanuvchi feedbagiga qarab moslashtirish)
# ---------------------------------------------------------------------------

AIM_SPEED_ADJUST = {
    "too_fast": 0.90,   # "Juda tez" -> pasaytiramiz
    "too_slow": 1.12,   # "Juda sekin" -> oshiramiz
    "good": 1.00,
}

RECOIL_ADJUST = {
    "goes_up": 0.93,    # recoil yuqoriga ketsa -> ADS sensitivityni ehtiyotkorlik bilan pasaytiramiz
    "goes_down": 1.05,
    "good": 1.00,
}

SCOPE_ADJUST = {
    "shaky": 0.88,      # titraydi -> scope sensitivity pasayadi
    "slow": 1.10,
    "fast": 0.92,
    "good": 1.00,
}


def adjust_sensitivity(previous_result: dict, aim: str, recoil: str, scope_feedback: str) -> dict:
    """Oldingi natijaga feedback asosida ehtiyotkorlik bilan tuzatish kiritadi."""
    aim_mult = AIM_SPEED_ADJUST.get(aim, 1.0)
    recoil_mult = RECOIL_ADJUST.get(recoil, 1.0)
    scope_mult = SCOPE_ADJUST.get(scope_feedback, 1.0)

    def adjust_table(table: dict[str, int], mult: float) -> dict[str, int]:
        return {k: round(_clamp(v * mult)) if v else 0 for k, v in table.items()}

    new_result = {
        "input": previous_result["input"],
        # Umumiy aim tezligi camera sensitivitga, ADS ga esa recoil+scope ta'sir qiladi
        "camera_sensitivity": adjust_table(previous_result["camera_sensitivity"], aim_mult),
        "ads_sensitivity": adjust_table(previous_result["ads_sensitivity"], recoil_mult * scope_mult),
        "gyroscope_sensitivity": adjust_table(previous_result["gyroscope_sensitivity"], aim_mult),
        "ads_gyroscope_sensitivity": adjust_table(
            previous_result["ads_gyroscope_sensitivity"], recoil_mult * scope_mult
        ),
        "free_look": previous_result["free_look"],
    }
    return new_result
