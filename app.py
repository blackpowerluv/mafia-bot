from flask import Flask, request
import asyncio
import os
import json
import traceback
from bot import bot, dp
from aiogram.types import Update

app = Flask(__name__)

# ==========================================
# УСТАНОВКА ВЕБХУКА ПРИ СТАРТЕ
# ==========================================
print("🚀 Запуск бота через webhook...")
try:
    webhook_url = "https://mafia-bot-sggx.onrender.com/webhook"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot.set_webhook(url=webhook_url))
    loop.close()
    print(f"✅ Webhook установлен: {webhook_url}")
except Exception as e:
    print(f"⚠️ Ошибка установки webhook: {e}")

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("📩 Получен POST запрос на /webhook")
        update_data = request.get_json()
        
        update = Update.model_validate(update_data)
        
        # Запускаем обработку Aiogram
        asyncio.run(dp.feed_update(update))
        
        return "OK", 200
    except Exception as e:
        # Это выведет полную ошибку в логи Render
        print(f"❌ Ошибка webhook: {e}")
        traceback.print_exc()
        return "Error", 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        webhook_url = "https://mafia-bot-sggx.onrender.com/webhook"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.set_webhook(url=webhook_url))
        loop.close()
        return f"✅ Webhook установлен: {webhook_url}", 200
    except Exception as e:
        return f"❌ Ошибка: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
