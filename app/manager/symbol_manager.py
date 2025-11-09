from typing import Dict
from app.core.aggregator import SymbolAggregator
from app.core.broadcaster import broadcast
from app.core.models import Tick, Candle
import asyncio

class SymbolManager:
    def __init__(self):
        self.aggregators: Dict[str, SymbolAggregator] = {}
        self.latest_tick: Dict[str, Tick] = {}
        self.latest_candle: Dict[str, Candle] = {}

    # add symbol
    def add(self, symbol: str) -> bool:
        symbol = symbol.upper()
        if symbol in self.aggregators:
            return False
        self.aggregators[symbol] = SymbolAggregator(symbol, self._on_candle)
        return True

    # remove symbol
    def remove(self, symbol: str) -> bool:
        symbol = symbol.upper()
        if symbol in self.aggregators:
            del self.aggregators[symbol]
            self.latest_tick.pop(symbol, None)
            self.latest_candle.pop(symbol, None)
            return True
        return False

    # acts as a callable function
    def _on_candle(self, candle: Candle):
        self.latest_candle[candle.symbol] = candle
        asyncio.create_task(broadcast(candle))

    # processing the latest tick to get the correct 1s - OHLC
    def process_tick(self, tick: Tick):
        self.latest_tick[tick.symbol] = tick
        agg = self.aggregators.get(tick.symbol)
        if agg:
            agg.process_tick(tick)

    def get_tick(self, symbol: str):
        return self.latest_tick.get(symbol.upper())

    def get_candle(self, symbol: str):
        return self.latest_candle.get(symbol.upper())

    def list_symbols(self):
        return list(self.aggregators.keys())

manager = SymbolManager()