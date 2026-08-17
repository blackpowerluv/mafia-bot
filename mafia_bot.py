import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8331219511:AAESgh6Bk70GyID3dhfI_bFvwK65b8G00CQ"
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Простая клавиатура
def get_main_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Магазин"), KeyboardButton(text="💎 Сдать кристаллы")]
        ],
        resize_keyboard=True
    )
    return kb

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Тестовый режим! Нажми на любую кнопку.", reply_markup=get_main_keyboard())

# Обработка кнопки МАГАЗИН (с гарантированным ответом)
@dp.message(F.text == "🛒 Магазин")
async def shop(message: types.Message):
    # Создаем инлайн кнопки
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Нажми меня", callback_data="test_button")]
    ])
    # Бот отправляет сообщение с кнопкой
    await message.answer("🛒 *Магазин (тестовый):*\nНажми на кнопку ниже.", reply_markup=kb, parse_mode="Markdown")

# Обработка нажатия на инлайн кнопку (ГЛАВНОЕ ИСПРАВЛЕНИЕ)
@dp.callback_query(F.data == "test_button")
async def process_callback(callback: types.CallbackQuery):
    # ВАЖНО: Всегда отвечаем на callback, чтобы Telegram знал, что всё принято!
    await callback.answer("✅ Кнопка нажата! Бот работает.", show_alert=True)

    # Меняем текст сообщения
    await callback.message.edit_text("✅ Ты нажал на кнопку! Всё работает отлично!")
