import asyncio
import os
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8331219511:AAESgh6Bk70GyID3dhfI_bFvwK65b8G00CQ"
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Меню (Кнопки)
def get_main_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Магазин")]
        ],
        resize_keyboard=True
    )
    return kb

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Привет! Нажми на кнопку 'Магазин'.", reply_markup=get_main_keyboard())

@dp.message(F.text == "🛒 Магазин")
async def shop(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Казино (5 пист.)", callback_data="casino")]
    ])
    await message.answer("🛒 Выбери:", reply_markup=kb)

@dp.callback_query(F.data == "casino")
async def casino(callback: types.CallbackQuery):
    outcomes = ["🤑 Выиграл 5!", "🎉 Выиграл 2!", "😐 Ничего.", "💀 Проиграл всё!"]
    text = random.choice(outcomes)
    # ОТВЕЧАЕМ В ЧАТ (это ты увидишь!)
    await callback.message.answer(f"🎰 Результат: {text}")
    # И закрываем кнопку
    await callback.answer()

# =========================================================
# ДОБАВЛЕНО: Чтобы бот отвечал на любое слово в чате!
# =========================================================
@dp.message()
async def echo(message: types.Message):
    await message.answer(f"✅ Я получил твоё сообщение: '{message.text}'")
