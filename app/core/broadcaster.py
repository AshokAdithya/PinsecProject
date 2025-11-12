import json
from typing import Set
import websockets
from app.utils.time_format import format_timestamp
import asyncio

clients: Set[websockets.WebSocketServerProtocol] = set()


# Broadcast message to all the clients connected
async def broadcast(candle):
    if not clients:
        return

    data = candle.to_dict()
    data["timestamp"] = format_timestamp(data["timestamp"])
    message = json.dumps(data)

    # Async for each client
    send_tasks = []

    disconnected = set()
    for client in clients:
        send_tasks.append(_safe_send(client, message, disconnected))

    await asyncio.gather(*send_tasks, return_exceptions=True)
    clients.difference_update(disconnected)


async def _safe_send(client, message, disconnected):
    try:
        await client.send(message)
    except Exception:
        disconnected.add(client)
