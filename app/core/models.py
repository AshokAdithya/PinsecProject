from dataclasses import dataclass
from typing import Dict

@dataclass
class Tick:
    symbol: str
    price: float
    qty: float
    timestamp: int  # ms

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "qty": self.qty,
            "timestamp": self.timestamp
        }

@dataclass
class Candle:
    symbol: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close
        }