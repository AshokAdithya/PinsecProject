import json
import websockets
import asyncio
from app.manager.symbol_manager import manager
from app.core.models import Tick
from app.utils.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

# websocket url
URL = os.getenv("BINANCE_TESTNET")

class BinanceClient:
    def __init__(self, max_retries: int = 5, base_delay: float = 3.0):
        self.ws = None
        self.running = True
        self.max_retries = max_retries
        self.base_delay = base_delay

    # Getting data from websocket
    async def run_forever(self):
        logger.info("Binance Testnet client starting...")
        attempt = 0

        while self.running:
            symbols = manager.list_symbols()
            if not symbols:
                await asyncio.sleep(1)
                continue

            streams = [f"{s.lower()}@trade" for s in symbols]
            stream_path = "/".join(streams)
            url = f"{URL}?streams={stream_path}"

            try:
                logger.info(f"Connecting to Testnet: {symbols}")
                async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                    self.ws = ws
                    logger.info(f"TESTNET SYMBOLS : {symbols}")

                    # Getting updates every time from BINANCE TESTNET
                    while True:
                        msg = json.loads(await ws.recv())
                        data = msg.get("data") or msg

                        if data.get("e") != "trade":
                            continue

                        symbol = data["s"]
                        if symbol not in manager.aggregators:
                            continue

                        tick = Tick(
                            symbol=symbol,
                            price=float(data["p"]),
                            qty=float(data["q"]),
                            timestamp=int(data["T"])
                        )
                        manager.process_tick(tick)

                        # Check if symbol list changed
                        current_symbols = manager.list_symbols()
                        if set(current_symbols) != set(symbols):
                            logger.info("Symbol list changed")
                            break

            except Exception as e:
                attempt += 1
                delay = min(self.base_delay * (2 ** (attempt - 1)), 60.0)
                logger.warning(f"Attempt : {attempt}/{self.max_retries}, Connection failed: {e}. Reconnecting in {delay:.1f}s...")

                self.ws = None
                await asyncio.sleep(delay)

                if attempt >= self.max_retries:
                    logger.error(f"Exceeded max retries ({self.max_retries}). Giving up.")
                    break

    def stop(self):
        self.running = False