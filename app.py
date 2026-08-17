from flask import Flask
import threading
import os
# Импортируем вашего основного бота
from bot import bot, dp

app = Flask(__name__)

# Простые проверки для Render, чтобы сервис считался живым
@app.route('/')
@app.route('/health')
def health():
    return "Bot is running", 200

# Функция, которая запускает вашего бота в фоновом потоке
def run_bot():
    import asyncio
    from bot import main
    asyncio.run(main())

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке, чтобы Flask не блокировал его
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Запускаем Flask-сервер, который будет занимать порт $PORT
    # Render требует, чтобы приложение слушало этот порт [citation:2][citation:3]
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)