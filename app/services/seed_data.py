"""
Real, ommaviy manbalardan olingan pro o'yinchilar ma'lumotlarini bazaga
qo'shadigan seed skripti. FAQAT haqiqiy, manba ko'rsatilgan ma'lumotlar
qo'shiladi — hech qanday uydirma raqam yo'q.

Bu funksiya idempotent: bot qayta ishga tushirilganda ham, agar o'yinchi
allaqachon bazada bo'lsa, uni qayta qo'shmaydi va dublikat yaratmaydi.

Manbalar:
- NOVA Paraboy: https://en.esportsku.com/pubg-mobile-sensitivity-settings-nv-paraboy-version-pubg/
- NV Order: https://wargxp.com/esports/nv-order-sensitivity-settings-and-control-code/
- Levinho: https://sportskeeda.com/esports/pubg-mobile-levinho-s-control-setup-sensitivity-settings
- ZGOD: https://www.sportskeeda.com/esports/pubg-mobile-tsm-entity-zgod-s-controls-setup-sensitivity-settings
- BTR Zuxxy: https://sportskeeda.com/esports/pubg-mobile-btrxzuxxy-s-controls-setup-sensitivity-settings
- ScoutOP: https://sportskeeda.com/esports/pubg-mobile-scout-control-setup-sensitivity-settings
- Soul Regaltos: https://www.sportskeeda.com/esports/pubg-mobile-soul-regaltos-control-setup-sensitivity-settings
- BTR Luxxy: https://www.sportskeeda.com/esports/pubg-mobile-btr-luxxy-s-controls-setup-sensitivity-settings
- AGGRESSOR, EZ4BADBOY (O'zbekiston terma jamoalari, PMCO Central Asia / PMNC Uzbekistan
  rosterlari): https://liquipedia.net/pubgmobile/PUBG_Mobile_Super_League/Central_and_South_Asia/2025/Fall

Diqqat: bu ma'lumotlar uchinchi tomon (community/blog/wiki) manbalaridan olingan,
o'yinchilarning rasmiy/birinchi shaxs tasdiqlangan bayonoti emas. Shu sabab
verified=False qilib belgilangan — foydalanuvchi manba havolasi orqali
o'zi tekshirishi mumkin. AGGRESSOR va EZ4BADBOY uchun faqat jamoa/region
ma'lumoti tasdiqlangan (Liquipedia roster orqali) — ularning sensitivity
sozlamalari hech qanday ochiq manbada topilmagani uchun bo'sh (None) qoldirilgan,
bot bu holatda "sensitivity ma'lumoti topilmadi" deb to'g'ri ko'rsatadi.

TOP 10 tartibi haqida: `rank_position` maydoni rasmiy/tashqi reyting emas —
jamoalarning PUBG Mobile'dagi umumiy tanilganligi asosida tuzilgan ichki
kuratorlik tartibi (masalan, Nova Esports va Bigetron Esports xalqaro
turnirlarda ko'p yillik tarixga ega mashhur tashkilotlar). Bu haqiqiy
musobaqa natijalariga asoslangan rasmiy reyting emasligini unutmang.
"""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.pro_player_service import get_player_by_nickname
from app.database.models import ProPlayer, ProPlayerSensitivity

logger = logging.getLogger(__name__)


SEED_PLAYERS: list[dict] = [
    {
        "nickname": "Paraboy",
        "rank_position": 1,
        "team": "Nova Esports",
        "region": "China",
        "device": "iPhone 13 Pro Max",
        "fps": None,
        "gyroscope_enabled": True,
        "play_style": None,
        "source_url": "https://en.esportsku.com/pubg-mobile-sensitivity-settings-nv-paraboy-version-pubg/",
        "verified": False,
        "camera_sensitivity": {
            "TPP No Scope": 80,
            "FPP No Scope": 119,
            "Red Dot": 74,
            "2x": 76,
            "3x": 24,
            "4x": 24,
            "6x": 10,
            "8x": 9,
        },
        "ads_sensitivity": {
            "TPP No Scope": 79,
            "FPP No Scope": 119,
            "Red Dot": 1,
            "2x": 1,
            "3x": 1,
            "4x": 1,
            "6x": 1,
            "8x": 1,
        },
        "gyroscope_sensitivity": {
            "TPP No Scope": 230,
            "FPP No Scope": 230,
            "Red Dot": 185,
            "2x": 95,
            "3x": 170,
            "4x": 120,
            "6x": 100,
            "8x": 100,
        },
        "ads_gyroscope_sensitivity": {
            "TPP No Scope": 230,
            "FPP No Scope": 230,
            "Red Dot": 185,
            "2x": 120,
            "3x": 170,
            "4x": 120,
            "6x": 100,
            "8x": 100,
        },
    },
    {
        "nickname": "Order",
        "rank_position": 2,
        "team": "Nova Esports",
        "region": "China",
        "device": None,
        "fps": None,
        "gyroscope_enabled": True,
        "play_style": None,
        "source_url": "https://wargxp.com/esports/nv-order-sensitivity-settings-and-control-code/",
        "verified": False,
        "camera_sensitivity": {
            "TPP No Scope": 103,
            "FPP No Scope": 103,
            "Red Dot": 30,
            "2x": 17,
            "3x": 15,
            "4x": 10,
            "6x": 4,
            "8x": 3,
        },
        # Order ADS sensitivity sozlamalarini yopiq (private) qilib qo'ygan —
        # manbada bu qiymatlar mavjud emas, shuning uchun None qoldiramiz.
        "ads_sensitivity": None,
        "gyroscope_sensitivity": {
            "TPP No Scope": 350,
            "FPP No Scope": 350,
            "Red Dot": 280,
            "2x": 250,
            "3x": 200,
            "4x": 200,
            "6x": 80,
            "8x": 55,
        },
        # Order ADS Gyroscope sozlamalarini ham yopiq qilib qo'ygan.
        "ads_gyroscope_sensitivity": None,
    },
    {
        "nickname": "Levinho",
        "rank_position": 8,
        "team": None,
        "region": "Sweden",
        "device": "iPhone XS Max",
        "fps": None,
        "gyroscope_enabled": True,
        "play_style": None,
        "source_url": "https://sportskeeda.com/esports/pubg-mobile-levinho-s-control-setup-sensitivity-settings",
        "verified": False,
        "camera_sensitivity": {
            "TPP No Scope": 300,
            "FPP No Scope": 300,
            "Red Dot": 60,
            "2x": 36,
            "3x": 22,
            "4x": 17,
            "6x": 8,
            "8x": 8,
        },
        "ads_sensitivity": {
            "TPP No Scope": 300,
            "FPP No Scope": 120,
            "Red Dot": 60,
            "2x": 36,
            "3x": 22,
            "4x": 20,
            "6x": 12,
            "8x": 12,
        },
        "gyroscope_sensitivity": {
            "TPP No Scope": 300,
            "FPP No Scope": 300,
            "Red Dot": 300,
            "2x": 300,
            "3x": 150,
            "4x": 135,
            "6x": 57,
            "8x": 55,
        },
        # Manbada ADS Gyroscope alohida ko'rsatilmagan (faqat bitta umumiy
        # Gyroscope jadvali berilgan), shuning uchun uydirmaslik uchun None.
        "ads_gyroscope_sensitivity": None,
    },
    {
        "nickname": "ZGOD",
        "rank_position": 6,
        "team": "TSM-Entity",
        "region": "India",
        "device": None,
        "fps": None,
        "gyroscope_enabled": True,
        "play_style": None,
        "source_url": "https://www.sportskeeda.com/esports/pubg-mobile-tsm-entity-zgod-s-controls-setup-sensitivity-settings",
        "verified": False,
        "camera_sensitivity": {
            "TPP No Scope": 93,
            "FPP No Scope": 112,
            "Red Dot": 1,
            "2x": 1,
            "3x": 9,
            "4x": 9,
            "6x": 1,
            "8x": 1,
        },
        "ads_sensitivity": {
            "TPP No Scope": 104,
            "FPP No Scope": 110,
            "Red Dot": 1,
            "2x": 1,
            "3x": 1,
            "4x": 1,
            "6x": 1,
            "8x": 1,
        },
        "gyroscope_sensitivity": {
            "TPP No Scope": 300,
            "FPP No Scope": 300,
            "Red Dot": 272,
            "2x": 300,
            "3x": 175,
            "4x": 140,
            "6x": 55,
            "8x": 50,
        },
        "ads_gyroscope_sensitivity": None,
    },
    {
        "nickname": "Zuxxy",
        "rank_position": 3,
        "team": "Bigetron Esports",
        "region": "Indonesia",
        "device": None,
        "fps": None,
        "gyroscope_enabled": True,
        "play_style": None,
        "source_url": "https://sportskeeda.com/esports/pubg-mobile-btrxzuxxy-s-controls-setup-sensitivity-settings",
        "verified": False,
        "camera_sensitivity": {
            "TPP No Scope": 120,
            "FPP No Scope": 115,
            "Red Dot": 50,
            "2x": 35,
            "3x": 29,
            "4x": 20,
            "6x": 15,
            "8x": 12,
        },
        "ads_sensitivity": {
            "TPP No Scope": 120,
            "FPP No Scope": 115,
            "Red Dot": 88,
            "2x": 36,
            "3x": 30,
            "4x": 40,
            "6x": 30,
            "8x": 12,
        },
        "gyroscope_sensitivity": {
            "TPP No Scope": 300,
            "FPP No Scope": 300,
            "Red Dot": 300,
            "2x": 300,
            "3x": 165,
            "4x": 124,
            "6x": 60,
            "8x": 45,
        },
        "ads_gyroscope_sensitivity": None,
    },
    {
        "nickname": "Scout",
        "rank_position": 7,
        "team": "Orange Rock",
        "region": "India",
        "device": None,
        "fps": None,
        "gyroscope_enabled": True,
        "play_style": None,
        "source_url": "https://sportskeeda.com/esports/pubg-mobile-scout-control-setup-sensitivity-settings",
        "verified": False,
        "camera_sensitivity": {
            "TPP No Scope": 120,
            "FPP No Scope": 125,
            "Red Dot": 46,
            "2x": 46,
            "3x": 27,
            "4x": 17,
            "6x": 13,
            "8x": 10,
        },
        "ads_sensitivity": {
            "TPP No Scope": 135,
            "FPP No Scope": 134,
            "Red Dot": 60,
            "2x": 60,
            "3x": 40,
            "4x": 30,
            "6x": 13,
            "8x": 11,
        },
        "gyroscope_sensitivity": {
            "TPP No Scope": 220,
            "FPP No Scope": 220,
            "Red Dot": 300,
            "2x": 300,
            "3x": 240,
            "4x": 232,
            "6x": 64,
            "8x": 40,
        },
        "ads_gyroscope_sensitivity": None,
    },
    {
        "nickname": "Regaltos",
        "rank_position": 5,
        "team": "Team Soul",
        "region": "India",
        "device": None,
        "fps": None,
        # Manba: "non-gyro player, faqat scope-on holatida gyroscope ishlatadi"
        "gyroscope_enabled": False,
        "play_style": None,
        "source_url": "https://www.sportskeeda.com/esports/pubg-mobile-soul-regaltos-control-setup-sensitivity-settings",
        "verified": False,
        "camera_sensitivity": {
            "TPP No Scope": 90,
            "FPP No Scope": 92,
            "Red Dot": 29,
            "2x": 1,
            "3x": 9,
            "4x": 9,
            "6x": 6,
            "8x": 6,
        },
        "ads_sensitivity": {
            "TPP No Scope": 100,
            "FPP No Scope": 120,
            "Red Dot": 30,
            "2x": 2,
            "3x": 8,
            "4x": 8,
            "6x": 8,
            "8x": 6,
        },
        "gyroscope_sensitivity": {
            "TPP No Scope": 200,
            "FPP No Scope": 200,
            "Red Dot": 300,
            "2x": 300,
            "3x": 200,
            "4x": 100,
            "6x": 80,
            "8x": 70,
        },
        "ads_gyroscope_sensitivity": None,
    },
    {
        "nickname": "Luxxy",
        "rank_position": 4,
        "team": "Bigetron Esports",
        "region": "Indonesia",
        "device": None,
        "fps": None,
        # Manba: barcha gyroscope qiymatlari 1% — amalda non-gyro o'yinchi
        "gyroscope_enabled": False,
        "play_style": None,
        "source_url": "https://www.sportskeeda.com/esports/pubg-mobile-btr-luxxy-s-controls-setup-sensitivity-settings",
        "verified": False,
        "camera_sensitivity": {
            "TPP No Scope": 35,
            "FPP No Scope": 35,
            "Red Dot": 30,
            "2x": 24,
            "3x": 11,
            "4x": 8,
            "6x": 4,
            "8x": 3,
        },
        "ads_sensitivity": {
            "TPP No Scope": 35,
            "FPP No Scope": 35,
            "Red Dot": 34,
            "2x": 24,
            "3x": 19,
            "4x": 8,
            "6x": 8,
            "8x": 4,
        },
        "gyroscope_sensitivity": {
            "TPP No Scope": 1,
            "FPP No Scope": 1,
            "Red Dot": 1,
            "2x": 1,
            "3x": 1,
            "4x": 1,
            "6x": 1,
            "8x": 1,
        },
        "ads_gyroscope_sensitivity": None,
    },
    {
        # Liquipedia PMCO Central Asia / PMNC Uzbekistan roster'lariga ko'ra,
        # THE721 AGGRESSOR jamoasi o'zbek terma jamoasi sifatida qatnashgan.
        "nickname": "AGGRESSOR",
        "rank_position": 9,
        "team": "THE721 AGGRESSOR",
        "region": "Uzbekistan",
        "device": None,
        "fps": None,
        "gyroscope_enabled": None,
        "play_style": None,
        "source_url": "https://liquipedia.net/pubgmobile/PUBG_Mobile_Super_League/Central_and_South_Asia/2025/Fall",
        "verified": False,
        "camera_sensitivity": None,
        "ads_sensitivity": None,
        "gyroscope_sensitivity": None,
        "ads_gyroscope_sensitivity": None,
    },
    {
        "nickname": "EZ4BADBOY",
        "rank_position": 10,
        "team": "ARCRED",
        "region": "Uzbekistan",
        "device": None,
        "fps": None,
        "gyroscope_enabled": None,
        "play_style": None,
        "source_url": "https://liquipedia.net/pubgmobile/PUBG_Mobile_Super_League/Central_and_South_Asia/2025/Fall",
        "verified": False,
        "camera_sensitivity": None,
        "ads_sensitivity": None,
        "gyroscope_sensitivity": None,
        "ads_gyroscope_sensitivity": None,
    },
]


async def seed_verified_pro_players(session: AsyncSession) -> None:
    for data in SEED_PLAYERS:
        existing = await get_player_by_nickname(session, data["nickname"])
        if existing:
            # O'yinchi allaqachon mavjud — faqat rank_position'ni yangilaymiz
            # (agar seed ma'lumotida belgilangan bo'lsa), boshqa qo'lda
            # tahrirlangan maydonlarga tegmaymiz.
            new_rank = data.get("rank_position")
            if new_rank is not None and existing.rank_position != new_rank:
                existing.rank_position = new_rank
            continue

        player = ProPlayer(
            nickname=data["nickname"],
            team=data["team"],
            region=data["region"],
            device=data["device"],
            fps=data["fps"],
            gyroscope_enabled=data["gyroscope_enabled"],
            play_style=data["play_style"],
            rank_position=data.get("rank_position"),
        )
        session.add(player)
        await session.flush()

        sensitivity = ProPlayerSensitivity(
            player_id=player.id,
            camera_sensitivity=data["camera_sensitivity"],
            ads_sensitivity=data["ads_sensitivity"],
            gyroscope_sensitivity=data["gyroscope_sensitivity"],
            ads_gyroscope_sensitivity=data["ads_gyroscope_sensitivity"],
            source_url=data["source_url"],
            verified=data["verified"],
        )
        session.add(sensitivity)
        logger.info("Seed: pro player qo'shildi: %s", data["nickname"])

    await session.commit()
