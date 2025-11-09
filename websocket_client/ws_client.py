# ws_client.py
import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        print("Connected to Crypto Price Streaming Platform WebSocket server!")

        # Continuously read messages
        async for message in websocket:
            print(f"Candle: {message}")

if __name__ == "__main__":
    asyncio.run(listen())
