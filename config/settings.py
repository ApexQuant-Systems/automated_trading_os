# Component Manifest Contract Header
__module_name__ = "global_configuration_core"
__build_version__ = "4.0.0-stable"
__spec_contract_hash__ = "8f3b2361a998c_config"
__regression_suite_hash__ = "c24931a782b5e_config"

from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class AssetUniverse:
    """Core tracking universes managed independently by structural filters."""
    crypto_tier_1: Tuple[str, ...] = ("BTCUSD", "ETHUSD", "SOLUSD")
    forex_majors: Tuple[str, ...] = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF", "USDCAD")
    spot_metals: Tuple[str, ...] = ("XAUUSD", "XAGUSD")
    indices: Tuple[str, ...] = ("NAS100", "SPX500", "US30", "GER40")

@dataclass(frozen=True)
class TimeframeHorizons:
    """Multi-timeframe synchronization sets mapping historical data granularity."""
    set_1_macro: Tuple[str, ...] = ("1M", "1W", "1D")
    set_2_position: Tuple[str, ...] = ("1W", "1D", "4H")
    set_3_swing: Tuple[str, ...] = ("1D", "4H", "1H")
    set_4_intraday: Tuple[str, ...] = ("4H", "1H", "15M")

@dataclass(frozen=True)
class RiskFirewalls:
    """Absolute mathematical thresholds protecting system cash balances."""
    max_position_risk_pct: float = 0.01      # 1.0% maximum risk allocation per individual trade plan
    min_risk_reward_ratio: float = 4.0       # Minimum 1:4 risk-to-reward floor restriction
    max_daily_drawdown_pct: float = 0.03     # 3.0% cumulative rolling 24-hour drawdown ceiling
    max_weekly_drawdown_pct: float = 0.06    # 6.0% cumulative rolling 7-day drawdown ceiling
    max_systemic_drawdown_pct: float = 0.10  # 10.0% structural maximum equity high circuit drop

@dataclass(frozen=True)
class OperationalLimits:
    """Runtime limits tracking environment data purity and network overhead."""
    required_strategy_consensus: float = 0.70  # Minimum ensemble voter threshold
    min_market_quality_score: int = 60         # Participation filter metric cutoff index
    news_lockdown_window_mins: int = 30        # Protective temporal filter boundaries
    max_infrastructure_latency_ms: int = 250   # Absolute hardware response constraint

GLOBAL_ASSETS = AssetUniverse()
GLOBAL_TIMEFRAMES = TimeframeHorizons()
GLOBAL_RISK = RiskFirewalls()
GLOBAL_LIMITS = OperationalLimits()