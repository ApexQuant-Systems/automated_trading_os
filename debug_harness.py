"""
APEX Quant OS - Surgical Pipeline Diagnostic Harness
Inspects intermediate states for Scenario 1 without altering production code.
"""

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler

def debug_scenario_1():
    print("==================================================================")
    print("   APEX QUANT OS: PIPELINE DIAGNOSTIC INSPECTOR (SCENARIO 1)      ")
    print("==================================================================")

    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 101.0, 100),
        Candle(2000, 101.0, 106.0, 100.0, 105.0, 100),
        Candle(3000, 105.0, 110.0, 104.0, 108.0, 100),  # Bar 2: High @ 110.0
        Candle(4000, 108.0, 107.0, 102.0, 103.0, 100),
        Candle(5000, 103.0, 105.0, 101.0, 102.0, 100),
        Candle(6000, 102.0, 111.0, 101.0, 108.0, 100),  # Bar 5: Wick=111.0, Close=108.0
        Candle(7000, 108.0, 115.0, 107.0, 114.0, 200),  # Bar 6: Close=114.0
    ]

    policy = MarketStructurePolicy(fractal_left_bars=2, fractal_right_bars=2, break_confirmation="STRICT_BODY")
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    print("\n1. CANDLES INGESTED:")
    for idx, c in enumerate(candles):
        print(f"   Bar {idx} | High: {c.high:>5.1f} | Low: {c.low:>5.1f} | Close: {c.close:>5.1f}")

    print("\n2. INTERNAL SWINGS DETECTED:")
    for s in state.internal_swings:
        print(f"   Index: {s.candle_index} | Type: {s.orientation.value:<4} | Price: {s.price_point.price:.1f}")

    print("\n3. EXTERNAL SWINGS PROMOTED:")
    for s in state.external_swings:
        print(f"   Index: {s.candle_index} | Type: {s.orientation.value:<4} | Price: {s.price_point.price:.1f} | Lifecycle: {s.lifecycle.value}")

    print("\n4. EVENTS GENERATED:")
    for e in state.recent_events:
        print(f"   Type: {e.event_type.value:<25} | Trigger Price: {e.trigger_price:.1f}")

    print("==================================================================")

if __name__ == "__main__":
    debug_scenario_1()
