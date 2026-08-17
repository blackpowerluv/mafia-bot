import os
import json
from aiohttp import web
from bot import bot, dp

app = web.Application()

async def webhook(request):
    try:
        # Получаем данные от Telegram (это обычный словарь Python)
        update_data = await request.json()
        
        # В Aiogram 3 feed_update принимает только СЛОВАРЬ (dict)
        await dp.feed_update(update_data)
        
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return web.Response(text="Error", status=500)

async def on_startup(app):
    webhook_url = "https://mafia-bot-sggx.onrender.com/webhook"
    await bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook установлен: {webhook_url}")

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

app.router.add_post("/webhook", webhook)
app.router.add_get("/", lambda r: web.Response(text="OK", status=200))
app.router.add_get("/health", lambda r: web.Response(text="OK", status=200))

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    web.run_app(app, host="0.0.0.0", port=port)
