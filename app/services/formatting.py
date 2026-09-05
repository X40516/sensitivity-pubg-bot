"""
Sensitivity natijalarini chiroyli matn ko'rinishida formatlash.
"""
from __future__ import annotations

from app.services.i18n import t


def _format_table(table: dict[str, int]) -> str:
    return "\n".join(f"{label}: {value}%" for label, value in table.items())


def format_sensitivity_result(result: dict, locale: str) -> str:
    lines = [
        f"<b>{t('result_camera', locale)}</b>",
        _format_table(result["camera_sensitivity"]),
        "",
        f"<b>{t('result_ads', locale)}</b>",
        _format_table(result["ads_sensitivity"]),
    ]

    if result["input"].get("gyroscope_enabled"):
        lines += [
            "",
            f"<b>{t('result_gyro', locale)}</b>",
            _format_table(result["gyroscope_sensitivity"]),
            "",
            f"<b>{t('result_ads_gyro', locale)}</b>",
            _format_table(result["ads_gyroscope_sensitivity"]),
        ]

    lines += [
        "",
        f"<b>{t('result_free_look', locale)}</b>",
        _format_table(result["free_look"]),
    ]
    return "\n".join(lines)


def format_plain_copy_text(result: dict) -> str:
    """Copy tugmasi uchun formatsiz (plain) matn, oson nusxalash uchun."""
    lines = ["CAMERA SENSITIVITY"]
    lines += [f"{k}: {v}%" for k, v in result["camera_sensitivity"].items()]
    lines.append("")
    lines.append("ADS SENSITIVITY")
    lines += [f"{k}: {v}%" for k, v in result["ads_sensitivity"].items()]
    if result["input"].get("gyroscope_enabled"):
        lines.append("")
        lines.append("GYROSCOPE")
        lines += [f"{k}: {v}%" for k, v in result["gyroscope_sensitivity"].items()]
        lines.append("")
        lines.append("ADS GYROSCOPE")
        lines += [f"{k}: {v}%" for k, v in result["ads_gyroscope_sensitivity"].items()]
    lines.append("")
    lines.append("FREE LOOK")
    lines += [f"{k}: {v}%" for k, v in result["free_look"].items()]
    return "\n".join(lines)
