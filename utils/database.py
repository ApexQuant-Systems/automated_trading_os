# Component Manifest Contract Header
__module_name__ = "partitioned_persistence_engine"
__build_version__ = "0.3.2-stable"
__spec_contract_hash__ = "0x102_database_partitioned"
__regression_suite_hash__ = "0x102_database_verify_partitioned"

import os
import sqlite3
import datetime
from contextlib import contextmanager
from typing import Generator

class RelationalPersistenceManager:
    """Agnostic thread-safe storage core managing partitioned time-series price data warehouses."""

    def __init__(self, db_path: str = "market_data/warehouse/price_warehouse.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.initialize_core_schemas()

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager providing thread-safe WAL transactions with strict isolation controls."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")  # High-throughput asynchronous write performance
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def initialize_core_schemas(self):
        """Builds standardized partitioned infrastructure tables matching the frozen asset classes."""
        with self.connection() as conn:
            # 1. Automated Schema Migration Audit Control Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL,
                    checksum TEXT NOT NULL
                );
            """)

            # 2. Partitioned Historical Price Repositories
            for asset_class in ["crypto", "forex", "metal", "index"]:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {asset_class}_candles (
                        timestamp INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        open REAL NOT NULL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL NOT NULL,
                        volume REAL NOT NULL,
                        quote_volume REAL DEFAULT 0.0,
                        trade_count INTEGER DEFAULT 0,
                        dataset_id TEXT NOT NULL,
                        PRIMARY KEY (symbol, timestamp)
                    );
                """)
                # Accelerate time-series aggregation sweeps
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{asset_class}_chrono ON {asset_class}_candles (symbol, timestamp);")

            # 3. Normalized Centralized In-Memory Feature Store Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feature_store (
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    feature_type TEXT NOT NULL,
                    feature_key TEXT NOT NULL,
                    feature_value TEXT NOT NULL,
                    PRIMARY KEY (symbol, timeframe, timestamp, feature_type, feature_key)
                );
            """)

            # 4. Advanced Telemetry Staged Trade Journal Ledger
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trade_journal (
                    trade_id TEXT PRIMARY KEY,
                    strategy_id TEXT NOT NULL,
                    setup_score REAL NOT NULL,
                    entry_timestamp INTEGER NOT NULL,
                    exit_timestamp INTEGER,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    risk_amount REAL NOT NULL,
                    position_size REAL NOT NULL,
                    spread REAL NOT NULL,
                    slippage REAL DEFAULT 0.0,
                    commission REAL NOT NULL,
                    swap REAL DEFAULT 0.0,
                    expected_rr REAL NOT NULL,
                    actual_rr REAL DEFAULT 0.0,
                    realized_pnl REAL DEFAULT 0.0,
                    execution_latency REAL NOT NULL,
                    exit_reason TEXT
                );
            """)
            
            # Seed primary version tracking records safely
            conn.execute("""
                INSERT OR IGNORE INTO schema_version (version, applied_at, checksum)
                VALUES (?, ?, ?)
            """, (1, datetime.datetime.utcnow().isoformat(), __spec_contract_hash__))

db = RelationalPersistenceManager()
