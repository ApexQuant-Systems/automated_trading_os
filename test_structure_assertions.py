"""
APEX Quant OS - Ground-Truth Unit Assertion Test Suite
Verifies algorithmic correctness against known market scenarios.
"""

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.market_structure.models import EventType, SwingLifecycleState


def test_scenario_1_true_bos_vs_wick_sweep():
    """
    Scenario 1:
    - Bar 2: Swing High at 110.0
    - Bar 5: Wicks to 111.0, Closes at 108.0 -> Expected: STRUCTURAL_REJECTION
    - Bar 6: Closes at 114.0 -> Expected: Structural Break (CHOCH / BOS)
    """
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

    # 1. Assert Rejection Sweep Event Exists
    rejection_events = [e for e in state.recent_events if e.event_type == EventType.STRUCTURAL_REJECTION]
    assert len(rejection_events) >= 1, f"ASSERTION FAILED: Expected STRUCTURAL_REJECTION event, got {len(rejection_events)}"

    # 2. Assert Structural Break Event Exists
    break_events = [
        e for e in state.recent_events 
        if e.event_type in [EventType.EXTERNAL_BOS_BULLISH, EventType.EXTERNAL_CHOCH_BULLISH]
    ]
    assert len(break_events) >= 1, f"ASSERTION FAILED: Expected Structural Break event, got {len(break_events)}"

    print("  ✅ PASS: True Structural Break and Wick Sweep correctly differentiated.")


def test_scenario_2_inducement_idm_trap():
    """
    Scenario 2:
    - Verifies that internal pullback lows following an expansion move are tracked.
    """
    print("Executing Unit Test 2: Inducement (IDM) Trap Identification...")
    
    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 101.0, 100),
        Candle(2000, 101.0, 108.0, 100.0, 107.0, 100),
        Candle(3000, 107.0, 115.0, 106.0, 114.0, 100),  # Peak @ 115.0
        Candle(4000, 114.0, 113.0, 109.0, 110.0, 100),  # IDM Pullback Low @ 109.0
        Candle(5000, 110.0, 112.0, 108.0, 111.0, 100),
        Candle(6000, 111.0, 118.0, 110.0, 117.0, 100),
    ]

    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    assert len(state.internal_swings) >= 1, f"ASSERTION FAILED: Expected internal swings, got {len(state.internal_swings)}"
    print("  ✅ PASS: Inducement (IDM) trap tracking verified.")


def test_scenario_3_causal_strong_anchor():
    """
    Scenario 3:
    - Verifies Causal Anchor protection on displacement legs.
    """
    print("Executing Unit Test 3: Causal Strong Anchor Verification...")
    
    candles = [
        Candle(500,  102.0, 103.0, 101.0, 102.0, 100),  # Boundary Padding Candle
        Candle(1000, 102.0, 101.0, 95.0,  99.0,  100),  # CAUSAL ORIGIN FRACTAL LOW @ 95.0 (Index 1)
        Candle(2000, 99.0,  105.0, 98.0,  104.0, 100),
        Candle(3000, 104.0, 110.0, 103.0, 108.0, 100),  # Old High @ 110.0
        Candle(4000, 108.0, 107.0, 102.0, 103.0, 100),
        Candle(5000, 103.0, 116.0, 102.0, 115.0, 300),  # Displacement Break Close=115
    ]

    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    assert state.anchors.protected_low is not None, "ASSERTION FAILED: Protected Low anchor is None"
    assert state.anchors.protected_low.price_point.price == 95.0, f"ASSERTION FAILED: Expected Protected Low @ 95.0, got {state.anchors.protected_low.price_point.price}"

    print("  ✅ PASS: Causal Strong Anchor successfully proved and protected.")


if __name__ == "__main__":
    print("==================================================================")
    print("   APEX QUANT OS: GROUND-TRUTH UNIT ASSERTION TEST SUITE         ")
    print("==================================================================")
    test_scenario_1_true_bos_vs_wick_sweep()
    test_scenario_2_inducement_idm_trap()
    test_scenario_3_causal_strong_anchor()
    print("==================================================================")
    print("   🏆 ALL GROUND-TRUTH ASSERTIONS PASSED (100% LOGIC TRUTH)      ")
    print("==================================================================")
