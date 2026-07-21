# Component Manifest Contract Header
__module_name__ = "production_download_planner"
__build_version__ = "1.3.1-stable"
__spec_contract_hash__ = "0x103_production_planner_v2"

import datetime
from typing import List, Dict, Any
from market_data.asset_registry import asset_registry

class DownloadPlanner:
    """Calculates exact historical data chunk boundaries to prevent empty or invalid remote queries."""

    def __init__(self):
        self.timeframes = ["15M", "1H", "4H", "1D", "1W", "1M"]
        # Enforce explicit (Year, Month) tuples matching true historical data availability
        self.asset_inceptions = {
            "BTCUSDT": (2017, 8), 
            "ETHUSDT": (2017, 8), 
            "SOLUSDT": (2020, 8),
            "EURUSD": (2015, 1), 
            "GBPUSD": (2015, 1), 
            "USDJPY": (2015, 1), 
            "AUDUSD": (2015, 1), 
            "USDCAD": (2015, 1),
            "XAUUSD": (2015, 1), 
            "XAGUSD": (2015, 1),
            "NAS100": (2016, 1), 
            "SPX500": (2016, 1), 
            "US30": (2016, 1), 
            "GER40": (2016, 1), 
            "UK100": (2016, 1)
        }

    def generate_job_matrix(self, current_year: int = 2026, current_month: int = 7) -> List[Dict[str, Any]]:
        """Computes comprehensive monthly data task allocations mapping real asset lifecycles."""
        job_matrix: List[Dict[str, Any]] = []
        watchlist = asset_registry.get_complete_watchlist()

        for symbol in watchlist:
            asset_meta = asset_registry.get_asset(symbol)
            start_yr, start_mo = self.asset_inceptions.get(symbol, (2015, 1))

            for tf in self.timeframes:
                for year in range(start_yr, current_year + 1):
                    # Determine exact starting and ending month boundaries for the active year loop
                    start_month = start_mo if year == start_yr else 1
                    end_month = current_month if year == current_year else 12
                    
                    for month in range(start_month, end_month + 1):
                        job_id = f"JOB-{symbol}-{tf}-{year}{month:02d}"
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
