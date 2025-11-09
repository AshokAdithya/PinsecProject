from .models import Tick, Candle
from typing import Callable
import time

class SymbolAggregator:
    def __init__(self, symbol: str, on_candle: Callable[[Candle], None]):
        self.symbol = symbol.upper()
        self.on_candle = on_candle
        self.reset() 

    def reset(self):
        self.timestamp = None
        self.open = self.high = self.low = self.close = None

    def process_tick(self, tick: Tick):
        if tick.symbol != self.symbol:
            return

        sec = (tick.timestamp // 1000) * 1000
        if self.timestamp != sec:
            # If got a new second, finalize the old candle and return to websocket
            if self.timestamp is not None:
                self._emit()
            self.timestamp = sec
            self.open = self.high = self.low = self.close = tick.price
        else:
            self.high = max(self.high, tick.price)
            self.low = min(self.low, tick.price)
            self.close = tick.price

    def _emit(self):
        candle = Candle(self.symbol, self.timestamp, self.open, self.high, self.low, self.close)
        self.on_candle(candle)