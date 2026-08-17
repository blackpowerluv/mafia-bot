import os
import json
import traceback
from aiohttp import web
from bot import bot, dp

# Создаем приложение aiohttp
app = web.Application()

async def webhook(request):
    """Обработка входящих обновлений от Telegram"""
    try:
        print("📩 Получен POST запрос на /webhook")
        # Получаем данные от Telegram (это обычный словарь)
        update_data = await request.json()
        
        # ВАЖНО: feed_update принимает СЛОВАРЬ (dict), а не объект Update!
        await dp.feed_update(update_data)
        
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка webhook: {e}")
        traceback.print_exc()
        return web.Response(text="Error", status=500)

async def on_startup(app):
    """Установка вебхука при старте"""
    print("🚀 Запуск бота через webhook...")
    try:
        # Убедимся, что старый вебхук удален перед установкой нового
        await bot.delete_webhook(drop_pending_updates=True)
        
        webhook_url = "https://mafia-bot-sggx.onrender.com/webhook"
        await bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook установлен: {webhook_url}")
    except Exception as e:
        print(f"⚠️ Ошибка установки webhook: {e}")

async def on_shutdown(app):
    """Очистка при остановке"""
    await bot.delete_webhook()
    await bot.session.close()
    print("🛑 Бот остановлен")

# Настраиваем роутер
app.router.add_post("/webhook", webhook)
app.router.add_get("/", lambda r: web.Response(text="Bot is running!", status=200))
app.router.add_get("/health", lambda r: web.Response(text="OK", status=200))

# Подключаем хуки старта и остановки
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    web.run_app(app, host="0.0.0.0", port=port)
