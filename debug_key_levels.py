"""
APEX Quant OS - Diagnostic Inspector for Key Levels
Inspects detected internal swings and EQH/EQL outputs.
"""

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.key_levels import KeyLevelsEngine, LevelType


def debug_key_levels():
    print("==================================================================")
    print("   APEX QUANT OS: KEY LEVELS DIAGNOSTIC INSPECTOR                 ")
    print("==================================================================")

    candles = [
        Candle(1000, 100.0, 110.0, 99.0, 108.0, 100),
        Candle(2000, 108.0, 107.0, 95.0, 96.0, 100),   # Low 1 @ 95.0
        Candle(3000, 96.0, 120.0, 96.0, 118.0, 100),  # High 1 @ 120.0
        Candle(4000, 118.0, 117.0, 95.02, 96.0, 100), # Low 2 @ 95.02
        Candle(5000, 96.0, 120.03, 95.5, 119.0, 100), # High 2 @ 120.03 (Last Bar)
    ]

    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    print("\n1. DETECTED INTERNAL SWINGS:")
    for s in state.internal_swings:
        print(f"   Bar {s.candle_index} | Type: {s.orientation.value:<4} | Price: {s.price_point.price:.2f}")

    levels = KeyLevelsEngine.detect_equal_levels(list(state.internal_swings), tolerance_pct=0.001)
    
    print("\n2. KEY LEVELS GENERATED:")
    for l in levels:
        print(f"   Type: {l.level_type.value:<4} | Price: {l.price:.2f}")

    print("==================================================================")


if __name__ == "__main__":
    debug_key_levels()
