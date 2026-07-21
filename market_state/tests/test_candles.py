import unittest
from market_state.analysis.candles import CandleDetector

class TestCandleDetector(unittest.TestCase):
    def test_inside_bar_detection(self):
        candles = [
            {"timestamp": 100, "open": 100, "high": 110, "low": 90, "close": 105, "volume": 100},
            {"timestamp": 101, "open": 102, "high": 108, "low": 92, "close": 104, "volume": 100} # Inside bar
        ]
        results = CandleDetector.detect(candles)
        self.assertTrue(results[1].is_inside)
        self.assertFalse(results[1].is_outside)

    def test_doji_detection(self):
        candles = [
            {"timestamp": 100, "open": 100, "high": 110, "low": 90, "close": 100.1, "volume": 100} # Doji
        ]
        results = CandleDetector.detect(candles)
        self.assertTrue(results[0].is_doji)

if __name__ == "__main__":
    unittest.main()
