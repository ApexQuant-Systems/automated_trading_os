# Component Manifest Contract Header
__module_name__ = "global_architecture_configuration"
__build_version__ = "0.1.0-stable"
__spec_contract_hash__ = "0x00_project_config_core"
__regression_suite_hash__ = "0x00_project_config_verify"

class ProjectConfiguration:
    """Immutable parameter bank managing multi-market watches, strategy horizons, and risk thresholds."""

    def __init__(self):
        # 1. Broad Institutional Watchlist Universe Boundaries Definition
        self.FAVOURITED_ASSETS = {
            "CRYPTO": ["BTCUSD", "ETHUSD", "SOLUSD", "LINKUSD"],
            "FOREX": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"],
            "METALS": ["XAUUSD", "XAGUSD"],
            "INDICES": ["NAS100", "SPX500"]
        }

        # 2. Strict Fractal Timeframe Hierarchies Mapping for the 4 Operational Sets
        self.STRATEGY_SETS = {
            "SET_1_INVESTING": {
                "DESCRIPTION": "Macro Portfolio Horizons",
                "HTF": "1M", "MTF": "1W", "LTF": "1D"
            },
            "SET_2_POSITIONAL": {
                "DESCRIPTION": "Weekly Swing Horizons",
                "HTF": "1W", "MTF": "1D", "LTF": "4H"
            },
            "SET_3_SWING": {
                "DESCRIPTION": "Intraday Swing Horizons",
                "HTF": "1D", "MTF": "4H", "LTF": "1H"
            },
            "SET_4_INTRADAY": {
                "DESCRIPTION": "Intraday Scalping Horizons",
                "HTF": "4H", "MTF": "1H", "LTF": "15M"
            }
        }

        # 3. Capital Supremacy Preservation & Risk Circuit Parameters
        self.RISK_LIMITS = {
            "MAX_POSITION_RISK_PCT": 0.01,       # Strict 1% treasury exposure rule per trade plan
            "MAX_DAILY_DRAWDOWN_PCT": 0.03,      # 3% Maximum rolling 24-hour portfolio cap
            "MAX_WEEKLY_DRAWDOWN_PCT": 0.06,     # 6% Maximum rolling 7-day portfolio cap
            "MAX_SYSTEMIC_DRAWDOWN_PCT": 0.10,   # 10% Absolute terminal equity freeze circuit
            "MIN_RISK_REWARD_RATIO": 4.0         # Absolute 1:4 minimum target requirement barrier
        }

        # 4. Macro Causal Economic News Event Protection Parameters
        self.NEWS_FILTER_GATES = {
            "HIGH_IMPACT_EVENTS": ["FOMC", "NFP", "CPI", "INTEREST_RATE_DECISION"],
            "RESTRICTIVE_WINDOW_MINUTES": 30     # Operational pause scale prior to and post-release
        }

        # 5. Infrastructure Relational Key Constraints Store
        self.DATABASE = {
            "PRIMARY_PATH": "data/storage/apex_warehouse.db",
            "TESTING_SCHEMA_PATH": "data/storage/sandbox_warehouse.db"
        }

    def fetch_all_symbols(self) -> list:
        """Flattens sector categories to pull the entire monitored ecosystem watchlist."""
        symbols = []
        for asset_class in self.FAVOURITED_ASSETS.values():
            symbols.extend(asset_class)
        return symbols

project_config = ProjectConfiguration()
