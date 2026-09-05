"""
Barcha FSM (Finite State Machine) holatlari.
"""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class SensitivityFlow(StatesGroup):
    phone_brand = State()
    phone_model_text = State()
    fps = State()
    gyroscope = State()
    play_style = State()
    weapon = State()
    scope = State()
    level = State()
    result = State()
    saving_name = State()


class TestFlow(StatesGroup):
    aim = State()
    recoil = State()
    scope_feedback = State()


class SavedProfileFlow(StatesGroup):
    renaming = State()


class MyPhoneFlow(StatesGroup):
    phone_brand = State()
    phone_model_text = State()


class AdminBroadcast(StatesGroup):
    waiting_text = State()
    waiting_confirm = State()


class AdminUserAction(StatesGroup):
    waiting_user_id_ban = State()
    waiting_user_id_unban = State()


class AdminProPlayerFlow(StatesGroup):
    nickname = State()
    team = State()
    region = State()
    device = State()
    fps = State()
    gyro = State()
    style = State()
    source = State()
    verified = State()
    delete_nickname = State()
