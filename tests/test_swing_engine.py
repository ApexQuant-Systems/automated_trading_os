import unittest
import json
from market_data.swing_engine import DynamicSwingFactEngine

class TestDynamicSwingFactEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DynamicSwingFactEngine()
        # Load production configuration matrix values
        with open("config/trading_settings.json", "r") as f:
            self.config = json.load(f)

    def test_plateau_high_invariant_displacement(self):
        """Regression Test A: Confirms that plateau structures resolve to a single maximum record via displacement."""
        mock_candles = [
            {"timestamp": 1782825600, "open": 100.0, "high": 100.0, "low": 99.0,  "close": 100.0, "volume": 100.0},
            {"timestamp": 1782826500, "open": 100.0, "high": 105.0, "low": 102.0, "close": 104.0, "volume": 150.0},
            {"timestamp": 1782827400, "open": 104.0, "high": 105.0, "low": 103.0, "close": 104.0, "volume": 300.0},
            # Index 3: Has largest subsequent downward vector expansion drop down to 101/92
            {"timestamp": 1782828300, "open": 104.0, "high": 105.0, "low": 101.0, "close": 102.0, "volume": 120.0},
            {"timestamp": 1782829200, "open": 102.0, "high": 101.0, "low": 90.0,  "close": 91.0,  "volume": 400.0},
            {"timestamp": 1782830100, "open": 91.0,  "high": 92.0,  "low": 88.0,  "close": 89.0,  "volume": 200.0}
        ]
        
        results = self.engine.calculate_swings("BTCUSDT", "15M", "PLAT-TEST-JOB", mock_candles, self.config)
        
        # Verify strict single extraction contract
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["timestamp"], 1782828300)
        self.assertEqual(results[0]["swing_type"], "HIGH")
        self.assertEqual(results[0]["status"], "DISCOVERED")
        self.assertEqual(results[0]["confirmed_at_ts"], 1782830100)

    def test_realtime_streaming_confirmation_gate(self):
        """Regression Test B: Confirms that look-ahead bias is barred and facts expose only at index i+N."""
        mock_candles = [
            {"timestamp": 1782825600, "open": 100.0, "high": 102.0, "low": 99.0,  "close": 101.0, "volume": 150.0},
            {"timestamp": 1782826500, "open": 101.0, "high": 104.0, "low": 100.0, "close": 103.0, "volume": 200.0},
            {"timestamp": 1782827400, "open": 103.0, "high": 108.0, "low": 102.0, "close": 106.0, "volume": 350.0}, # Apex i
            {"timestamp": 1782828300, "open": 106.0, "high": 103.5, "low": 101.0, "close": 102.0, "volume": 180.0}, # i+1
            {"timestamp": 1782829200, "open": 102.0, "high": 101.0, "low": 98.0,  "close": 99.0,  "volume": 120.0}  # i+N Confirmation
        ]
        
        # Step 1: Simulate stream context prior to confirmation close
        partial_stream_1 = mock_candles[:4]
        res_1 = self.engine.calculate_swings("BTCUSDT", "15M", "STREAM-JOB", partial_stream_1, self.config)
        self.assertEqual(len(res_1), 0)
        
        # Step 2: Feed the confirmation bar
        res_2 = self.engine.calculate_swings("BTCUSDT", "15M", "STREAM-JOB", mock_candles, self.config)
        self.assertEqual(len(res_2), 1)
        self.assertEqual(res_2[0]["timestamp"], 1782827400)
        self.assertEqual(res_2[0]["confirmed_at_ts"], 1782829200)

    def test_missing_data_discontinuity_outage(self):
        """Regression Test C: Asserts that gaps breaking timeframe intervals reset windows cleanly with zero phantom lines."""
        mock_candles = [
            {"timestamp": 1782825600, "open": 100.0, "high": 100.0, "low": 95.0, "close": 99.0, "volume": 100.0},
            {"timestamp": 1782826500, "open": 99.0,  "high": 102.0, "low": 98.0, "close": 101.0, "volume": 120.0},
            {"timestamp": 1782827400, "open": 101.0, "high": 106.0, "low": 100.0, "close": 105.0, "volume": 150.0}, # Peak i
            # Giga Timeline Discontinuity Gap Intercept (7200s vs 900s baseline expected steps)
            {"timestamp": 1782834600, "open": 105.0, "high": 101.0, "low": 97.0, "close": 98.0, "volume": 110.0},
            {"timestamp": 1782835500, "open": 98.0,  "high": 99.0,  "low": 96.0, "close": 97.0, "volume": 130.0}
        ]
        
        results = self.engine.calculate_swings("BTCUSDT", "15M", "OUTAGE-JOB", mock_candles, self.config)
        
        # Assert tracking buffer reset drop: Index 2 cannot collect future lookahead frames across the gap
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()
