# Component Manifest Contract Header
__module_name__ = "persistent_asset_registry"
__build_version__ = "1.6.0-stable"
__spec_contract_hash__ = "0x101_persistent_asset_core"
__regression_suite_hash__ = "0x101_persistent_asset_verify"

from typing import Dict, Any, List
from utils.database import db_manager

class PersistentAssetRegistry:
    """Manages structural definitions and seeding for the 15-market core research universe."""

    def __init__(self):
        self._static_universe = {
            # --- Tier 1: Crypto Assets ---
            "BTCUSDT": {
                "asset_class": "CRYPTO", "venue": "BINANCE", "provider": "BINANCE_VISION",
                "tick_size": 0.01, "price_precision": 2, "volume_precision": 5,
                "base_currency": "BTC", "quote_currency": "USDT", "trading_hours": "247"
            },
            "ETHUSDT": {
                "asset_class": "CRYPTO", "venue": "BINANCE", "provider": "BINANCE_VISION",
                "tick_size": 0.01, "price_precision": 2, "volume_precision": 4,
                "base_currency": "ETH", "quote_currency": "USDT", "trading_hours": "247"
            },
            "SOLUSDT": {
                "asset_class": "CRYPTO", "venue": "BINANCE", "provider": "BINANCE_VISION",
                "tick_size": 0.01, "price_precision": 2, "volume_precision": 3,
                "base_currency": "SOL", "quote_currency": "USDT", "trading_hours": "247"
            },
            # --- Tier 2: Forex Currency Majors ---
            "EURUSD": {
                "asset_class": "FOREX", "venue": "OTC", "provider": "DUKASCOPY",
                "tick_size": 0.00001, "price_precision": 5, "volume_precision": 2,
                "base_currency": "EUR", "quote_currency": "USD", "trading_hours": "FX_24H"
            },
            "GBPUSD": {
                "asset_class": "FOREX", "venue": "OTC", "provider": "DUKASCOPY",
                "tick_size": 0.00001, "price_precision": 5, "volume_precision": 2,
                "base_currency": "GBP", "quote_currency": "USD", "trading_hours": "FX_24H"
            },
            "USDJPY": {
                "asset_class": "FOREX", "venue": "OTC", "provider": "DUKASCOPY",
                "tick_size": 0.001, "price_precision": 3, "volume_precision": 2,
                "base_currency": "USD", "quote_currency": "JPY", "trading_hours": "FX_24H"
            },
            "AUDUSD": {
                "asset_class": "FOREX", "venue": "OTC", "provider": "DUKASCOPY",
                "tick_size": 0.00001, "price_precision": 5, "volume_precision": 2,
                "base_currency": "AUD", "quote_currency": "USD", "trading_hours": "FX_24H"
            },
            "USDCAD": {
                "asset_class": "FOREX", "venue": "OTC", "provider": "DUKASCOPY",
                "tick_size": 0.00001, "price_precision": 5, "volume_precision": 2,
                "base_currency": "USD", "quote_currency": "CAD", "trading_hours": "FX_24H"
            },
            # --- Tier 3: Spot Metals ---
            "XAUUSD": {
                "asset_class": "METALS", "venue": "OTC", "provider": "DUKASCOPY",
                "tick_size": 0.01, "price_precision": 2, "volume_precision": 2,
                "base_currency": "XAU", "quote_currency": "USD", "trading_hours": "METALS_23H"
            },
            "XAGUSD": {
                "asset_class": "METALS", "venue": "OTC", "provider": "DUKASCOPY",
                "tick_size": 0.001, "price_precision": 3, "volume_precision": 2,
                "base_currency": "XAG", "quote_currency": "USD", "trading_hours": "METALS_23H"
            },
            # --- Tier 4: Global Market Indices ---
            "NAS100": {
                "asset_class": "INDICES", "venue": "CME", "provider": "DUKASCOPY",
                "tick_size": 0.01, "price_precision": 2, "volume_precision": 2,
                "base_currency": "NAS", "quote_currency": "USD", "trading_hours": "INDEX_CHRONO"
            },
            "SPX500": {
                "asset_class": "INDICES", "venue": "CME", "provider": "DUKASCOPY",
                "tick_size": 0.01, "price_precision": 2, "volume_precision": 2,
                "base_currency": "SPX", "quote_currency": "USD", "trading_hours": "INDEX_CHRONO"
            },
            "US30": {
                "asset_class": "INDICES", "venue": "CBOT", "provider": "DUKASCOPY",
                "tick_size": 1.0, "price_precision": 0, "volume_precision": 2,
                "base_currency": "DJI", "quote_currency": "USD", "trading_hours": "INDEX_CHRONO"
            },
            "GER40": {
                "asset_class": "INDICES", "venue": "EUREX", "provider": "DUKASCOPY",
                "tick_size": 0.5, "price_precision": 1, "volume_precision": 2,
                "base_currency": "DAX", "quote_currency": "EUR", "trading_hours": "INDEX_CHRONO"
            },
            "UK100": {
                "asset_class": "INDICES", "venue": "ICE", "provider": "DUKASCOPY",
                "tick_size": 0.5, "price_precision": 1, "volume_precision": 2,
                "base_currency": "FTSE", "quote_currency": "GBP", "trading_hours": "INDEX_CHRONO"
            }
        }
        self.initialize_and_seed()

    def initialize_and_seed(self) -> int:
        """Seeds the persistent asset registry table if it is currently unpopulated."""
        seeded_count = 0
        with db_manager.metadata_db() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM asset_registry;")
            if cursor.fetchone()["count"] == 0:
                for symbol, meta in self._static_universe.items():
                    conn.execute("""
                        INSERT INTO asset_registry (
                            symbol, asset_class, venue, provider, tick_size, 
                            price_precision, volume_precision, base_currency, quote_currency, trading_hours
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        symbol, meta["asset_class"], meta["venue"], meta["provider"],
                        meta["tick_size"], meta["price_precision"], meta["volume_precision"],
                        meta["base_currency"], meta["quote_currency"], meta["trading_hours"]
                    ))
                    seeded_count += 1
        return seeded_count

    def verify_asset_exists(self, symbol: str) -> bool:
        """Queries the persistent metadata database to check asset registration status."""
        with db_manager.metadata_db() as conn:
            cursor = conn.execute("SELECT 1 FROM asset_registry WHERE symbol = ?;", (symbol.upper(),))
            return cursor.fetchone() is not None

    def get_asset(self, symbol: str) -> Dict[str, Any]:
        """Retrieves the complete structural parameter profile row for a target instrument."""
        with db_manager.metadata_db() as conn:
            cursor = conn.execute("SELECT * FROM asset_registry WHERE symbol = ?;", (symbol.upper(),))
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Asset Invalidation Exception: Ticker string '{symbol}' is completely unregistered.")
            return dict(row)

    def get_watchlist_by_class(self, asset_class: str) -> List[str]:
        """Extracts all matching symbol tokens filtered by a specific asset class."""
        with db_manager.metadata_db() as conn:
            cursor = conn.execute("SELECT symbol FROM asset_registry WHERE asset_class = ?;", (asset_class.upper(),))
            return [row["symbol"] for row in cursor.fetchall()]

    def get_complete_watchlist(self) -> List[str]:
        """Queries the operational table database to return the complete 15-asset tracking scope."""
        with db_manager.metadata_db() as conn:
            cursor = conn.execute("SELECT symbol FROM asset_registry;")
            return [row["symbol"] for row in cursor.fetchall()]

asset_registry = PersistentAssetRegistry()
