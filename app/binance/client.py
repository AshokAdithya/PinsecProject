# One connection for all symbols
# import json
# import websockets
# import asyncio
# from app.manager.symbol_manager import manager
# from app.core.models import Tick
# from app.utils.logger import logger
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # websocket url
# URL = os.getenv("BINANCE_TESTNET")

# class BinanceClient:
#     def __init__(self, max_retries: int = 5, base_delay: float = 3.0):
#         self.ws = None
#         self.running = True
#         self.max_retries = max_retries
#         self.base_delay = base_delay

#     # Getting data from websocket
#     async def run_forever(self):
#         logger.info("Binance Testnet client starting...")
#         attempt = 0

#         while self.running:
#             symbols = manager.list_symbols()
#             if not symbols:
#                 await asyncio.sleep(1)
#                 continue

#             streams = [f"{s.lower()}@trade" for s in symbols]
#             stream_path = "/".join(streams)
#             url = f"{URL}?streams={stream_path}"

#             try:
#                 logger.info(f"Connecting to Testnet: {symbols}")
#                 async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
#                     self.ws = ws
#                     logger.info(f"TESTNET SYMBOLS : {symbols}")

#                     # Getting updates every time from BINANCE TESTNET
#                     while True:
#                         msg = json.loads(await ws.recv())
#                         data = msg.get("data") or msg

#                         if data.get("e") != "trade":
#                             continue

#                         symbol = data["s"]
#                         if symbol not in manager.aggregators:
#                             continue

#                         tick = Tick(
#                             symbol=symbol,
#                             price=float(data["p"]),
#                             qty=float(data["q"]),
#                             timestamp=int(data["T"])
#                         )
#                         manager.process_tick(tick)

#                         # Check if symbol list changed
#                         current_symbols = manager.list_symbols()
#                         if set(current_symbols) != set(symbols):
#                             logger.info("Symbol list changed")
#                             break

#             except Exception as e:
#                 attempt += 1
#                 delay = min(self.base_delay * (2 ** (attempt - 1)), 5.0)
#                 logger.warning(f"Attempt : {attempt}/{self.max_retries}, Connection failed: {e}. Reconnecting in {delay:.1f}s...")

#                 self.ws = None
#                 await asyncio.sleep(delay)

#                 if attempt >= self.max_retries:
#                     logger.error(f"Exceeded max retries ({self.max_retries}). Giving up.")
#                     break

#     def stop(self):

#         self.running = False

# Parallel connection
import json
import websockets
import asyncio
from app.manager.symbol_manager import manager
from app.core.models import Tick
from app.utils.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.getenv("BINANCE_TESTNET")

class BinanceClient:
    def __init__(self, max_retries: int = 5, base_delay: float = 3.0):
        self.running = True
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.tasks = {}  # for parallel stream per symbol

    # parallel per symbol
    async def connect_symbol(self, symbol: str):
        attempt = 0
        stream_url = f"{URL}?streams={symbol.lower()}@trade"

        while self.running:
            try:
                logger.info(f"[{symbol}] Connecting to Binance Testnet...")
                async with websockets.connect(stream_url, ping_interval=20, ping_timeout=20) as ws:
                    logger.info(f"[{symbol}] Connected to Testnet stream.")
                    attempt = 0

                    while self.running:
                        msg = json.loads(await ws.recv())
                        data = msg.get("data") or msg

                        if data.get("e") != "trade":
                            continue

                        tick = Tick(
                            symbol=data["s"],
                            price=float(data["p"]),
                            qty=float(data["q"]),
                            timestamp=int(data["T"])
                        )
                        manager.process_tick(tick)

            except Exception as e:
                attempt += 1
                delay = min(self.base_delay * (2 ** (attempt - 1)), 10.0)
                logger.warning(f"[{symbol}] Attempt {attempt}/{self.max_retries}, Error: {e}. Reconnecting in {delay:.1f}s...")
                await asyncio.sleep(delay)

                if attempt >= self.max_retries:
                    logger.error(f"[{symbol}] Exceeded max retries, stopping stream.")
                    break

        logger.info(f"[{symbol}] Stream stopped.")

    async def monitor_symbols(self):
        logger.info("Binance Testnet client starting...")

        while self.running:
            current_symbols = set(manager.list_symbols())
            active_symbols = set(self.tasks.keys())

            # Start new tasks
            for symbol in current_symbols - active_symbols:
                task = asyncio.create_task(self.connect_symbol(symbol))
                self.tasks[symbol] = task
                logger.info(f"Started stream for {symbol}")

            # Popping removed symbols from tasks
            for symbol in active_symbols - current_symbols:
                logger.info(f"Stopping stream for {symbol}")
                task = self.tasks.pop(symbol)
                task.cancel()

            await asyncio.sleep(2)

    async def run_forever(self):
        await self.monitor_symbols()

    def stop(self):
        self.running = False
        for symbol, task in self.tasks.items():
            task.cancel()
        logger.info("All streams stopped.")
