import asyncio
import requests
from app.utils.logger import logger
import os
from dotenv import load_dotenv

load_dotenv()

VALID_SYMBOLS = set()
_lock = asyncio.Lock()

async def fetch_testnet_symbols():
    url = os.getenv("BINANCE_LIST")

    try:
        response = await asyncio.to_thread(requests.get, url, timeout=5)
        response.raise_for_status()
        data = response.json()

        symbols = {s["symbol"].upper() for s in data.get("symbols", []) if s.get("status") == "TRADING"}

        async with _lock:
            VALID_SYMBOLS.clear()
            VALID_SYMBOLS.update(symbols)

        logger.info(f"Loaded {len(VALID_SYMBOLS)} symbols from Binance Testnet")

    except Exception as e:
        logger.error(f"Failed to fetch symbols: {e}")

def is_valid_symbol(symbol: str) -> bool:
    return symbol.upper() in VALID_SYMBOLS
