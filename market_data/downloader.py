# Component Manifest Contract Header
__module_name__ = "production_historical_downloader"
__build_version__ = "1.5.2-stable"
__spec_contract_hash__ = "0x105_production_downloader_v3"

import os
import sys
import time
import urllib.request
from typing import Dict, Any
from market_data.asset_registry import asset_registry

class HistoricalDownloader:
    """Resilient network worker executing multi-market data downloads via structured public adapters."""

    def __init__(self):
        self.max_retries = 3
        self.retry_delay_base = 2
        
        # Institutional endpoint distribution matrix
        self._endpoints = {
            "BINANCE_VISION": "https://data.binance.vision/data/spot/monthly/klines/{symbol}/{timeframe}/{symbol}-{timeframe}-{year}-{month:02d}.zip",
            "YAHOO_FINANCE": "https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_ts}&period2={end_ts}&interval={interval}&events=history&includeAdjustedClose=true"
        }

        # Symbol dictionary mapping for public index gateways
        self._yahoo_symbols = {
            "NAS100": "^NDX", "SPX500": "^GSPC", "US30": "^DJI", "GER40": "^GDAXI", "UK100": "^FTSE",
            "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "USDCAD": "CAD=X",
            "XAUUSD": "GC=F", "XAGUSD": "SI=F"
        }

    def _calculate_yahoo_timestamps(self, year: int, month: int) -> tuple:
        """Computes accurate unix epoch boundaries matching the target monthly chunk."""
        import calendar
        import datetime
        start_date = datetime.datetime(year, month, 1, 0, 0, 0)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime.datetime(year, month, last_day, 23, 59, 59)
        
        return int(start_date.timestamp()), int(end_date.timestamp())

    def _resolve_download_url(self, job: Dict[str, Any]) -> str:
        """Translates an internal job descriptor into an explicit public remote resource link."""
        symbol = job["symbol"]
        tf = job["timeframe"]
        year = job["chunk_year"]
        month = job["chunk_month"]

        asset_meta = asset_registry.get_asset(symbol)
        provider = asset_meta["provider"]

        if provider == "BINANCE_VISION":
            p_tf = tf.lower()
            return self._endpoints["BINANCE_VISION"].format(
                symbol=symbol, timeframe=p_tf, year=year, month=month
            )
        else:
            # Fallback to high-fidelity global equity/macro data index
            y_symbol = self._yahoo_symbols.get(symbol, symbol)
            start_ts, end_ts = self._calculate_yahoo_timestamps(year, month)
            
            # Map intervals cleanly into Yahoo Finance API standards
            interval_map = {"15M": "15m", "1H": "1h", "4H": "1h", "1D": "1d", "1W": "1wk", "1M": "1mo"}
            y_interval = interval_map.get(tf.upper(), "1d")
            
            return self._endpoints["YAHOO_FINANCE"].format(
                symbol=y_symbol, start_ts=start_ts, end_ts=end_ts, interval=y_interval
            )

    def download_job_chunk(self, job: Dict[str, Any]) -> bool:
        """Streams raw multi-market data packets directly to your immutable storage layers."""
        symbol = job["symbol"]
        tf = job["timeframe"]
        year = job["chunk_year"]
        month = job["chunk_month"]
        
        asset_meta = asset_registry.get_asset(symbol)
        file_extension = "zip" if asset_meta["provider"] == "BINANCE_VISION" else "csv"
        file_name = f"{symbol}-{tf}-{year}-{month:02d}.{file_extension}"
        dest_path = f"market_data/raw/{asset_meta['asset_class'].lower()}/{symbol}/{tf.lower()}/{file_name}"
        
        source_url = self._resolve_download_url(job)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        for attempt in range(1, self.max_retries + 1):
            try:
                req = urllib.request.Request(
                    source_url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) APEX Quant Ingestion'}
                )
                
                with urllib.request.urlopen(req, timeout=20.0) as response:
                    content_length = response.headers.get('Content-Length')
                    total_size = int(content_length) if content_length else 0
                    bytes_downloaded = 0
                    block_size = 1024 * 64
                    
                    with open(dest_path, 'wb') as out_file:
                        while True:
                            buffer = response.read(block_size)
                            if not buffer:
                                break
                            out_file.write(buffer)
                            bytes_downloaded += len(buffer)
                            
                            if total_size > 0:
                                percent = (bytes_downloaded / total_size) * 100
                                sys.stdout.write(f"\r  └─ Ingress Progress: {symbol} [{tf}] {year}-{month:02d} -> {percent:6.1f}% Completed")
                                sys.stdout.flush()
                                
                    sys.stdout.write("\n")
                    return True
                    
            except Exception as network_exception:
                if hasattr(network_exception, 'code') and network_exception.code == 404:
                    print(f"  └─ [404 Not Found] Target historical row bounds not available on remote server for {symbol} {year}-{month:02d}.")
                    break
                    
                sleep_duration = self.retry_delay_base ** attempt
                print(f"\n  [Warning] Ingress timeout on attempt {attempt}/{self.max_retries}. Re-trying loop in {sleep_duration}s...")
                time.sleep(sleep_duration)
                
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                    
        return False

historical_downloader = HistoricalDownloader()
