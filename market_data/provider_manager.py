# Component Manifest Contract Header
__module_name__ = "stateless_provider_manager"
__build_version__ = "1.2.0-stable"
__spec_contract_hash__ = "0x102_provider_manager_core"
__regression_suite_hash__ = "0x102_provider_manager_verify"

import datetime
from typing import Dict, Any, List
from market_data.asset_registry import asset_registry

class ProviderManager:
    """Stateless coordinator translating structural assets requests into granular data task maps."""

    def __init__(self):
        # Base historical target archive endpoints mappings configuration
        self._url_templates = {
            "BINANCE_VISION": "https://data.binance.vision/data/spot/monthly/klines/{symbol}/{timeframe}/{symbol}-{timeframe}-{year}-{month}.zip",
            "DUKASCOPY": "https://data.dukascopy.com/bidask/{symbol}/{year}/{month:02d}/{day:02d}/data.binance.csv"
        }

    def _normalize_timeframe_string(self, provider: str, timeframe: str) -> str:
        """Standardizes internal timeframe definitions to match specific remote naming schemas."""
        tf = timeframe.upper()
        if provider == "BINANCE_VISION":
            if tf == "15M": return "15m"
            if tf == "1H": return "1h"
            if tf == "4H": return "4h"
            if tf == "1D": return "1d"
            if tf == "1W": return "1w"
            if tf == "1M": return "1mo"
        return tf.lower()

    def generate_download_tasks(self, symbol: str, timeframe: str, start_ts: int, end_ts: int) -> List[Dict[str, Any]]:
        """Processes time series boundaries to output an array of discrete monthly archive download paths."""
        if not asset_registry.verify_asset_exists(symbol):
            raise KeyError(f"Provider Manager Intercept Failure: '{symbol}' is completely unregistered inside the platform system.")

        asset_meta = asset_registry.get_asset(symbol)
        provider = asset_meta["provider"]
        venue = asset_meta["venue"]
        asset_class = asset_meta["asset_class"]

        start_date = datetime.datetime.utcfromtimestamp(start_ts)
        end_date = datetime.datetime.utcfromtimestamp(end_ts)

        tasks: List[Dict[str, Any]] = []

        # Chronological structural time slicing execution loop (Iterates month-by-month chunks)
        current_date = datetime.datetime(start_date.year, start_date.month, 1)
        while current_date <= end_date:
            year_str = str(current_date.year)
            month_str = f"{current_date.month:02d}"
            
            p_tf = self._normalize_timeframe_string(provider, timeframe)
            
            # Construct immutable download file name formats matching targets
            file_name = f"{symbol}-{timeframe}-{year_str}-{month_str}.zip"
            relative_storage_path = f"market_data/raw/{asset_class.lower()}/{symbol}/{timeframe.lower()}/{file_name}"

            if provider == "BINANCE_VISION":
                url = self._url_templates["BINANCE_VISION"].format(
                    symbol=symbol, timeframe=p_tf, year=year_str, month=month_str
                )
            else:
                # Generic path fallback matrix definition for non-crypto historical archives
                url = f"https://archive.storage.net/historical/{venue.lower()}/{symbol}/{year_str}-{month_str}.csv"

            tasks.append({
                "dataset_id": f"DS-{symbol}-{timeframe}-{year_str}{month_str}",
                "symbol": symbol,
                "timeframe": timeframe,
                "asset_class": asset_class,
                "venue": venue,
                "provider": provider,
                "source_url": url,
                "destination_path": relative_storage_path,
                "chunk_year": current_date.year,
                "chunk_month": current_date.month,
                "compression_type": "ZIP" if provider == "BINANCE_VISION" else "CSV",
                "validation_status": "PENDING"
            })

            # Advance tracking pointer index forward by 1 calendar month cleanly
            if current_date.month == 12:
                current_date = datetime.datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime.datetime(current_date.year, current_date.month + 1, 1)

        return tasks

provider_manager = ProviderManager()
