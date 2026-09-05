"""
Barcha callback_data factory'lari (aiogram CallbackData asosida).
"""
from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class MenuCB(CallbackData, prefix="menu"):
    action: str  # create_sensitivity | pro_players | my_phone | by_weapon | pro_presets |
    # test | saved | referral | premium | language | help | home | back


class FlowCB(CallbackData, prefix="flow"):
    step: str  # phone_brand | fps | gyro | style | weapon | scope | level
    value: str


class ResultCB(CallbackData, prefix="result"):
    action: str  # copy | save | regenerate | test | send_friend


class SavedProfileCB(CallbackData, prefix="saved"):
    action: str  # view | rename | delete | confirm_delete | cancel_delete | list
    profile_id: int = 0


class TestFeedbackCB(CallbackData, prefix="test"):
    category: str  # aim | recoil | scope
    value: str


class ProPlayerCB(CallbackData, prefix="pro"):
    action: str  # list | top10 | view | filter
    player_id: int = 0
    page: int = 0


class ProFilterCB(CallbackData, prefix="profilter"):
    field: str  # region | team | device | fps | gyro | style
    value: str = ""


class WeaponCB(CallbackData, prefix="weapon"):
    name: str


class PresetCB(CallbackData, prefix="preset"):
    name: str


class PhoneBrandCB(CallbackData, prefix="phonebrand"):
    brand: str


class LanguageCB(CallbackData, prefix="lang"):
    code: str


class ConfirmCB(CallbackData, prefix="confirm"):
    action: str  # yes | no
    context: str  # what is being confirmed
    ref_id: int = 0


class AdminCB(CallbackData, prefix="admin"):
    action: str


class AdminProPlayerCB(CallbackData, prefix="adminpro"):
    action: str  # add | edit | delete | search | list
    player_id: int = 0
