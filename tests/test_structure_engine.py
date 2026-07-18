import unittest
import json
from market_data.structure_engine import DeterministicStructureEngine

class TestDeterministicStructureEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DeterministicStructureEngine()
        self.config = {
            "market_ontology_parameters": {
                "floating_point_epsilon": 1e-8,
                "timeframe_swing_windows": {"15m": 2, "1h": 2}
            }
        }

    def test_wick_sweep_false_positive_filter(self):
        """Test Case 5: Verify that wicks penetrating range extremes do NOT alter structure without body closes."""
        mock_candles = [
            {"timestamp": 100, "open": 90.0, "high": 95.0,  "low": 89.0, "close": 94.0, "volume": 100},
            {"timestamp": 200, "open": 94.0, "high": 100.0, "low": 93.0, "close": 98.0, "volume": 100}, # Major boundary anchor
            {"timestamp": 300, "open": 98.0, "high": 104.0, "low": 95.0, "close": 99.5, "volume": 100}  # Wick sweep high but close inside
        ]
        
        mock_swings = [
            {
                "swing_id": "MOCK-HIGH-200", "timestamp": 200, "swing_type": "HIGH", "price": 100.0,
                "confirmed_at_ts": 200, "status": "DISCOVERED", "classification": "EXTERNAL_MAJOR",
                "window_meta": {"configured_n": 2, "left_window_actual": 2, "right_window_actual": 2}
            },
            {
                "swing_id": "MOCK-LOW-100", "timestamp": 100, "swing_type": "LOW", "price": 89.0,
                "confirmed_at_ts": 100, "status": "DISCOVERED", "classification": "EXTERNAL_MAJOR",
                "window_meta": {"configured_n": 2, "left_window_actual": 2, "right_window_actual": 2}
            }
        ]
        
        classified = self.engine.classify_swings(mock_swings, self.config, "15m")
        output = self.engine.process_structure("BTCUSDT", "15M", mock_candles, classified, self.config)
        
        # Verify strict structural enforcement rule: 0 events recorded
        self.assertEqual(len(output["events"]), 0)
        self.assertEqual(output["trend"]["current_regime"], "RANGE")

    def test_deterministic_choch_trend_reversal(self):
        """Test Case 2: Verify that valid body close penetrations cleanly flip structural trend parameters."""
        mock_candles = [
            {"timestamp": 100, "open": 140.0, "high": 150.0, "low": 139.0, "close": 145.0, "volume": 100}, # High anchor
            {"timestamp": 200, "open": 145.0, "high": 146.0, "low": 120.0, "close": 122.0, "volume": 100}, # Low anchor
            {"timestamp": 300, "open": 122.0, "high": 153.0, "low": 121.0, "close": 151.5, "volume": 100}  # Confirmed body close breakout
        ]
        
        mock_swings = [
            {
                "swing_id": "SWING-H-100", "timestamp": 100, "swing_type": "HIGH", "price": 150.0,
                "confirmed_at_ts": 100, "status": "DISCOVERED", "classification": "EXTERNAL_MAJOR",
                "window_meta": {"configured_n": 2}
            },
            {
                "swing_id": "SWING-L-200", "timestamp": 200, "swing_type": "LOW", "price": 120.0,
                "confirmed_at_ts": 200, "status": "DISCOVERED", "classification": "EXTERNAL_MAJOR",
                "window_meta": {"configured_n": 2}
            }
        ]
        
        classified = self.engine.classify_swings(mock_swings, self.config, "15m")
        output = self.engine.process_structure("BTCUSDT", "15M", mock_candles, classified, self.config)
        
        # Inversion assertions mapping to the frozen blueprint logic rules
        self.assertEqual(len(output["events"]), 1)
        self.assertEqual(output["events"][0]["event_type"], "CHOCH")
        self.assertEqual(output["events"][0]["direction"], "BULLISH")
        self.assertEqual(output["trend"]["current_regime"], "BULLISH")

if __name__ == "__main__":
    unittest.main()
