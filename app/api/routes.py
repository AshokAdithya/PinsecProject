from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.config.binance_symbols import VALID_SYMBOLS, is_valid_symbol
from app.manager.symbol_manager import manager
from app.utils.logger import logger
from app.utils.time_format import format_timestamp
from app.utils.limiter import limiter

router = APIRouter()


class SymbolRequest(BaseModel):
    symbol: str


# Add new symbols
@router.post("/add_symbol")
@limiter.limit("10/second")
async def add_symbol(request: Request, req: SymbolRequest):
    sym = req.symbol.upper()

    # When symbols not in valid symbols
    if not is_valid_symbol(sym):
        raise HTTPException(status_code=400, detail=f"Invalid symbol: {sym}.")

    # Adding symbols
    if manager.add(sym):
        logger.info(f"Added symbol: {sym}")
        return {"message": f"Subscribed to {sym}", "symbol": sym}

    # If duplicate symbols
    raise HTTPException(status_code=400, detail=f"Symbol {sym} is already subscribed.")


# Remove symbols
@router.delete("/remove_symbol/{symbol}")
@limiter.limit("10/second")
async def remove_symbol(request: Request, symbol: str):
    if manager.remove(symbol):
        return {"message": f"Unsubscribed from {symbol.upper()}"}
    raise HTTPException(404, "Symbol not found")


# Get all using symbols
@router.get("/symbols")
@limiter.limit("10/second")
async def list_symbols(request: Request):
    return {"symbols": manager.list_symbols()}


# Response with latest snapshot of specified symbol
@router.get("/tick/{symbol}")
@limiter.limit("10/second")
async def get_latest_tick(request: Request, symbol: str):
    tick = manager.get_tick(symbol)
    if not tick:
        raise HTTPException(404, f"No tick data or not subscribed to {symbol}")
    data = tick.to_dict()

    if "timestamp" in data:
        data["timestamp"] = format_timestamp(data["timestamp"])

    return data


# Response with 1s - OHLC of specified symbol (THIS IS NOT WEBSOCKET)
@router.get("/ohlc/{symbol}")
@limiter.limit("10/second")
async def get_latest_ohlc(request: Request, symbol: str):
    candle = manager.get_candle(symbol)
    if not candle:
        raise HTTPException(404, f"No OHLC data or not subscribed to {symbol}")

    data = candle.to_dict()
    if "timestamp" in data:
        data["timestamp"] = format_timestamp(data["timestamp"])

    return data


# Available symbols / stocks
@router.get("/symbols/available")
@limiter.limit("10/second")
async def list_available(request: Request):
    return {"count": len(VALID_SYMBOLS), "symbols": sorted(VALID_SYMBOLS)}
