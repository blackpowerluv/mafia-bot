from flask import Flask
import asyncio
import os
import threading
from aiogram import Bot, Dispatcher
from bot import bot, dp, main  # импортируем вашего бота

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running!", 200

# Запускаем бота в отдельном потоке с правильным event loop
def run_bot():
    # Создаём новый event loop для этого потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Запускаем главную функцию бота
    try:
        loop.run_until_complete(main())
    except Exception as e:
        print(f"Ошибка бота: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask для пингов Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
