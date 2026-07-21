# market_state/engine/primitives.py

class PrimitiveEngine:
    def __init__(self, config):
        self.config = config

    def classify(self, candles: list[dict]) -> list[dict]:
        """
        Input: Raw Candle OHLCV
        Output: Candles decorated with primitive flags 
                (e.g., is_displacement, is_inside_bar)
        """
        # Placeholder for implementation
        return candles
