# SENSITIVITY PUBG — Telegram Bot

PUBG Mobile o'yinchilari uchun sensitivity generatori. Telefon modeli, FPS,
Gyroscope, o'yin uslubi, qurol, scope va daraja asosida individual sensitivity
sozlamalarini hisoblab beradi.

## Texnologiyalar

- Python 3.11+
- [aiogram 3.x](https://docs.aiogram.dev/) — Telegram Bot framework
- PostgreSQL + SQLAlchemy 2.0 (async, `asyncpg`)
- Alembic — database migratsiyalari
- Docker / Railway / Render uchun tayyor

## Loyiha strukturasi

```
app/
  config.py              # .env dan sozlamalarni o'qish
  bot.py                 # Bot/Dispatcher yaratish, middleware ulash
  database/
    db.py                # SQLAlchemy engine/session
    models.py             # Barcha jadvallar (users, pro_players, va h.k.)
  keyboards/              # Inline keyboardlar va callback_data factory'lari
  handlers/                # Barcha bot oqimlari (sensitivity, admin, va h.k.)
  services/                # Biznes-logika: generator, i18n, DB service'lar
  locales/                 # uz.json, ru.json, en.json tarjimalari
  middlewares/             # DB session va user context middleware'lari
main.py                    # Ishga tushirish nuqtasi (polling/webhook)
alembic/                   # Migratsiya fayllari
```

## O'rnatish (lokal, polling rejimida)

1. Repositoryni klonlang va papkaga o'ting.

2. Virtual environment yarating:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. `.env.example` faylidan nusxa oling va to'ldiring:

   ```bash
   cp .env.example .env
   ```

   - `BOT_TOKEN` — @BotFather dan olingan token
   - `DATABASE_URL` — PostgreSQL ulanish manzili, masalan:
     `postgresql://user:password@localhost:5432/sensitivity_pubg`
   - `ADMIN_IDS` — admin bo'ladigan Telegram user ID'lar (vergul bilan)

4. PostgreSQL ni ishga tushiring (lokal yoki Docker orqali):

   ```bash
   docker compose up -d db
   ```

5. Migratsiyalarni qo'llang:

   ```bash
   alembic revision --autogenerate -m "init"
   alembic upgrade head
   ```

   > Eslatma: `main.py` ishga tushganda jadvallarni avtomatik yaratadi
   > (`init_models()`), lekin **production**da faqat Alembic migratsiyalaridan
   > foydalanish tavsiya etiladi — bu jadval o'zgarishlarini kuzatish va
   > xavfsiz yangilash imkonini beradi.

6. Botni ishga tushiring:

   ```bash
   python main.py
   ```

## Docker orqali ishga tushirish

```bash
docker compose up --build
```

Bu `bot` va `db` (PostgreSQL) konteynerlarini birga ko'taradi.

## Railway / Render ga joylashtirish

1. Loyihani GitHub repositoryga push qiling.
2. Railway yoki Render'da yangi loyiha yarating va reponi ulang — Dockerfile
   avtomatik aniqlanadi.
3. Quyidagi environment variable'larni platforma sozlamalarida kiriting
   (hech qachon kodga yozmang):
   - `BOT_TOKEN`
   - `DATABASE_URL` (platforma taqdim etgan PostgreSQL manzili)
   - `ADMIN_IDS`
   - Agar webhook rejimini ishlatmoqchi bo'lsangiz:
     `USE_WEBHOOK=true`, `WEBHOOK_BASE_URL=https://<app-domain>`
4. Deploy qilingandan so'ng migratsiyalarni ishga tushiring:
   ```bash
   alembic upgrade head
   ```

## Admin panel

Admin (ADMIN_IDS ro'yxatidagi foydalanuvchi) botga `/admin` buyrug'ini yuborib
panelga kiradi. U yerdan:

- 📊 Statistika ko'rish (real DB so'rovlari asosida)
- 🚫 / ✅ Foydalanuvchini ban qilish / blokdan chiqarish
- 📢 Barcha foydalanuvchilarga xabar yuborish (broadcast)
- 🏆 Pro Players qo'shish / o'chirish

## Pro Players haqida muhim eslatma

`Pro Players` bo'limidagi ma'lumotlar — real, manbali (sourced) ma'lumotlar
bo'lishi shart. Bot hech qanday sun'iy/uydirma pro o'yinchi yoki sensitivity
qiymatini o'zi generatsiya qilmaydi. Bu ma'lumotlarni faqat admin panel orqali
qo'lda kiritish mumkin, har bir yozuv uchun manba (`source`) va
tasdiqlanganlik holati (`verified`/`unverified`) saqlanadi. Agar biror
o'yinchi uchun sensitivity ma'lumoti kiritilmagan bo'lsa, foydalanuvchiga
"❌ Sensitivity ma'lumoti topilmadi" deb ko'rsatiladi.

`🎯 Sensitivity yaratish`, `🔫 Qurol bo'yicha` va `🔥 Pro Presetlar`
bo'limlaridagi qiymatlar esa FPS/gyroscope/o'yin uslubi/qurol/scope asosidagi
**hisoblangan tavsiyalar** — bular pro o'yinchining haqiqiy sozlamalari
sifatida taqdim etilmaydi.

## Xavfsizlik

- `BOT_TOKEN`, `DATABASE_URL` va boshqa maxfiy ma'lumotlar faqat `.env` orqali
  o'qiladi, kodga yozilmagan.
- Admin funksiyalari faqat `ADMIN_IDS` ro'yxatidagi Telegram ID'lar uchun
  ochiq — har bir admin handler `is_admin` tekshiruvidan o'tadi.
- Barcha DB so'rovlar SQLAlchemy ORM orqali parametrlashtirilgan (SQL
  injectiondan himoyalangan).
- Broadcast funksiyasida oddiy rate-limiting (har xabar orasida kichik
  kutish) qo'shilgan.

## Kengaytirish

Yangi funksiya qo'shish uchun:

- **Yangi til**: `app/locales/` ga yangi `<kod>.json` qo'shing va
  `app/services/i18n.py` dagi `SUPPORTED_LOCALES` ro'yxatiga kiriting.
- **Yangi qurol/telefon**: `app/keyboards/sensitivity_flow.py` dagi
  `WEAPONS` / `PHONE_BRANDS` ro'yxatlariga qo'shing.
- **Yangi preset**: `app/handlers/weapon_presets.py` dagi `PRESET_DEFAULTS`
  ga qo'shing va tegishli tarjima kalitini (`preset_<name>`) barcha locale
  fayllariga kiriting.
- **Yangi admin funksiya**: `app/handlers/admin.py` yoki
  `app/handlers/admin_pro_players.py` ga yangi handler qo'shing.

## Litsenziya

Ushbu loyiha buyurtma asosida yaratilgan texnik topshiriqqa muvofiq ishlab
chiqilgan.
