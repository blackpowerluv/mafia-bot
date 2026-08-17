import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

# ======= КОНФИГ =======
TOKEN = "8331219511:AAESgh6Bk70GyID3dhfI_bFvwK65b8G00CQ"
ADMINS = [1164507938, 6390275949, 5104412904, 5728665841, 7124674387]
MAIN_CHAT = -1004427827487
ADMIN_CHAT = -1003912490630

# Цены в пистолетиках
PRICES = {
    "at": 10,
    "diamond": 3,
    "stars": 20,
    "casino": 5
}

# Уровни скидок за сданные кристаллы
DISCOUNT_LEVELS = [
    {"crystals": 1, "discount": 1},
    {"crystals": 5, "discount": 10},
    {"crystals": 20, "discount": 50},
    {"crystals": 50, "discount": 70},
    {"crystals": 100, "discount": 90}
]

# ======= ХРАНИЛИЩЕ =======
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "users": {},
        "admins": {},
        "week_start": datetime.now().isoformat(),
        "total_crystals": 0
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

# ======= БОТ =======
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ---- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----
def get_user(user_id):
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "knives": 0,
            "guns": 0,
            "at": 0,
            "at_until": None,
            "diamonds": 0,
            "stars": 0,
            "crystals": 0,
            "donated_crystals": 0
        }
        save_data(data)
    return data["users"][uid]

def save_user(user_id, user_data):
    data["users"][str(user_id)] = user_data
    save_data(data)

def get_admin(user_id):
    uid = str(user_id)
    if uid not in data["admins"]:
        data["admins"][uid] = {"regs": 0}
        save_data(data)
    return data["admins"][uid]

def save_admin(user_id, admin_data):
    data["admins"][str(user_id)] = admin_data
    save_data(data)

def get_discount(user_id):
    user = get_user(user_id)
    donated = user["donated_crystals"]
    discount = 0
    for lvl in DISCOUNT_LEVELS:
        if donated >= lvl["crystals"]:
            discount = lvl["discount"]
    return discount

def check_week_reset():
    start = datetime.fromisoformat(data["week_start"])
    if datetime.now() - start > timedelta(days=7):
        for uid in data["admins"]:
            data["admins"][uid]["regs"] = 0
        data["week_start"] = datetime.now().isoformat()
        save_data(data)

def is_at_active(user_id):
    user = get_user(user_id)
    if user["at_until"]:
        try:
            until = datetime.fromisoformat(user["at_until"])
            if datetime.now() < until:
                return True
        except:
            pass
    return False

def parse_at_time(text):
    parts = text.split()
    if len(parts) == 2 and parts[1].lower() == "24h":
        now = datetime.now()
        until = now + timedelta(hours=24)
        return now.isoformat(), until.isoformat()
    elif len(parts) == 5:
        try:
            start = datetime.strptime(f"{parts[1]} {parts[2]}", "%d.%m.%Y %H:%M")
            until = datetime.strptime(f"{parts[3]} {parts[4]}", "%d.%m.%Y %H:%M")
            if until > start:
                return start.isoformat(), until.isoformat()
        except:
            pass
    return None, None

# ---- КНОПКИ (КЛАВИАТУРА) ----
def get_main_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Магазин"), KeyboardButton(text="💎 Сдать кристаллы")],
            [KeyboardButton(text="📩 Связаться с админами"), KeyboardButton(text="🛡️ Запросить АТ")]
        ],
        resize_keyboard=True
    )
    return kb

# ---- КОМАНДА /START (Показать меню) ----
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для игры в Мафию.\n"
        "Используй меню ниже или команды: /balance, /exchange",
        reply_markup=get_main_keyboard()
    )

# ---- КОМАНДА /BALANCE ----
@dp.message(Command("balance"))
async def balance(message: types.Message):
    user = get_user(message.from_user.id)
    discount = get_discount(message.from_user.id)
    at_status = "🟢 Активен" if is_at_active(message.from_user.id) else "🔴 Не активен"
    if user["at_until"]:
        try:
            until = datetime.fromisoformat(user["at_until"])
            at_status += f" до {until.strftime('%d.%m.%Y %H:%M')}"
        except:
            pass
    await message.reply(
        f"📊 *Твой баланс:*\n"
        f"🔪 Ножички: {user['knives']}\n"
        f"🔫 Пистолетики: {user['guns']}\n"
        f"💎 Кристаллы: {user['crystals']}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🛡️ АТ: {at_status}\n"
        f"💎 Алмазы: {user['diamonds']}\n"
        f"⭐ Звёзды: {user['stars']}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 Сдано кристаллов: {user['donated_crystals']}\n"
        f"🏷️ Твоя скидка: {discount}%",
        parse_mode="Markdown"
    )

# ---- ОБМЕН 10 НОЖИЧКОВ = 1 ПИСТОЛЕТ ----
@dp.message(Command("exchange"))
async def exchange(message: types.Message):
    user = get_user(message.from_user.id)
    if user["knives"] >= 10:
        user["knives"] -= 10
        user["guns"] += 1
        save_user(message.from_user.id, user)
        await message.reply("✅ Обменял 10 ножичков на 1 пистолетик!")
    else:
        await message.reply("❌ Не хватает ножичков (нужно 10).")

# ---- АДМИН: НАЧИСЛЕНИЕ НОЖИЧКОВ ----
@dp.message(Command("knife"))
async def add_knives(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    if message.reply_to_message is None or not message.reply_to_message.forward_from:
        await message.reply("❌ Ответь на пересланное сообщение игрока.")
        return
    try:
        count = int(message.text.split()[1])
    except:
        await message.reply("❌ Пример: `/knife 2`", parse_mode="Markdown")
        return
    user_id = message.reply_to_message.forward_from.id
    user = get_user(user_id)
    user["knives"] += count
    save_user(user_id, user)
    await message.reply(f"✅ Начислил {count} ножичка(ей) игроку.")

# ---- АДМИН: НАЧИСЛЕНИЕ ПИСТОЛЕТОВ ----
@dp.message(Command("gun"))
async def add_guns(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    if message.reply_to_message is None or not message.reply_to_message.forward_from:
        await message.reply("❌ Ответь на пересланное сообщение игрока.")
        return
    try:
        count = int(message.text.split()[1])
    except:
        await message.reply("❌ Пример: `/gun 1`", parse_mode="Markdown")
        return
    user_id = message.reply_to_message.forward_from.id
    user = get_user(user_id)
    user["guns"] += count
    save_user(user_id, user)
    await message.reply(f"✅ Начислил {count} пистолетик(ов) игроку.")

# ---- АДМИН: ВЫДАЧА АТ ----
@dp.message(Command("+at"))
async def give_at(message: types.Message):
    if message.chat.id != ADMIN_CHAT:
        return
    if message.from_user.id not in ADMINS:
        return
    if message.reply_to_message is None:
        await message.reply("❌ Ответь на сообщение игрока, которому выдаёшь АТ.")
        return
    user_id = None
    if message.reply_to_message.forward_from:
        user_id = message.reply_to_message.forward_from.id
    elif message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    if not user_id:
        await message.reply("❌ Не удалось определить пользователя.")
        return
    start, until = parse_at_time(message.text)
    if not start or not until:
        await message.reply("❌ Пример: `+at 24h` или `+at 19.08.2026 15:00 20.08.2026 15:00`", parse_mode="Markdown")
        return
    user = get_user(user_id)
    user["at_until"] = until
    user["at"] += 1
    save_user(user_id, user)
    await message.reply(f"✅ Игроку выдан АТ до {datetime.fromisoformat(until).strftime('%d.%m.%Y %H:%M')}")
    try:
        await bot.send_message(user_id, f"🛡️ Тебе выдан АТ до {datetime.fromisoformat(until).strftime('%d.%m.%Y %H:%M')}")
    except:
        pass

# ---- АДМИН: РЕГ ----
@dp.message(Command("reg"))
async def add_reg(message: types.Message):
    if message.chat.id != ADMIN_CHAT:
        return
    if message.from_user.id not in ADMINS:
        return
    admin = get_admin(message.from_user.id)
    admin["regs"] += 1
    save_admin(message.from_user.id, admin)
    await message.reply(f"✅ Записал тебе +1 рег. Всего: {admin['regs']}")

# ---- АДМИН: СТАТИСТИКА РЕГОВ ----
@dp.message(Command("stat"))
async def stat_regs(message: types.Message):
    if message.chat.id != ADMIN_CHAT:
        return
    if message.from_user.id not in ADMINS:
        return
    check_week_reset()
    sorted_admins = sorted(data["admins"].items(), key=lambda x: x[1]["regs"], reverse=True)
    text = "📊 *Статистика админов за неделю:*\n\n"
    for i, (uid, info) in enumerate(sorted_admins[:5], 1):
        try:
            user = await bot.get_chat(int(uid))
            name = user.first_name
        except:
            name = uid
        text += f"{i}. {name} — {info['regs']} регов\n"
    await message.reply(text, parse_mode="Markdown")

# ---- КНОПКИ В ЛС (МАГАЗИН) ----
@dp.message(F.text == "🛒 Магазин")
async def shop(message: types.Message):
    discount = get_discount(message.from_user.id)
    price_at = PRICES["at"]
    if discount > 0:
        price_at = int(price_at * (100 - discount) / 100)
    price_diamond = PRICES["diamond"]
    if discount > 0:
        price_diamond = int(price_diamond * (100 - discount) / 100)
    price_stars = PRICES["stars"]
    if discount > 0:
        price_stars = int(price_stars * (100 - discount) / 100)
    price_casino = PRICES["casino"]
    if discount > 0:
        price_casino = int(price_casino * (100 - discount) / 100)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🛡️ АТ ({price_at} пист.)", callback_data="buy_at")],
        [InlineKeyboardButton(text=f"💎 Алмаз ({price_diamond} пист.)", callback_data="buy_diamond")],
        [InlineKeyboardButton(text=f"⭐ Звёзды 10шт ({price_stars} пист.)", callback_data="buy_stars")],
        [InlineKeyboardButton(text=f"🎰 Казино ({price_casino} пист.)", callback_data="casino")]
    ])
    await message.answer(
        f"🛒 *Выбери товар:*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🏷️ Твоя скидка: {discount}%\n"
        f"💡 Цены уже с учётом скидки.",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(F.text == "💎 Сдать кристаллы")
async def donate_crystals_menu(message: types.Message):
    user = get_user(message.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Сдать 1 кристалл", callback_data="donate_1")],
        [InlineKeyboardButton(text="💎 Сдать 5 кристаллов", callback_data="donate_5")],
        [InlineKeyboardButton(text="💎 Сдать 20 кристаллов", callback_data="donate_20")],
        [InlineKeyboardButton(text="💎 Сдать 50 кристаллов", callback_data="donate_50")],
        [InlineKeyboardButton(text="💎 Сдать 100 кристаллов", callback_data="donate_100")]
    ])
    await message.answer(
        f"💎 *У тебя: {user['crystals']} кристаллов*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"За сдачу кристаллов ты повышаешь свою скидку в магазине:\n"
        f"1 кристалл → 1%\n"
        f"5 кристаллов → 10%\n"
        f"20 кристаллов → 50%\n"
        f"50 кристаллов → 70%\n"
        f"100 кристаллов → 90%\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 Ты уже сдал: {user['donated_crystals']} кристаллов",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(F.text == "📩 Связаться с админами")
async def contact_admin(message: types.Message):
    await message.answer("✍️ *Напиши своё сообщение админам.* Они ответят тебе сюда.", parse_mode="Markdown")

@dp.message(F.text == "🛡️ Запросить АТ")
async def request_at(message: types.Message):
    await message.answer(
        "🛡️ *Запрос на бесплатный АТ*\n\n"
        "Чтобы получить бесплатный АТ на 1 день, отправь сюда:\n"
        "1. Три ссылки на сообщения в чате, где видно, что тебя 3 раза подряд били/проверяли/садились в первую или вторую ночь/день.\n"
        "2. Краткое описание ситуации.\n\n"
        "Админы проверят и выдадут АТ.",
        parse_mode="Markdown"
    )

# ---- ОБРАБОТКА СДАЧИ КРИСТАЛЛОВ ----
@dp.callback_query(F.data.startswith("donate_"))
async def donate_crystals(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[1])
    user = get_user(callback.from_user.id)
    if user["crystals"] < amount:
        await callback.answer(f"❌ Не хватает кристаллов! У тебя {user['crystals']}", show_alert=True)
        return
    user["crystals"] -= amount
    user["donated_crystals"] += amount
    save_user(callback.from_user.id, user)
    data["total_crystals"] += amount
    save_data(data)
    discount = get_discount(callback.from_user.id)
    await callback.answer(
        f"✅ Сдал {amount} кристаллов!\n"
        f"Твоя скидка теперь: {discount}%",
        show_alert=True
    )
    await callback.message.edit_text(
        f"✅ Ты сдал {amount} кристаллов.\n"
        f"💰 Всего сдано: {user['donated_crystals']} кристаллов\n"
        f"🏷️ Твоя скидка: {discount}%"
    )

# ---- ОБРАБОТКА ПОКУПОК ----
@dp.callback_query(F.data.startswith("buy_") | F.data == "casino")
async def handle_purchase(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    discount = get_discount(callback.from_user.id)
    action = callback.data
    if action == "buy_at":
        price = int(PRICES["at"] * (100 - discount) / 100)
        if is_at_active(callback.from_user.id):
            await callback.answer("❌ У тебя уже активен АТ!", show_alert=True)
            return
        if user["guns"] >= price:
            user["guns"] -= price
            user["at"] += 1
            user["at_until"] = (datetime.now() + timedelta(hours=24)).isoformat()
            save_user(callback.from_user.id, user)
            await callback.answer("🛡️ Купил АТ на 24 часа!", show_alert=True)
        else:
            await callback.answer(f"❌ Не хватает пистолетиков! Нужно {price}", show_alert=True)
    elif action == "buy_diamond":
        price = int(PRICES["diamond"] * (100 - discount) / 100)
        if user["guns"] >= price:
            user["guns"] -= price
            user["diamonds"] += 1
            save_user(callback.from_user.id, user)
            await callback.answer("💎 Купил алмаз!", show_alert=True)
        else:
            await callback.answer(f"❌ Не хватает пистолетиков! Нужно {price}", show_alert=True)
    elif action == "buy_stars":
        price = int(PRICES["stars"] * (100 - discount) / 100)
        if user["guns"] >= price:
            user["guns"] -= price
            user["stars"] += 10
            save_user(callback.from_user.id, user)
            await callback.answer("⭐ Купил 10 звёзд!", show_alert=True)
        else:
            await callback.answer(f"❌ Не хватает пистолетиков! Нужно {price}", show_alert=True)
    elif action == "casino":
        price = int(PRICES["casino"] * (100 - discount) / 100)
        if user["guns"] >= price:
            user["guns"] -= price
            save_user(callback.from_user.id, user)
            outcomes = [
                ("🤑 Выиграл 5 пистолетов!", 5),
                ("🎉 Выиграл 2 пистолета!", 2),
                ("😐 Ничего не выиграл.", 0),
                ("💀 Проиграл всё!", 0)
            ]
            text, win = random.choice(outcomes)
            if win > 0:
                user["guns"] += win
                save_user(callback.from_user.id, user)
            await callback.answer(f"🎰 {text}", show_alert=True)
        else:
            await callback.answer(f"❌ Не хватает пистолетиков! Нужно {price}", show_alert=True)
