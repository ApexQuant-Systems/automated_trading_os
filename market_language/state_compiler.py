"""
APEX Quant OS - Domain 1: Unified MarketState Compiler (v3.6.0)
Wires frozen engine APIs into an immutable MarketState snapshot.
"""

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.key_levels import KeyLevelsEngine, KeyLevel
from market_language.key_zones import KeyZonesEngine, PriceZone
from market_language.market_structure.phase_engine import MarketPhase, PhaseEngine


@dataclass(frozen=True)
class MarketState:
    """
    Immutable, single-source-of-truth snapshot of objective market facts.
    """

    symbol: str
    timeframe: str
    last_timestamp: int
    last_close: float
    
    # 1. Structure State Snapshot
    structure: Any
    
    # 2. Key Levels (Liquidity Pools)
    equal_levels: Tuple[KeyLevel, ...]
    htf_levels: Tuple[KeyLevel, ...]
    
    # 3. Key Zones (Imbalances & Supply/Demand)
    fair_value_gaps: Tuple[PriceZone, ...]
    order_blocks: Tuple[PriceZone, ...]
    
    # 4. Market Phase & Equilibrium State
    phase: MarketPhase
    is_premium: bool
    is_discount: bool


class Domain1Compiler:
    """
    Master compiler executing the complete Domain 1 Market Language pipeline.
    """

    def __init__(self, policy: Optional[MarketStructurePolicy] = None):
        self.policy = policy or MarketStructurePolicy()
        self.structure_compiler = StructureCompiler(policy=self.policy)

    def compile(self, candles: List[Candle], symbol: str = "BTCUSDT", timeframe: str = "1H") -> MarketState:
        if not candles:
            raise ValueError("Cannot compile MarketState from empty candle list.")

        last_candle = candles[-1]

        # 1. Compile Core Market Structure & Anchors
        struct_state = self.structure_compiler.compile(candles, symbol=symbol, timeframe=timeframe)

        # 2. Extract Key Levels
        equal_levels = tuple(KeyLevelsEngine.detect_equal_levels(list(struct_state.internal_swings)))
        htf_levels = tuple(KeyLevelsEngine.detect_htf_levels(candles))

        # 3. Extract Key Zones
        fvgs = tuple(KeyZonesEngine.detect_fair_value_gaps(candles))
        obs = tuple(KeyZonesEngine.detect_order_blocks(candles, list(struct_state.recent_events)))

        # 4. Classify Market Phase using Frozen API Signature
        current_phase = PhaseEngine.classify_phase(
            events=list(struct_state.recent_events),
            trend=struct_state.trend,
            anchors=struct_state.anchors,
            latest_price=last_candle.close
        )

        # 5. Evaluate Premium / Discount Position
        is_premium = False
        is_discount = False
        if struct_state.dealing_range:
            is_premium = last_candle.close > struct_state.dealing_range.equilibrium_price
            is_discount = last_candle.close < struct_state.dealing_range.equilibrium_price

        return MarketState(
            symbol=symbol,
            timeframe=timeframe,
            last_timestamp=last_candle.timestamp,
            last_close=last_candle.close,
            structure=struct_state,
            equal_levels=equal_levels,
            htf_levels=htf_levels,
            fair_value_gaps=fvgs,
            order_blocks=obs,
            phase=current_phase,
            is_premium=is_premium,
            is_discount=is_discount
        )
