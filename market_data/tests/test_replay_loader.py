import unittest
from market_data.warehouse.replay import ReplayLoader

class TestReplayLoader(unittest.TestCase):
    
    def test_limit_parameter(self):
        # Request exactly 5 candles
        data = ReplayLoader.get_history(symbol="BTCUSDT", timeframe="1D", limit=5)
        self.assertTrue(len(data) <= 5, "ReplayLoader failed to respect the limit parameter.")
        
    def test_chronological_ordering(self):
        data = ReplayLoader.get_history(symbol="BTCUSDT", timeframe="1D", limit=10)
        if len(data) > 1:
            for i in range(1, len(data)):
                self.assertTrue(
                    data[i]["timestamp"] > data[i-1]["timestamp"], 
                    "ReplayLoader returned out-of-order timestamps!"
                )
                
    def test_invalid_symbol_handling(self):
        # Should return an empty list, not crash
        data = ReplayLoader.get_history(symbol="FAKECRYPTO", timeframe="1D")
        self.assertEqual(len(data), 0)
        
    def test_schema_formatting(self):
        data = ReplayLoader.get_history(symbol="BTCUSDT", timeframe="1D", limit=1)
        if data:
            candle = data[0]
            required_keys = ["timestamp", "open", "high", "low", "close", "volume"]
            for key in required_keys:
                self.assertIn(key, candle, f"ReplayLoader missing required key: {key}")

if __name__ == "__main__":
    unittest.main()
