import asyncio
import requests
import time
from telegram import Bot
import schedule

# === CONFIG ===
TELEGRAM_TOKEN = '7557580299:AAGbdDBhUrOFQ5cPbeRoOq0tNzv59IIdMYE'   # Replace with your BotFather token
CHAT_ID         = 1808160620                 # Your Telegram chat ID
TOKEN_ADDRESS   = "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof"
CHAIN_ID        = "solana"

bot = Bot(token=TELEGRAM_TOKEN)

def fetch_data():
    # 1) Get all pools for the token
    pools_url = f"https://api.dexscreener.com/token-pairs/v1/{CHAIN_ID}/{TOKEN_ADDRESS}"
    resp_pools = requests.get(pools_url)
    print("Pools HTTP status:", resp_pools.status_code)
    if resp_pools.status_code != 200:
        return f"⚠️ Error fetching pools (status {resp_pools.status_code})"
    pools = resp_pools.json()
    if not pools:
        return "⚠️ No pools found for this token."  # :contentReference[oaicite:0]{index=0}

    # 2) Pick the first pool's pairAddress
    pair_id = pools[0]["pairAddress"]

    # 3) Fetch latest pair data
    pair_url = f"https://api.dexscreener.com/latest/dex/pairs/{CHAIN_ID}/{pair_id}"
    resp_pair = requests.get(pair_url)
    print("Pair HTTP status:", resp_pair.status_code)
    if resp_pair.status_code != 200:
        return f"⚠️ Error fetching pair data (status {resp_pair.status_code})"
    data = resp_pair.json()
    pairs = data.get("pairs")
    if not pairs:
        return "⚠️ No data for this pair."
    pair = pairs[0]

    # 4) Extract metrics
    token_symbol  = pair["baseToken"]["symbol"]
    price_usd     = float(pair.get("priceUsd", 0))
    volume_24h    = float(pair.get("volume", {}).get("h24", 0))
    buys          = pair.get("txns", {}).get("buys", 0)
    sells         = pair.get("txns", {}).get("sells", 0)

    # 5) Build message
    msg = (
        f"📊 *Hourly Solana Token Update*\n\n"
        f"🪙 Token: `{token_symbol}` ({TOKEN_ADDRESS[:6]}…{TOKEN_ADDRESS[-4:]})\n"
        f"🔗 Pair: {pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}\n\n"
        f"💰 Price: ${price_usd:.6f}\n"
        f"📈 24 h Volume: ${volume_24h:,.0f}\n"
        f"🟢 Buys: {buys} | 🔴 Sells: {sells}"
    )
    return msg

async def send_update():
    message = fetch_data()
    print("Message to send:\n", message)
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

def run_scheduled():
    # Schedule at the top of every hour
    schedule.every().hour.at(":00").do(lambda: asyncio.run(send_update()))
    print("✅ Bot is running... Press CTRL+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # 1) Send immediate test
    asyncio.run(send_update())
    # 2) Then hourly
    run_scheduled()
