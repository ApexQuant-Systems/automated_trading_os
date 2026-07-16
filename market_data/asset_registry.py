# Component Manifest Contract Header
__module_name__ = "immutable_asset_registry"
__build_version__ = "1.1.0-stable"
__spec_contract_hash__ = "0x101_asset_registry_core"
__regression_suite_hash__ = "0x101_asset_registry_verify"

from typing import Dict, Any, List

class AssetRegistry:
    """Immutable central data matrix managing configurations for the target research universe."""

    def __init__(self):
        # 1. Standardized Multi-Market Universe Definitions (15 Chosen Global Assets)
        self._registry: Dict[str, Dict[str, Any]] = {
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

    def verify_asset_exists(self, symbol: str) -> bool:
        """Verifies if the specified token is registered inside the tracking matrix universe."""
        return symbol.upper() in self._registry

    def get_asset(self, symbol: str) -> Dict[str, Any]:
        """Fetches isolated configuration profile dictionary parameters for the target asset."""
        sym = symbol.upper()
        if sym not in self._registry:
            raise KeyError(f"Asset Registry Core Drop: Symbol '{symbol}' is completely unknown to this platform.")
        return self._registry[sym].copy()

    def get_watchlist_by_class(self, asset_class: str) -> List[str]:
        """Returns all registered ticker symbol strings belonging to a target macro category."""
        target_cls = asset_class.upper()
        return [sym for sym, cfg in self._registry.items() if cfg["asset_class"] == target_cls]

    def get_complete_watchlist(self) -> List[str]:
        """Flattens the entire registry to return all 15 active research assets."""
        return list(self._registry.keys())

asset_registry = AssetRegistry()
