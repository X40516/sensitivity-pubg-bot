"""
🧪 Sensitivity Test — foydalanuvchi feedbagi asosida AI adjustment.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.handlers.states import SensitivityFlow, TestFlow
from app.keyboards.callback_data import MenuCB, ResultCB, TestFeedbackCB
from app.keyboards.misc import test_aim_keyboard, test_recoil_keyboard, test_scope_keyboard
from app.keyboards.sensitivity_flow import result_actions_keyboard
from app.services.formatting import format_sensitivity_result
from app.services.i18n import t
from app.services.profile_service import add_history
from app.services.sensitivity_generator import adjust_sensitivity

router = Router(name="test")


async def _start_test(callback: CallbackQuery, state: FSMContext, locale: str) -> bool:
    """last_result mavjudligini tekshiradi va test oqimini boshlaydi. Bo'lmasa False qaytaradi."""
    data = await state.get_data()
    if not data.get("last_result"):
        await callback.answer(t("no_saved_profiles", locale), show_alert=True)
        return False
    await state.set_state(TestFlow.aim)
    await callback.message.edit_text(
        f"{t('test_intro', locale)}\n\n{t('ask_aim', locale)}", reply_markup=test_aim_keyboard(locale)
    )
    return True


@router.callback_query(SensitivityFlow.result, ResultCB.filter(F.action == "test"))
async def start_test_from_result(callback: CallbackQuery, state: FSMContext, locale: str) -> None:
    await _start_test(callback, state, locale)
    await callback.answer()


@router.callback_query(MenuCB.filter(F.action == "test"))
async def start_test_from_menu(callback: CallbackQuery, state: FSMContext, locale: str) -> None:
    started = await _start_test(callback, state, locale)
    if not started:
        from app.keyboards.main_menu import main_menu_keyboard

        await callback.message.edit_text(t("main_menu", locale), reply_markup=main_menu_keyboard(locale))
    await callback.answer()


@router.callback_query(TestFlow.aim, TestFeedbackCB.filter(F.category == "aim"))
async def receive_aim_feedback(
    callback: CallbackQuery, callback_data: TestFeedbackCB, state: FSMContext, locale: str
) -> None:
    await state.update_data(aim_feedback=callback_data.value)
    await state.set_state(TestFlow.recoil)
    await callback.message.edit_text(t("ask_recoil", locale), reply_markup=test_recoil_keyboard(locale))
    await callback.answer()


@router.callback_query(TestFlow.recoil, TestFeedbackCB.filter(F.category == "recoil"))
async def receive_recoil_feedback(
    callback: CallbackQuery, callback_data: TestFeedbackCB, state: FSMContext, locale: str
) -> None:
    await state.update_data(recoil_feedback=callback_data.value)
    await state.set_state(TestFlow.scope_feedback)
    await callback.message.edit_text(t("ask_scope_feedback", locale), reply_markup=test_scope_keyboard(locale))
    await callback.answer()


@router.callback_query(TestFlow.scope_feedback, TestFeedbackCB.filter(F.category == "scope"))
async def receive_scope_feedback(
    callback: CallbackQuery,
    callback_data: TestFeedbackCB,
    state: FSMContext,
    locale: str,
    session: AsyncSession,
    db_user: User,
) -> None:
    data = await state.get_data()
    previous_result = data["last_result"]
    new_result = adjust_sensitivity(
        previous_result,
        aim=data.get("aim_feedback", "good"),
        recoil=data.get("recoil_feedback", "good"),
        scope_feedback=callback_data.value,
    )
    await add_history(session, db_user.id, new_result["input"], new_result)

    await state.update_data(last_result=new_result)
    await state.set_state(SensitivityFlow.result)

    text = (
        f"{t('adjustment_result', locale)}\n\n"
        f"{format_sensitivity_result(new_result, locale)}"
    )
    await callback.message.edit_text(text, reply_markup=result_actions_keyboard(locale))
    await callback.answer()
