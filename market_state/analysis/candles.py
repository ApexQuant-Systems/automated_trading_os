from market_state.models.candle import Candle

class CandleDetector:
    @staticmethod
    def detect(candles: list[dict], atr_value: float = None) -> list[Candle]:
        """
        Input: Raw Candle dictionaries
        Output: Processed Candle models with primitive flags
        """
        processed = []
        for i, c in enumerate(candles):
            # Calculate basics
            body = abs(c['close'] - c['open'])
            candle_range = c['high'] - c['low']
            
            # Logic: Displacement (simplified placeholder for now)
            is_disp = body > (2.0 * atr_value) if atr_value else False
            
            # Logic: Inside/Outside Bars
            is_in, is_out = False, False
            if i > 0:
                prev = candles[i-1]
                is_in = c['high'] < prev['high'] and c['low'] > prev['low']
                is_out = c['high'] > prev['high'] and c['low'] < prev['low']
            
            # Logic: Doji (body < 5% of range)
            is_doji = body <= (0.05 * candle_range) if candle_range > 0 else True
            
            processed.append(Candle(
                timestamp=c['timestamp'],
                open=c['open'],
                high=c['high'],
                low=c['low'],
                close=c['close'],
                volume=c['volume'],
                is_displacement=is_disp,
                is_inside=is_in,
                is_outside=is_out,
                is_doji=is_doji
            ))
        return processed
