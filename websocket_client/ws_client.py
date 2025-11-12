# ws_client.py
import asyncio
import websockets
from dotenv import load_dotenv
import os

load_dotenv()

WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
WEBSOCKET_PORT = os.getenv("WEBSOCKET_PORT")


async def listen():
    uri = f"ws://localhost:{WEBSOCKET_PORT}"

    async with websockets.connect(uri) as websocket:
        print("Connected to Crypto Price Streaming Platform WebSocket server!")

        # Continuously read messages
        async for message in websocket:
            print(f"Candle: {message}")


if __name__ == "__main__":
    asyncio.run(listen())
