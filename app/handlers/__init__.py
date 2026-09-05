"""
Barcha routerlarni bitta joyda ro'yxatdan o'tkazish.
"""
from __future__ import annotations

from aiogram import Dispatcher

from app.handlers import (
    admin,
    admin_pro_players,
    my_phone,
    pro_players,
    referral_premium,
    saved,
    sensitivity,
    start,
    test,
    weapon_presets,
)


def register_all_routers(dp: Dispatcher) -> None:
    # Tartib muhim: aniqroq (state-bog'liq) handlerlar avval, umumiy menyu handlerlari keyin
    # bo'lishi kerak emas — aiogram Router state filtri orqali avtomatik farqlaydi,
    # lekin admin routerlarni oldinroq qo'yish callback nomlari to'qnashmasligini ta'minlaydi.
    dp.include_router(admin.router)
    dp.include_router(admin_pro_players.router)
    dp.include_router(start.router)
    dp.include_router(sensitivity.router)
    dp.include_router(test.router)
    dp.include_router(saved.router)
    dp.include_router(my_phone.router)
    dp.include_router(weapon_presets.router)
    dp.include_router(referral_premium.router)
    dp.include_router(pro_players.router)
