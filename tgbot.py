import asyncio
import logging
from datetime import datetime, timedelta

import aiosqlite

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties


# =========================
# CONFIG
# =========================

BOT_TOKEN = "8339719049:AAFbNPkZFHECNHLZP0QHmy5hjRacKrDwnZg"
ADMIN_ID = 6764552282
CHANNEL_ID = -1002025883162  # обязательно -100...

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# =========================
# DATA
# =========================

SUBSCRIPTIONS = {
    "vip_month": {
        "name_ru": "VIP на 1 месяц",
        "name_en": "VIP month",
        "days": 30,
        "price_ru": "1500₽",
        "price_en": "$18",
    },
    "vip_forever": {
        "name_ru": "VIP навсегда",
        "name_en": "VIP forever",
        "days": 3650,
        "price_ru": "10000₽",
        "price_en": "$120",
    },
}

PAYMENT_DETAILS = {
    "card": {
        "ru": "Перевод на карту РФ:\n2200271158995556",
        "en": "Card transfer:\n2200271158995556",
    },
    "usdt": {
        "ru": "USDT TRC20\nTS5wFQBgRnPfVwM4GBuY5EArXFhNW4WZxi",
        "en": "USDT TRC20\nTS5wFQBgRnPfVwM4GBuY5EArXFhNW4WZxi",
    },
    "btc": {
        "ru": "Bitcoin\nbc1qcsnvksmv4xh39c8v48n86elkznknlstmzcp6ex",
        "en": "Bitcoin\nbc1qcsnvksmv4xh39c8v48n86elkznknlstmzcp6ex",
    },
    "paypal": {
        "ru": "PayPal\nplesovskihdenis466@gmail.com",
        "en": "PayPal\nplesovskihdenis466@gmail.com",
    },
}

TEXT = {
    "ru": {
        "choose_lang": "Выберите язык",
        "main_menu": "Главное меню",
        "user_menu": "Меню пользователя",
        "choose_sub": "Выберите подписку",
        "choose_pay": "Выберите способ оплаты",
        "send_receipt": "После оплаты отправьте квитанцию",
        "receipt_sent": "Квитанция отправлена на проверку",
        "approved": "✅ Оплата подтверждена!\nВот ваша ссылка:",
        "rejected": "❌ Оплата отклонена",
        "banned_user": "⛔ Вы заблокированы за спам или фейковые квитанции.",
        "check_sub_none": "У вас нет активной подписки.",
        "check_sub_ok": "Ваша подписка: <b>{sub}</b>\nДействует до: <b>{expire}</b>\nОсталось дней: <b>{days}</b>",
        "expiring_soon": "⚠️ Ваша подписка заканчивается завтра.",
        "expired": "❌ Ваша подписка закончилась.",
        "renew_hint": "Чтобы продлить подписку, выберите тариф заново.",
        "back": "⬅️ Назад",
        "home": "🏠 Главное меню",
        "user_check": "📌 Проверить подписку",
        "buy_sub": "💎 Купить подписку",
        "admin_panel": "🛠 Админ-панель",
        "admin_users": "📋 Пользователи",
        "admin_expiring": "⏳ Скоро истекают",
        "admin_give": "➕ Выдать VIP",
        "admin_broadcast": "📨 Рассылка",
        "admin_banned": "⛔ Бан-лист",
        "admin_menu_title": "Админ-панель",
        "send_user_id": "Отправьте ID пользователя",
        "send_days": "Отправьте количество дней",
        "vip_granted": "🎁 Вам выдан VIP на {days} дней.",
        "done": "Готово",
        "broadcast_text": "Отправьте текст рассылки",
        "broadcast_done": "Рассылка отправлена",
        "unknown_sub": "❌ Такой подписки нет",
        "invite_error": "❌ Не удалось создать ссылку. Проверьте CHANNEL_ID и права бота в канале.",
        "restart_flow": "Сессия сброшена. Нажмите /start",
        "new_payment": "🧾 НОВАЯ ОПЛАТА\n\nUser ID: <b>{uid}</b>\nUsername: @{username}\nПодписка: <b>{sub}</b>\nОплата: <b>{pay}</b>",
        "users_empty": "Список пользователей пуст.",
        "expiring_empty": "Нет подписок, которые скоро истекают.",
        "banned_empty": "Бан-лист пуст.",
        "banned_notice": "❌ Вы заблокированы и не можете пользоваться ботом.",
        "ban_done": "Пользователь заблокирован.",
        "unban_usage": "Использование: /unban USER_ID",
        "unban_done": "✅ Пользователь {uid} разблокирован.",
        "id_must_be_number": "ID должен быть числом",
        "days_must_be_number": "Количество дней должно быть числом",
        "user_flow_not_found": "Не найдена сессия пользователя",
    },
    "en": {
        "choose_lang": "Choose language",
        "main_menu": "Main menu",
        "user_menu": "User menu",
        "choose_sub": "Choose subscription",
        "choose_pay": "Choose payment method",
        "send_receipt": "After payment send receipt",
        "receipt_sent": "Receipt sent for review",
        "approved": "✅ Payment approved!\nHere is your link:",
        "rejected": "❌ Payment rejected",
        "banned_user": "⛔ You are banned for spam or fake receipts.",
        "check_sub_none": "You do not have an active subscription.",
        "check_sub_ok": "Your subscription: <b>{sub}</b>\nValid until: <b>{expire}</b>\nDays left: <b>{days}</b>",
        "expiring_soon": "⚠️ Your subscription expires tomorrow.",
        "expired": "❌ Your subscription has expired.",
        "renew_hint": "To renew, choose a plan again.",
        "back": "⬅️ Back",
        "home": "🏠 Main menu",
        "user_check": "📌 Check subscription",
        "buy_sub": "💎 Buy subscription",
        "admin_panel": "🛠 Admin panel",
        "admin_users": "📋 Users",
        "admin_expiring": "⏳ Expiring soon",
        "admin_give": "➕ Give VIP",
        "admin_broadcast": "📨 Broadcast",
        "admin_banned": "⛔ Banned users",
        "admin_menu_title": "Admin panel",
        "send_user_id": "Send user ID",
        "send_days": "Send number of days",
        "vip_granted": "🎁 VIP granted for {days} days.",
        "done": "Done",
        "broadcast_text": "Send broadcast text",
        "broadcast_done": "Broadcast sent",
        "unknown_sub": "❌ Unknown subscription",
        "invite_error": "❌ Failed to create invite link. Check CHANNEL_ID and bot rights in the channel.",
        "restart_flow": "Session reset. Press /start",
        "new_payment": "🧾 NEW PAYMENT\n\nUser ID: <b>{uid}</b>\nUsername: @{username}\nSubscription: <b>{sub}</b>\nPayment: <b>{pay}</b>",
        "users_empty": "Users list is empty.",
        "expiring_empty": "No subscriptions expiring soon.",
        "banned_empty": "Ban list is empty.",
        "banned_notice": "❌ You are banned and cannot use this bot.",
        "ban_done": "User banned.",
        "unban_usage": "Usage: /unban USER_ID",
        "unban_done": "✅ User {uid} unbanned.",
        "id_must_be_number": "ID must be a number",
        "days_must_be_number": "Days must be a number",
        "user_flow_not_found": "User session not found",
    },
}

# =========================
# STATE
# =========================

temp_users = {}
admin_state = {
    "mode": None,
    "target_user_id": None,
}

# =========================
# HELPERS
# =========================

def get_user_lang(user_id: int) -> str:
    return temp_users.get(user_id, {}).get("lang", "ru")

def format_sub_name(sub_key: str, lang: str) -> str:
    if sub_key in SUBSCRIPTIONS:
        return SUBSCRIPTIONS[sub_key]["name_ru"] if lang == "ru" else SUBSCRIPTIONS[sub_key]["name_en"]
    return sub_key

async def is_banned(user_id: int) -> bool:
    async with aiosqlite.connect("db.db") as db:
        async with db.execute(
            "SELECT 1 FROM banned_users WHERE user_id=?",
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row is not None

def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
    ]])

def user_main_kb(lang: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=TEXT[lang]["buy_sub"], callback_data="user_buy")],
        [InlineKeyboardButton(text=TEXT[lang]["user_check"], callback_data="user_check_sub")],
    ]
    if is_admin:
        rows.append([InlineKeyboardButton(text=TEXT[lang]["admin_panel"], callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def subscriptions_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{SUBSCRIPTIONS['vip_month']['name_ru'] if lang == 'ru' else SUBSCRIPTIONS['vip_month']['name_en']} — "
                 f"{SUBSCRIPTIONS['vip_month']['price_ru'] if lang == 'ru' else SUBSCRIPTIONS['vip_month']['price_en']}",
            callback_data="sub_vip_month"
        )],
        [InlineKeyboardButton(
            text=f"{SUBSCRIPTIONS['vip_forever']['name_ru'] if lang == 'ru' else SUBSCRIPTIONS['vip_forever']['name_en']} — "
                 f"{SUBSCRIPTIONS['vip_forever']['price_ru'] if lang == 'ru' else SUBSCRIPTIONS['vip_forever']['price_en']}",
            callback_data="sub_vip_forever"
        )],
        [
            InlineKeyboardButton(text=TEXT[lang]["back"], callback_data="back_user_main"),
            InlineKeyboardButton(text=TEXT[lang]["home"], callback_data="home"),
        ]
    ])

def payment_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="card", callback_data="pay_card")],
        [InlineKeyboardButton(text="USDT", callback_data="pay_usdt")],
        [InlineKeyboardButton(text="BTC", callback_data="pay_btc")],
        [InlineKeyboardButton(text="PayPal", callback_data="pay_paypal")],
        [
            InlineKeyboardButton(text=TEXT[lang]["back"], callback_data="back_to_subs"),
            InlineKeyboardButton(text=TEXT[lang]["home"], callback_data="home"),
        ]
    ])

def payment_back_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=TEXT[lang]["back"], callback_data="back_to_payments"),
        InlineKeyboardButton(text=TEXT[lang]["home"], callback_data="home"),
    ]])

def admin_main_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXT[lang]["admin_users"], callback_data="admin_users")],
        [InlineKeyboardButton(text=TEXT[lang]["admin_expiring"], callback_data="admin_expiring")],
        [InlineKeyboardButton(text=TEXT[lang]["admin_give"], callback_data="admin_give")],
        [InlineKeyboardButton(text=TEXT[lang]["admin_broadcast"], callback_data="admin_broadcast")],
        [InlineKeyboardButton(text=TEXT[lang]["admin_banned"], callback_data="admin_banned")],
        [
            InlineKeyboardButton(text=TEXT[lang]["back"], callback_data="back_user_main"),
            InlineKeyboardButton(text=TEXT[lang]["home"], callback_data="home"),
        ]
    ])

def admin_back_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=TEXT[lang]["back"], callback_data="admin_main"),
        InlineKeyboardButton(text=TEXT[lang]["home"], callback_data="home"),
    ]])

async def show_main_menu(target, user_id: int):
    lang = get_user_lang(user_id)
    is_admin = user_id == ADMIN_ID
    text = TEXT[lang]["main_menu"] if is_admin else TEXT[lang]["user_menu"]
    kb = user_main_kb(lang, is_admin=is_admin)

    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb)
    else:
        await target.message.edit_text(text, reply_markup=kb)

async def get_subscription_info(user_id: int):
    async with aiosqlite.connect("db.db") as db:
        async with db.execute(
            "SELECT user_id, lang, sub, expire FROM users WHERE user_id=?",
            (user_id,)
        ) as cur:
            return await cur.fetchone()

# =========================
# DB
# =========================

async def init_db():
    async with aiosqlite.connect("db.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            lang TEXT,
            sub TEXT,
            expire TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS banned_users(
            user_id INTEGER PRIMARY KEY,
            reason TEXT,
            created_at TEXT
        )
        """)
        await db.commit()

# =========================
# START
# =========================

@dp.message(F.text == "/start")
async def start(message: Message):
    if await is_banned(message.from_user.id):
        await message.answer(TEXT["ru"]["banned_notice"])
        return

    admin_state["mode"] = None
    admin_state["target_user_id"] = None
    await message.answer("Choose language / Выберите язык", reply_markup=lang_kb())

# =========================
# LANGUAGE
# =========================

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    if await is_banned(call.from_user.id):
        await call.answer(TEXT["ru"]["banned_notice"], show_alert=True)
        return

    lang = call.data.split("_", 1)[1]
    temp_users.setdefault(call.from_user.id, {})
    temp_users[call.from_user.id]["lang"] = lang
    await show_main_menu(call, call.from_user.id)

# =========================
# HOME / MAIN
# =========================

@dp.callback_query(F.data == "home")
async def home(call: CallbackQuery):
    if await is_banned(call.from_user.id):
        await call.answer(TEXT["ru"]["banned_notice"], show_alert=True)
        return

    admin_state["mode"] = None
    admin_state["target_user_id"] = None
    await show_main_menu(call, call.from_user.id)

@dp.callback_query(F.data == "back_user_main")
async def back_user_main(call: CallbackQuery):
    if await is_banned(call.from_user.id):
        await call.answer(TEXT["ru"]["banned_notice"], show_alert=True)
        return
    await show_main_menu(call, call.from_user.id)

# =========================
# USER MENU
# =========================

@dp.callback_query(F.data == "user_buy")
async def user_buy(call: CallbackQuery):
    if await is_banned(call.from_user.id):
        await call.answer(TEXT["ru"]["banned_notice"], show_alert=True)
        return

    lang = get_user_lang(call.from_user.id)
    await call.message.edit_text(TEXT[lang]["choose_sub"], reply_markup=subscriptions_kb(lang))

@dp.callback_query(F.data == "user_check_sub")
async def user_check_sub(call: CallbackQuery):
    if await is_banned(call.from_user.id):
        await call.answer(TEXT["ru"]["banned_notice"], show_alert=True)
        return

    lang = get_user_lang(call.from_user.id)
    row = await get_subscription_info(call.from_user.id)

    if not row:
        await call.message.edit_text(
            TEXT[lang]["check_sub_none"],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=TEXT[lang]["back"], callback_data="back_user_main"),
                InlineKeyboardButton(text=TEXT[lang]["home"], callback_data="home"),
            ]])
        )
        return

    _, _, sub_key, expire_str = row
    expire_dt = datetime.fromisoformat(expire_str)
    days_left = max((expire_dt - datetime.now()).days, 0)

    await call.message.edit_text(
        TEXT[lang]["check_sub_ok"].format(
            sub=format_sub_name(sub_key, lang),
            expire=expire_dt.strftime("%Y-%m-%d %H:%M"),
            days=days_left,
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=TEXT[lang]["back"], callback_data="back_user_main"),
            InlineKeyboardButton(text=TEXT[lang]["home"], callback_data="home"),
        ]])
    )

# =========================
# SUBSCRIPTIONS
# =========================

@dp.callback_query(F.data == "back_to_subs")
async def back_to_subs(call: CallbackQuery):
    if await is_banned(call.from_user.id):
        await call.answer(TEXT["ru"]["banned_notice"], show_alert=True)
        return

    lang = get_user_lang(call.from_user.id)
    await call.message.edit_text(TEXT[lang]["choose_sub"], reply_markup=subscriptions_kb(lang))

@dp.callback_query(F.data.startswith("sub_"))
async def choose_sub(call: CallbackQuery):
    if await is_banned(call.from_user.id):
        await call.answer(TEXT["ru"]["banned_notice"], show_alert=True)
        return

    sub_key = call.data.removeprefix("sub_").strip()
    lang = get_user_lang(call.from_user.id)

    if sub_key not in SUBSCRIPTIONS:
        await call.answer(TEXT[lang]["unknown_sub"], show_alert=True)
        return

    temp_users.setdefault(call.from_user.id, {})
    temp_users[call.from_user.id]["sub"] = sub_key

    await call.message.edit_text(TEXT[lang]["choose_pay"], reply_markup=payment_kb(lang))

# =========================
# PAYMENTS
# =========================

@dp.callback_query(F.data == "back_to_payments")
async def back_to_payments(call: CallbackQuery):
    if await is_banned(call.from_user.id):
        await call.answer(TEXT["ru"]["banned_notice"], show_alert=True)
        return

    lang = get_user_lang(call.from_user.id)
    await call.message.edit_text(TEXT[lang]["choose_pay"], reply_markup=payment_kb(lang))

@dp.callback_query(F.data.startswith("pay_"))
async def choose_payment(call: CallbackQuery):
    if await is_banned(call.from_user.id):
        await call.answer(TEXT["ru"]["banned_notice"], show_alert=True)
        return

    method = call.data.split("_", 1)[1]
    lang = get_user_lang(call.from_user.id)

    if "sub" not in temp_users.get(call.from_user.id, {}):
        await call.message.answer(TEXT[lang]["restart_flow"])
        return

    temp_users[call.from_user.id]["pay"] = method

    await call.message.answer(
        PAYMENT_DETAILS[method][lang] + "\n\n" + TEXT[lang]["send_receipt"],
        reply_markup=payment_back_kb(lang)
    )

# =========================
# RECEIPTS
# =========================

@dp.message(F.photo | F.document)
async def receipt(message: Message):
    uid = message.from_user.id

    if await is_banned(uid):
        return

    lang = get_user_lang(uid)

    if uid not in temp_users or "sub" not in temp_users[uid] or "pay" not in temp_users[uid]:
        await message.answer(TEXT[lang]["restart_flow"])
        return

    data = temp_users[uid]
    username = message.from_user.username or "no_username"

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Approve", callback_data=f"ok_{uid}"),
        InlineKeyboardButton(text="❌ Reject", callback_data=f"no_{uid}"),
        InlineKeyboardButton(text="⛔ Ban", callback_data=f"ban_{uid}"),
    ]])

    sub_name = format_sub_name(data["sub"], "en")

    await bot.send_message(
        ADMIN_ID,
        TEXT["en"]["new_payment"].format(
            uid=uid,
            username=username,
            sub=sub_name,
            pay=data["pay"]
        ),
        reply_markup=admin_kb
    )

    await message.forward(ADMIN_ID)
    await message.answer(TEXT[lang]["receipt_sent"])

# =========================
# APPROVE / REJECT / BAN
# =========================

@dp.callback_query(F.data.startswith("ok_"))
async def approve(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_", 1)[1])
    data = temp_users.get(uid)
    admin_lang = get_user_lang(ADMIN_ID)

    if not data or "sub" not in data or "lang" not in data:
        await call.answer(TEXT[admin_lang]["user_flow_not_found"], show_alert=True)
        return

    sub_key = data["sub"]
    days = SUBSCRIPTIONS[sub_key]["days"]
    expire = datetime.now() + timedelta(days=days)

    try:
        link = await bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            member_limit=1,
            expire_date=datetime.now() + timedelta(minutes=30)
        )
    except Exception:
        await call.message.answer(TEXT[admin_lang]["invite_error"])
        return

    await bot.send_message(
        uid,
        TEXT[data["lang"]]["approved"] + "\n" + link.invite_link
    )

    async with aiosqlite.connect("db.db") as db:
        await db.execute("""
        INSERT OR REPLACE INTO users(user_id, lang, sub, expire)
        VALUES (?, ?, ?, ?)
        """, (uid, data["lang"], sub_key, expire.isoformat()))
        await db.commit()

    temp_users.pop(uid, None)
    await call.answer("Approved")

@dp.callback_query(F.data.startswith("no_"))
async def reject(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_", 1)[1])
    user_lang = get_user_lang(uid)
    await bot.send_message(uid, TEXT[user_lang]["rejected"])
    temp_users.pop(uid, None)
    await call.answer("Rejected")

@dp.callback_query(F.data.startswith("ban_"))
async def ban_user(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_", 1)[1])
    admin_lang = get_user_lang(ADMIN_ID)

    async with aiosqlite.connect("db.db") as db:
        await db.execute("""
        INSERT OR REPLACE INTO banned_users(user_id, reason, created_at)
        VALUES (?, ?, ?)
        """, (uid, "spam_or_fake_receipt", datetime.now().isoformat()))
        await db.execute("DELETE FROM users WHERE user_id=?", (uid,))
        await db.commit()

    temp_users.pop(uid, None)

    try:
        await bot.send_message(uid, TEXT[get_user_lang(uid)]["banned_user"])
    except Exception:
        pass

    try:
        await bot.ban_chat_member(CHANNEL_ID, uid)
        await bot.unban_chat_member(CHANNEL_ID, uid)
    except Exception:
        pass

    await call.answer(TEXT[admin_lang]["ban_done"])
    await call.message.edit_text(f"⛔ User {uid} banned")

@dp.message(F.text.startswith("/unban "))
async def unban_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    lang = get_user_lang(message.from_user.id)
    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer(TEXT[lang]["unban_usage"])
        return

    uid = int(parts[1])

    async with aiosqlite.connect("db.db") as db:
        await db.execute("DELETE FROM banned_users WHERE user_id=?", (uid,))
        await db.commit()

    await message.answer(TEXT[lang]["unban_done"].format(uid=uid))

# =========================
# ADMIN PANEL
# =========================

@dp.callback_query(F.data == "admin_main")
async def admin_main(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    lang = get_user_lang(call.from_user.id)
    admin_state["mode"] = None
    admin_state["target_user_id"] = None
    await call.message.edit_text(TEXT[lang]["admin_menu_title"], reply_markup=admin_main_kb(lang))

@dp.callback_query(F.data == "admin_users")
async def admin_users(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    lang = get_user_lang(call.from_user.id)

    async with aiosqlite.connect("db.db") as db:
        async with db.execute("SELECT user_id, lang, sub, expire FROM users ORDER BY expire ASC") as cur:
            rows = await cur.fetchall()

    if not rows:
        await call.message.edit_text(TEXT[lang]["users_empty"], reply_markup=admin_back_kb(lang))
        return

    text = "📋 USERS\n\n"
    for uid, row_lang, sub, exp in rows[:30]:
        text += f"ID: <b>{uid}</b>\n"
        text += f"Lang: {row_lang}\n"
        text += f"Sub: {sub}\n"
        text += f"Expire: {exp}\n\n"

    await call.message.edit_text(text, reply_markup=admin_back_kb(lang))

@dp.callback_query(F.data == "admin_expiring")
async def admin_expiring(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    lang = get_user_lang(call.from_user.id)
    now = datetime.now()

    async with aiosqlite.connect("db.db") as db:
        async with db.execute("SELECT user_id, lang, sub, expire FROM users ORDER BY expire ASC") as cur:
            rows = await cur.fetchall()

    lines = []
    for uid, row_lang, sub, exp in rows:
        expire_dt = datetime.fromisoformat(exp)
        days_left = (expire_dt - now).days
        if days_left <= 3:
            lines.append(f"ID: <b>{uid}</b> | {sub} | {days_left} days")

    if not lines:
        await call.message.edit_text(TEXT[lang]["expiring_empty"], reply_markup=admin_back_kb(lang))
        return

    await call.message.edit_text(
        "⏳ EXPIRING SOON\n\n" + "\n".join(lines),
        reply_markup=admin_back_kb(lang)
    )

@dp.callback_query(F.data == "admin_banned")
async def admin_banned(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    lang = get_user_lang(call.from_user.id)

    async with aiosqlite.connect("db.db") as db:
        async with db.execute("SELECT user_id, reason, created_at FROM banned_users ORDER BY created_at DESC") as cur:
            rows = await cur.fetchall()

    if not rows:
        await call.message.edit_text(TEXT[lang]["banned_empty"], reply_markup=admin_back_kb(lang))
        return

    text = "⛔ BANNED USERS\n\n"
    for uid, reason, created_at in rows[:30]:
        text += f"ID: <b>{uid}</b>\n"
        text += f"Reason: {reason}\n"
        text += f"At: {created_at}\n\n"

    await call.message.edit_text(text, reply_markup=admin_back_kb(lang))

@dp.callback_query(F.data == "admin_give")
async def admin_give(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    lang = get_user_lang(call.from_user.id)
    admin_state["mode"] = "give_uid"
    admin_state["target_user_id"] = None
    await call.message.answer(TEXT[lang]["send_user_id"], reply_markup=admin_back_kb(lang))

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    lang = get_user_lang(call.from_user.id)
    admin_state["mode"] = "broadcast"
    await call.message.answer(TEXT[lang]["broadcast_text"], reply_markup=admin_back_kb(lang))

# =========================
# ADMIN TEXT INPUT
# =========================

@dp.message(F.text)
async def text_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    mode = admin_state.get("mode")
    lang = get_user_lang(message.from_user.id)

    if mode == "give_uid":
        try:
            admin_state["target_user_id"] = int(message.text.strip())
        except ValueError:
            await message.answer(TEXT[lang]["id_must_be_number"])
            return
        admin_state["mode"] = "give_days"
        await message.answer(TEXT[lang]["send_days"])
        return

    if mode == "give_days":
        try:
            days = int(message.text.strip())
        except ValueError:
            await message.answer(TEXT[lang]["days_must_be_number"])
            return

        uid = admin_state["target_user_id"]
        expire = datetime.now() + timedelta(days=days)

        async with aiosqlite.connect("db.db") as db:
            await db.execute("""
            INSERT OR REPLACE INTO users(user_id, lang, sub, expire)
            VALUES (?, ?, ?, ?)
            """, (uid, "ru", "manual", expire.isoformat()))
            await db.commit()

        try:
            await bot.send_message(uid, TEXT["ru"]["vip_granted"].format(days=days))
        except Exception:
            pass

        admin_state["mode"] = None
        admin_state["target_user_id"] = None
        await message.answer(TEXT[lang]["done"], reply_markup=admin_main_kb(lang))
        return

    if mode == "broadcast":
        text = message.text

        async with aiosqlite.connect("db.db") as db:
            async with db.execute("SELECT user_id FROM users") as cur:
                users = await cur.fetchall()

        for (uid,) in users:
            try:
                await bot.send_message(uid, text)
            except Exception:
                pass

        admin_state["mode"] = None
        await message.answer(TEXT[lang]["broadcast_done"], reply_markup=admin_main_kb(lang))
        return

# =========================
# SUBSCRIPTION CHECKER
# =========================

async def subscription_checker():
    warned_today = set()

    while True:
        now = datetime.now()

        async with aiosqlite.connect("db.db") as db:
            async with db.execute("SELECT user_id, lang, sub, expire FROM users") as cur:
                rows = await cur.fetchall()

            for uid, lang, sub, expire_str in rows:
                expire_dt = datetime.fromisoformat(expire_str)

                if now >= expire_dt:
                    try:
                        await bot.ban_chat_member(CHANNEL_ID, uid)
                        await bot.unban_chat_member(CHANNEL_ID, uid)
                    except Exception:
                        pass

                    try:
                        await bot.send_message(uid, TEXT[lang]["expired"] + "\n" + TEXT[lang]["renew_hint"])
                    except Exception:
                        pass

                    await db.execute("DELETE FROM users WHERE user_id=?", (uid,))
                    await db.commit()
                    warned_today = {x for x in warned_today if x[0] != uid}
                    continue

                time_left = expire_dt - now
                if 0 < time_left.total_seconds() <= 86400:
                    key = (uid, now.date().isoformat())
                    if key not in warned_today:
                        try:
                            await bot.send_message(uid, TEXT[lang]["expiring_soon"] + "\n" + TEXT[lang]["renew_hint"])
                        except Exception:
                            pass
                        warned_today.add(key)

        await asyncio.sleep(3600)

# =========================
# MAIN
# =========================

async def main():
    await init_db()
    asyncio.create_task(subscription_checker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())