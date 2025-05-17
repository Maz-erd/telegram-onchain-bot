import os
import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=BOT_TOKEN)

async def fetch_onchain_data():
    one_hour_ago = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp())
    url = (
        "https://api.cddstamp.com/api/v1/onchain/buysells"
        "?token=rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof"
        f"&start_time={one_hour_ago}"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None, resp.status
            data = await resp.json()
            return data, None

def format_message(data):
    token = data.get("token", {})
    pair = data.get("pair", "N/A")
    price = token.get("price", "N/A")
    volume_24h = token.get("volume_24h", "N/A")

    buys = data.get("buys", [])
    sells = data.get("sells", [])

    buy_count = len(buys)
    sell_count = len(sells)

    buy_vol = sum(buy.get("amount", 0) for buy in buys)
    sell_vol = sum(sell.get("amount", 0) for sell in sells)

    message = (
        f"🪙 Token: {token.get('symbol', 'N/A')} ({token.get('address', '')[:6]}…{token.get('address', '')[-4:]})\n"
        f"🔗 Pair: {pair}\n\n"
        f"💰 Price: ${price}\n"
        f"📈 24 h Volume: ${volume_24h}\n\n"
        f"🟢 Buys: {buy_count} (${buy_vol:.2f}) | 🔴 Sells: {sell_count} (${sell_vol:.2f})"
    )
    return message

async def send_update():
    data, error = await fetch_onchain_data()
    if error:
        message = f"⚠️ Error fetching data (status {error})"
    elif not data or not data.get("token"):
        message = "⚠️ No data found."
    else:
        message = format_message(data)

    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

def run_scheduled():
    import schedule
    import time

    schedule.every(1).hours.do(lambda: asyncio.run(send_update()))

    print("✅ Bot is running... Press CTRL+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduled()
