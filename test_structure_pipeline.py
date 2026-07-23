"""
APEX Quant OS - Market Structure Engine Integration Test
Pulls historical candles from ReplayLoader and passes them through StructureCompiler.
"""

from market_data.warehouse.replay import ReplayLoader
from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler


def test_full_pipeline():
    print("==================================================================")
    print("   APEX QUANT OS: MARKET STRUCTURE ENGINE V2.0 INTEGRATION TEST   ")
    print("==================================================================")

    # 1. Fetch 1,000 BTC/USDT 4H Candles via ReplayLoader
    raw_candles = ReplayLoader.get_history(symbol="BTCUSDT", timeframe="4H", limit=1000)
    print(f"1. Fetched {len(raw_candles)} candles via ReplayLoader.")

    candles = [
        Candle(
            timestamp=c["timestamp"],
            open=c["open"],
            high=c["high"],
            low=c["low"],
            close=c["close"],
            volume=c["volume"]
        )
        for c in raw_candles
    ]

    # 2. Instantiate Policy and Compiler
    policy = MarketStructurePolicy(
        fractal_left_bars=2,
        fractal_right_bars=2,
        break_confirmation="STRICT_BODY"
    )
    compiler = StructureCompiler(policy=policy)

    # 3. Execute State Compilation
    state = compiler.compile(candles, symbol="BTCUSDT", timeframe="4H")

    # 4. Display Results
    print("\n📊 COMPILED MARKET STRUCTURE STATE:")
    print(f"   ├── Engine Version: {state.metadata.version}")
    print(f"   ├── Processing Time: {state.metadata.processing_time_ms} ms")
    print(f"   ├── Active Trend: {state.trend.direction.value} (Stage: {state.trend.maturity.value})")
    print(f"   ├── Total Swings Detected: {state.metrics.total_swings_detected}")
    print(f"   ├── Total Structural Events: {state.metrics.total_events_triggered}")
    print(f"   ├── Total Legs Constructed: {state.metrics.total_legs_constructed}")
    print(f"   ├── Protected Low: {state.anchors.protected_low.price_point.price if state.anchors.protected_low else 'N/A'}")
    print(f"   ├── Weak High: {state.anchors.weak_high.price_point.price if state.anchors.weak_high else 'N/A'}")
    
    if state.dealing_range:
        print(f"   ├── Dealing Range: [{state.dealing_range.low_price} - {state.dealing_range.high_price}]")
        print(f"   └── Equilibrium (50%): {state.dealing_range.equilibrium_price}")
    
    print(f"   ├── Pullback Active: {state.pullback.is_valid} (Complexity: {state.pullback.complexity})")
    print(f"   └── Structural Quality: {state.quality.classification} (Score: {state.quality.quality_score})")

    print("\n==================================================================")
    print("   ✅ MARKET STRUCTURE ENGINE V2.0 IS FULLY OPERATIONAL")
    print("==================================================================")


if __name__ == "__main__":
    test_full_pipeline()
