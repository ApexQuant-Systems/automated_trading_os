# Component Manifest Contract Header
__module_name__ = "dataset_inventory_catalog"
__build_version__ = "1.3.0-stable"
__spec_contract_hash__ = "0x103_dataset_catalog_core"
__regression_suite_hash__ = "0x103_dataset_catalog_verify"

import os
import sqlite3
import time
from typing import Dict, Any, List, Optional

class DatasetCatalog:
    """Persistent ledger managing inventory states for the historical research datasets universe."""

    def __init__(self, db_path: str = "market_data/warehouse/metadata_registry.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Isolated database worker providing localized transaction scopes."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self):
        """Constructs the standalone dataset tracking manifest table footprint."""
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dataset_catalog (
                        dataset_id TEXT PRIMARY KEY,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        start_timestamp INTEGER NOT NULL,
                        end_timestamp INTEGER NOT NULL,
                        status TEXT NOT NULL, -- REGISTERED, DOWNLOADED, VALIDATED, RESEARCH_READY
                        last_updated INTEGER NOT NULL
                    );
                """)
        finally:
            conn.close()

    def register_dataset(self, dataset_id: str, symbol: str, timeframe: str, start_ts: int, end_ts: int) -> bool:
        """Seeds a new historical data chunk descriptor track inside the tracking ledger."""
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR IGNORE INTO dataset_catalog (
                        dataset_id, symbol, timeframe, start_timestamp, end_timestamp, status, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (dataset_id, symbol.upper(), timeframe.upper(), start_ts, end_ts, "REGISTERED", int(time.time())))
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def update_dataset_status(self, dataset_id: str, status: str) -> bool:
        """Updates the operational life-cycle state flag for the target dataset tracking point."""
        valid_statuses = ["REGISTERED", "DOWNLOADED", "VALIDATED", "RESEARCH_READY"]
        if status.upper() not in valid_statuses:
            return False

        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    UPDATE dataset_catalog 
                    SET status = ?, last_updated = ? 
                    WHERE dataset_id = ?
                """, (status.upper(), int(time.time()), dataset_id))
                return cursor.rowcount > 0
        except Exception:
            return False
        finally:
            conn.close()

    def get_dataset_status(self, dataset_id: str) -> Optional[str]:
        """Retrieves the active inventory status for a specific tracking record block."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT status FROM dataset_catalog WHERE dataset_id = ?", (dataset_id,))
            row = cursor.fetchone()
            return row["status"] if row else None
        finally:
            conn.close()

    def fetch_datasets_by_status(self, status: str) -> List[str]:
        """Returns all matching dataset IDs pinned to a specific catalog state."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT dataset_id FROM dataset_catalog WHERE status = ?", (status.upper(),))
            return [row["dataset_id"] for row in cursor.fetchall()]
        finally:
            conn.close()

dataset_catalog = DatasetCatalog()
