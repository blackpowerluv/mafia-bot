from flask import Flask, request
import asyncio
import os
import json
from bot import bot, dp, on_startup, on_shutdown

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running!", 200

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Обработка входящих обновлений от Telegram"""
    update_data = request.get_data(as_text=True)
    update_obj = types.Update(**json.loads(update_data))
    
    # Обрабатываем обновление
    await dp.process_update(update_obj)
    return "OK", 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Ручная установка вебхука"""
    try:
        asyncio.run(bot.set_webhook(
            url="https://mafia-bot-sggx.onrender.com/webhook"
        ))
        return "Webhook set successfully!", 200
    except Exception as e:
        return f"Error: {e}", 500

# Инициализация при запуске
@app.before_first_request
def setup():
    """Настройка вебхука при первом запросе"""
    try:
        # Устанавливаем вебхук в фоновом режиме
        asyncio.run(bot.set_webhook(
            url="https://mafia-bot-sggx.onrender.com/webhook"
        ))
        print("✅ Webhook установлен при запуске")
    except Exception as e:
        print(f"⚠️ Ошибка установки webhook: {e}")

if __name__ == "__main__":
    print("🚀 Запуск бота через webhook...")
    
    # Устанавливаем вебхук
    try:
        asyncio.run(bot.set_webhook(
            url="https://mafia-bot-sggx.onrender.com/webhook"
        ))
        print("✅ Webhook успешно установлен")
    except Exception as e:
        print(f"⚠️ Ошибка webhook: {e}")
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
