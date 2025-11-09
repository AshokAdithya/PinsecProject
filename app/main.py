import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.config.binance_symbols import fetch_testnet_symbols
from app.websocket.server import start_ws_server
from app.binance.client import BinanceClient
from app.utils.logger import logger
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# Main REST API - FastAPI
server_ip = os.getenv("SERVER_IP")
server_port = os.getenv("SERVER_PORT")

# On startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup phase
    logger.info("STARTING CRYPTO PRICE STREAMING PLATFORM")
    
    await fetch_testnet_symbols()
    asyncio.create_task(start_ws_server())
    client = BinanceClient(max_retries = 5, base_delay = 3)
    asyncio.create_task(client.run_forever()) 

    yield

    #  when shutdown
    logger.info("SHUTTING DOWN CRYPTO PRICE STREAMING PLATFORM")

app = FastAPI(
    title="Crypto Price Streaming Platform",
    description="Real-time 1s OHLC, Tick from Binance Testnet",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

# Check endpoint
@app.get("/")
async def root():
    return {"message": "Crypto Price Streaming Platform is active"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host=server_ip,      
        port=int(server_port),         
        reload=False        
    )