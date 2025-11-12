import websockets
import asyncio
from app.core.broadcaster import clients
from app.utils.logger import logger
import os
from dotenv import load_dotenv

load_dotenv()

websocket_ip = os.getenv("WEBSOCKET_IP")
websocket_port = os.getenv("WEBSOCKET_PORT")


# Handling Multiple clients for websockets
async def handler(websocket):
    clients.add(websocket)
    logger.info(f"WS client connected. Total: {len(clients)}")
    try:
        async for _ in websocket:
            pass
    except:
        pass
    finally:
        clients.discard(websocket)


async def start_ws_server():
    server = await websockets.serve(
        handler,
        websocket_ip,
        websocket_port,
        compression="deflate",
        max_size=2**20,
        ping_interval=20,
        ping_timeout=20,
    )
    logger.info(f"WebSocket server running on {websocket_ip}:{websocket_port}")
    await server.wait_closed()
