import json
from typing import Set
import websockets
from app.utils.time_format import format_timestamp

clients: Set[websockets.WebSocketServerProtocol] = set()

# Broadcast message to all the clients connected
async def broadcast(candle):
    if not clients:
        return
    
    data = candle.to_dict()
    data["timestamp"] = format_timestamp(data["timestamp"])
    message = json.dumps(data)

    disconnected = set()
    for client in clients:
        try:
            await client.send(message)
        except:
            disconnected.add(client)
    clients.difference_update(disconnected)