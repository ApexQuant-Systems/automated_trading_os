# market_state/market_state_engine.py
# Core Orchestrator: Market State Engine v1.0
# Responsibility: Pipeline management only. Logic lives in engine/ folder.

from market_state.engine.primitives import PrimitiveEngine
from market_state.engine.swings import SwingEngine
from market_state.engine.structure import StructureEngine
from market_state.engine.liquidity import LiquidityEngine
from market_state.engine.zones import ZoneEngine
from market_state.engine.phases import PhaseEngine
from market_state.engine.compiler import StateCompiler

class StatelessMarketStateEngine:
    def __init__(self, config):
        self.config = config
        self.primitives = PrimitiveEngine(config)
        self.swings = SwingEngine(config)
        self.structure = StructureEngine(config)
        self.liquidity = LiquidityEngine(config)
        self.zones = ZoneEngine(config)
        self.phases = PhaseEngine(config)
        self.compiler = StateCompiler(config)

    def process(self, candles: list[dict]) -> dict:
        """The pipeline: Pipeline flows from raw data to MarketState object."""
        primitives = self.primitives.classify(candles)
        swings = self.swings.extract(primitives)
        structure = self.structure.detect(primitives, swings)
        liquidity = self.liquidity.detect(primitives, swings)
        zones = self.zones.map(primitives, structure)
        phase = self.phases.resolve(structure, trend=structure["trend"])
        
        return self.compiler.compile(primitives, swings, structure, liquidity, zones, phase)
