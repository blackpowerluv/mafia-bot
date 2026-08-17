from flask import Flask, request
import asyncio
import os
import json
from bot import bot, dp

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running!", 200

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Обработка входящих обновлений от Telegram"""
    try:
        update_data = request.get_data(as_text=True)
        update_obj = types.Update(**json.loads(update_data))
        await dp.process_update(update_obj)
        return "OK", 200
    except Exception as e:
        print(f"Ошибка webhook: {e}")
        return "Error", 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Ручная установка вебхука"""
    try:
        webhook_url = "https://mafia-bot-sggx.onrender.com/webhook"
        # Синхронный вызов асинхронной функции
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.set_webhook(url=webhook_url))
        loop.close()
        return f"✅ Webhook установлен: {webhook_url}", 200
    except Exception as e:
        return f"❌ Ошибка: {e}", 500

if __name__ == "__main__":
    print("🚀 Запуск бота через webhook...")
    
    # Устанавливаем вебхук при старте
    try:
        webhook_url = "https://mafia-bot-sggx.onrender.com/webhook"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.set_webhook(url=webhook_url))
        loop.close()
        print(f"✅ Webhook установлен: {webhook_url}")
    except Exception as e:
        print(f"⚠️ Ошибка установки webhook: {e}")
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
