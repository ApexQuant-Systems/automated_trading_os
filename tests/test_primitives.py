import unittest
from market_state.engine.primitives import PrimitiveEngine

class TestPrimitiveEngine(unittest.TestCase):
    def setUp(self):
        self.config = {"volatility_multiplier": 2.0}
        self.engine = PrimitiveEngine(self.config)

    def test_displacement_logic(self):
        # We will add logic here to test if a displacement candle is correctly identified
        candles = [
            {"open": 100, "close": 110}, # Placeholder
        ]
        results = self.engine.classify(candles)
        # self.assertTrue(results[0]['is_displacement'])
        pass

if __name__ == "__main__":
    unittest.main()
