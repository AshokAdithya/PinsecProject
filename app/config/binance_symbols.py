import asyncio
import requests
from app.utils.logger import logger
import os
from dotenv import load_dotenv

load_dotenv()

VALID_SYMBOLS = set()
_lock = asyncio.Lock()


async def fetch_testnet_symbols(retries: int = 3, delay=2.0):
    url = os.getenv("BINANCE_LIST")

    for attempt in range(1, retries + 1):
        try:
            response = await asyncio.to_thread(requests.get, url, timeout=5)
            response.raise_for_status()
            data = response.json()

            symbols = {
                s["symbol"].upper()
                for s in data.get("symbols", [])
                if s.get("status") == "TRADING"
            }

            async with _lock:
                VALID_SYMBOLS.clear()
                VALID_SYMBOLS.update(symbols)

            logger.info(f"Loaded {len(VALID_SYMBOLS)} symbols from Binance Testnet")
            return

        except Exception as e:

            logger.error(f"Attempt {attempt}/{retries} failed to fetch symbols: {e}")

            if attempt < retries:
                sleep_time = delay * (
                    2 ** (attempt - 1)
                )  # Retry logic with increasing delay
                logger.info(f"Retrying in {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)
            else:
                logger.error("❌ All retry attempts failed.")


def is_valid_symbol(symbol: str) -> bool:
    return symbol.upper() in VALID_SYMBOLS
