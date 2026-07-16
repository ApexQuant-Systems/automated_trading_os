# Component Manifest Contract Header
__module_name__ = "production_download_planner"
__build_version__ = "1.3.0-stable"
__spec_contract_hash__ = "0x103_production_planner"

import datetime
from typing import List, Dict, Any
from market_data.asset_registry import asset_registry

class DownloadPlanner:
    """Calculates time-series historical data chunks to schedule ingestion tasks across assets."""

    def __init__(self):
        self.timeframes = ["15M", "1H", "4H", "1D", "1W", "1M"]
        # Standardized asset inception year bounds to prevent empty remote queries
        self.start_years = {
            "BTCUSDT": 2017, "ETHUSDT": 2017, "SOLUSDT": 2020,
            "EURUSD": 2015, "GBPUSD": 2015, "USDJPY": 2015, "AUDUSD": 2015, "USDCAD": 2015,
            "XAUUSD": 2015, "XAGUSD": 2015,
            "NAS100": 2016, "SPX500": 2016, "US30": 2016, "GER40": 2016, "UK100": 2016
        }

    def generate_job_matrix(self, current_year: int = 2026, current_month: int = 7) -> List[Dict[str, Any]]:
        """Computes comprehensive monthly data task allocations across the complete research universe."""
        job_matrix: List[Dict[str, Any]] = []
        watchlist = asset_registry.get_complete_watchlist()

        for symbol in watchlist:
            asset_meta = asset_registry.get_asset(symbol)
            start_yr = self.start_years.get(symbol, 2015)

            for tf in self.timeframes:
                for year in range(start_yr, current_year + 1):
                    # Bounded end-month parameter calculation to protect from querying future fields
                    end_month = current_month if year == current_year else 12
                    
                    for month in range(1, end_month + 1):
                        job_id = f"JOB-{symbol}-{tf}-{year}{month:02d}"
                        
                        # Route configuration format settings matching target provider syntax
                        p_tf = tf.lower() if asset_meta["provider"] == "BINANCE_VISION" else tf.upper()
                        if p_tf == "1mo": p_tf = "1mo" # Handle Binance specific month codes
                        
                        file_name = f"{symbol}-{tf}-{year}-{month:02d}.zip"
                        dest_path = f"market_data/raw/{asset_meta['asset_class'].lower()}/{symbol}/{tf.lower()}/{file_name}"

                        job_matrix.append({
                            "job_id": job_id,
                            "symbol": symbol,
                            "timeframe": tf,
                            "chunk_year": year,
                            "chunk_month": month,
                            "destination_path": dest_path,
                            "provider": asset_meta["provider"],
                            "venue": asset_meta["venue"],
                            "asset_class": asset_meta["asset_class"]
                        })
        return job_matrix

download_planner = DownloadPlanner()
