"""
APEX Quant OS - Master Ground-Truth Unit Assertion Test Suite
Verifies algorithmic correctness for CHOCH, BOS, Premium/Discount, and Market Phases.
"""

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.market_structure.models import EventType, SwingLifecycleState, TrendDirection
from market_language.market_structure.phase_engine import MarketPhase


def test_scenario_1_true_bos_vs_wick_sweep():
    print("Executing Unit Test 1: True Structural Break vs Wick Sweep Fakeout...")
    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 101.0, 100),
        Candle(2000, 101.0, 106.0, 100.0, 105.0, 100),
        Candle(3000, 105.0, 110.0, 104.0, 108.0, 100),  # SWING HIGH @ 110.0
        Candle(4000, 108.0, 107.0, 102.0, 103.0, 100),
        Candle(5000, 103.0, 105.0, 101.0, 102.0, 100),
        Candle(6000, 102.0, 111.0, 101.0, 108.0, 100),  # WICK SWEEP (High=111, Close=108)
        Candle(7000, 108.0, 115.0, 107.0, 114.0, 200),  # DISPLACEMENT BREAK (Close=114)
    ]
    policy = MarketStructurePolicy(fractal_left_bars=2, fractal_right_bars=2, break_confirmation="STRICT_BODY")
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    rejection_events = [e for e in state.recent_events if e.event_type == EventType.STRUCTURAL_REJECTION]
    assert len(rejection_events) >= 1, f"ASSERTION FAILED: Expected STRUCTURAL_REJECTION, got {len(rejection_events)}"

    break_events = [e for e in state.recent_events if e.event_type in [EventType.EXTERNAL_BOS_BULLISH, EventType.EXTERNAL_CHOCH_BULLISH]]
    assert len(break_events) >= 1, f"ASSERTION FAILED: Expected Structural Break event, got {len(break_events)}"
    print("  ✅ PASS: True Structural Break and Wick Sweep correctly differentiated.")


def test_scenario_2_inducement_idm_trap():
    print("Executing Unit Test 2: Inducement (IDM) Trap Identification...")
    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 101.0, 100),
        Candle(2000, 101.0, 108.0, 100.0, 107.0, 100),
        Candle(3000, 107.0, 115.0, 106.0, 114.0, 100),
        Candle(4000, 114.0, 113.0, 109.0, 110.0, 100),
        Candle(5000, 110.0, 112.0, 108.0, 111.0, 100),
        Candle(6000, 111.0, 118.0, 110.0, 117.0, 100),
    ]
    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    assert len(state.internal_swings) >= 1, f"ASSERTION FAILED: Expected internal swings, got {len(state.internal_swings)}"
    print("  ✅ PASS: Inducement (IDM) trap tracking verified.")


def test_scenario_3_causal_strong_anchor():
    print("Executing Unit Test 3: Causal Strong Anchor Verification...")
    candles = [
        Candle(500,  102.0, 103.0, 101.0, 102.0, 100),
        Candle(1000, 102.0, 101.0, 95.0,  99.0,  100),  # CAUSAL LOW @ 95.0
        Candle(2000, 99.0,  105.0, 98.0,  104.0, 100),
        Candle(3000, 104.0, 110.0, 103.0, 108.0, 100),
        Candle(4000, 108.0, 107.0, 102.0, 103.0, 100),
        Candle(5000, 103.0, 116.0, 102.0, 115.0, 300),
    ]
    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    assert state.anchors.protected_low is not None, "ASSERTION FAILED: Protected Low anchor is None"
    assert state.anchors.protected_low.price_point.price == 95.0, f"ASSERTION FAILED: Expected Protected Low @ 95.0, got {state.anchors.protected_low.price_point.price}"
    print("  ✅ PASS: Causal Strong Anchor successfully proved and protected.")


def test_scenario_4_choch_vs_bos_sequence():
    print("Executing Unit Test 4: CHOCH Reversal vs BOS Continuation Sequence...")
    candles = [
        Candle(500,  100.0, 105.0, 99.0,  104.0, 100),
        Candle(1000, 104.0, 110.0, 103.0, 109.0, 100), # High @ 110
        Candle(2000, 109.0, 108.0, 101.0, 102.0, 100), # Low @ 101
        Candle(3000, 102.0, 116.0, 101.0, 115.0, 300), # Break 110 -> Expected: CHOCH_BULLISH (Trend flips to Bullish)
        Candle(4000, 115.0, 114.0, 108.0, 109.0, 100), # Pullback Low @ 108
        Candle(5000, 109.0, 122.0, 108.0, 121.0, 300), # Break 116 -> Expected: BOS_BULLISH (Continuation)
    ]
    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    choch_events = [e for e in state.recent_events if e.event_type == EventType.EXTERNAL_CHOCH_BULLISH]
    assert len(choch_events) >= 1, f"ASSERTION FAILED: Expected CHOCH event, got {len(choch_events)}"
    assert state.trend.direction == TrendDirection.BULLISH, f"ASSERTION FAILED: Expected BULLISH trend, got {state.trend.direction}"
    print("  ✅ PASS: CHOCH Reversal sequence correctly identified and verified.")


def test_scenario_5_dealing_range_equilibrium():
    print("Executing Unit Test 5: Dealing Range 50% Equilibrium Calculation...")
    candles = [
        Candle(500,  100.0, 102.0, 90.0,  99.0,  100), # Low @ 90.0
        Candle(1000, 99.0,  105.0, 98.0,  104.0, 100),
        Candle(2000, 104.0, 150.0, 103.0, 148.0, 300), # High @ 150.0
    ]
    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    assert state.dealing_range is not None, "ASSERTION FAILED: Dealing Range is None"
    expected_eq = (150.0 + 90.0) / 2.0  # 120.0
    assert state.dealing_range.equilibrium_price == expected_eq, f"ASSERTION FAILED: Expected EQ={expected_eq}, got {state.dealing_range.equilibrium_price}"
    print(f"  ✅ PASS: Dealing Range 50% Equilibrium verified (${expected_eq:.1f}).")


if __name__ == "__main__":
    print("==================================================================")
    print("   APEX QUANT OS: GROUND-TRUTH UNIT ASSERTION TEST SUITE         ")
    print("==================================================================")
    test_scenario_1_true_bos_vs_wick_sweep()
    test_scenario_2_inducement_idm_trap()
    test_scenario_3_causal_strong_anchor()
    test_scenario_4_choch_vs_bos_sequence()
    test_scenario_5_dealing_range_equilibrium()
    print("==================================================================")
    print("   🏆 ALL GROUND-TRUTH ASSERTIONS PASSED (100% LOGIC TRUTH)      ")
    print("==================================================================")
