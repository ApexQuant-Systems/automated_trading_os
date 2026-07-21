from dataclasses import dataclass

@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    # Flags populated by CandleAnalyzer
    is_displacement: bool = False
    is_inside: bool = False
    is_outside: bool = False
    is_doji: bool = False
