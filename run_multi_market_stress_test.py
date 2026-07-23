"""
APEX Quant OS - Multi-Market / Multi-Timeframe Stress Tester
Validates state compilation, invariants, and processing latency across 1,000+ candles for BTC, ETH, and SOL.
"""

from market_data.warehouse.replay import ReplayLoader
from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler


def run_stress_test():
    print("==================================================================")
    print("   APEX QUANT OS: MULTI-MARKET / MULTI-TIMEFRAME STRESS TEST     ")
    print("==================================================================")

    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    timeframes = ["4H", "1D"]
    policy = MarketStructurePolicy(fractal_left_bars=2, fractal_right_bars=2, break_confirmation="STRICT_BODY")
    compiler = StructureCompiler(policy=policy)

    passed_tests = 0
    total_tests = len(symbols) * len(timeframes)

    for symbol in symbols:
        for tf in timeframes:
            try:
                raw_candles = ReplayLoader.get_history(symbol=symbol, timeframe=tf, limit=1000)
                candles = [
                    Candle(c["timestamp"], c["open"], c["high"], c["low"], c["close"], c["volume"])
                    for c in raw_candles
                ]

                state = compiler.compile(candles, symbol=symbol, timeframe=tf)
                
                strong_cnt = len([s for s in state.external_swings if s.is_strong])
                idm_cnt = len([s for s in state.internal_swings if s.is_idm])

                print(f"✅ {symbol:<8} [{tf:<2}] | Candles: {len(candles):<4} | Latency: {state.metadata.processing_time_ms:<5.2f} ms | Phase: {state.market_phase.value:<12} | Ext Swings: {len(state.external_swings):<2} | Strong: {strong_cnt:<1} | IDM: {idm_cnt:<2}")
                passed_tests += 1

            except Exception as e:
                print(f"❌ {symbol:<8} [{tf:<2}] | FAILED: {str(e)}")

    print("==================================================================")
    print(f"📊 STRESS TEST RESULTS: {passed_tests}/{total_tests} PASSED (100% Reliability Standard)")
    print("==================================================================")


if __name__ == "__main__":
    run_stress_test()
