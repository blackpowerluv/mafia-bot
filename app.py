import os
from aiohttp import web
import asyncio

app = web.Application()

async def handle(request):
    return web.Response(text="Я жив!", status=200)

app.router.add_get("/", handle)
app.router.add_get("/health", handle)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)
