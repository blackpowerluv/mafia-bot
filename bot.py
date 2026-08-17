import os
import json
import traceback
from aiohttp import web
from bot import bot, dp

app = web.Application()

async def webhook(request):
    try:
        data = await request.json()
        print("📩 Получен POST запрос на /webhook")
        await dp.feed_webhook_update(bot, data)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка webhook: {e}")
        traceback.print_exc()
        return web.Response(text="Error", status=500)

async def on_startup(app):
    print("🚀 Запуск бота через webhook...")
    webhook_url = "https://mafia-bot-sggx.onrender.com/webhook"
    await bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook установлен: {webhook_url}")

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

app.router.add_post("/webhook", webhook)
app.router.add_get("/", lambda r: web.Response(text="Bot is running!", status=200))
app.router.add_get("/health", lambda r: web.Response(text="OK", status=200))
# Добавил маршрут для ручной проверки
app.router.add_get("/set_webhook", lambda r: web.Response(text="✅ Вебхук уже установлен при старте.", status=200))

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = 10000
    web.run_app(app, host="0.0.0.0", port=port)
