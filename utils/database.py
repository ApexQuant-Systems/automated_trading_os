# Component Manifest Contract Header
__module_name__ = "three_concern_persistence_manager"
__build_version__ = "1.5.0-stable"
__spec_contract_hash__ = "0x105_three_concern_core"
__regression_suite_hash__ = "0x105_three_concern_verify"

import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

class ThreeConcernDatabaseManager:
    """Manages transactional isolation across decoupled price, metadata, and audit dataspaces."""

    def __init__(self, base_dir: str = "market_data"):
        self.price_db_path = os.path.join(base_dir, "warehouse", "price_warehouse.db")
        self.meta_db_path = os.path.join(base_dir, "metadata", "metadata.db")
        self.audit_db_path = os.path.join(base_dir, "audit", "audit.db")

        # Automatically generate physical directory layout structures
        os.makedirs(os.path.dirname(self.price_db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.meta_db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.audit_db_path), exist_ok=True)

        self.initialize_all_schemas()

    @contextmanager
    def _connection(self, db_path: str) -> Generator[sqlite3.Connection, None, None]:
        """Provides thread-safe proxy connections running in asynchronous WAL caching mode."""
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @contextmanager
    def price_db(self) -> Generator[sqlite3.Connection, None, None]:
        """Isolated transactional context manager for historical pricing records."""
        with self._connection(self.price_db_path) as conn:
            yield conn

    @contextmanager
    def metadata_db(self) -> Generator[sqlite3.Connection, None, None]:
        """Isolated transactional context manager for job configurations and registries."""
        with self._connection(self.meta_db_path) as conn:
            yield conn

    @contextmanager
    def audit_db(self) -> Generator[sqlite3.Connection, None, None]:
        """Isolated transactional context manager for data quality logs."""
        with self._connection(self.audit_db_path) as conn:
            yield conn

    def initialize_all_schemas(self):
        """Constructs separated table footprints across the micro-database layout tiers."""
        # Tier 1: Historical Pricing Workspace Tables Setup
        with self.price_db() as conn:
            for schema in ["crypto", "forex", "metal", "index"]:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}_candles (
                        timestamp INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        open REAL NOT NULL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL NOT NULL,
                        volume REAL NOT NULL,
                        quote_volume REAL DEFAULT 0.0,
                        trade_count INTEGER DEFAULT 0,
                        job_id TEXT NOT NULL,
                        PRIMARY KEY (symbol, timestamp)
                    );
                """)
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{schema}_time ON {schema}_candles (symbol, timestamp);")

        # Tier 2: Operational Metadata Workspace Tables Setup
        with self.metadata_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS asset_registry (
                    symbol TEXT PRIMARY KEY,
                    asset_class TEXT NOT NULL,
                    venue TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    tick_size REAL NOT NULL,
                    price_precision INTEGER NOT NULL,
                    volume_precision INTEGER NOT NULL,
                    base_currency TEXT NOT NULL,
                    quote_currency TEXT NOT NULL,
                    trading_hours TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_scheduler (
                    job_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    chunk_year INTEGER NOT NULL,
                    chunk_month INTEGER NOT NULL,
                    status TEXT NOT NULL, -- PENDING, DOWNLOADING, DOWNLOADED, VALIDATED, TRANSFORMED, LOADED, AUDITED, RESEARCH_READY
                    retries INTEGER DEFAULT 0,
                    started_at INTEGER,
                    finished_at INTEGER,
                    error_msg TEXT
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dataset_manifests (
                    dataset_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    venue TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    start_timestamp INTEGER NOT NULL,
                    end_timestamp INTEGER NOT NULL,
                    total_rows INTEGER NOT NULL,
                    parser_version TEXT NOT NULL,
                    warehouse_version TEXT NOT NULL,
                    file_hash_sha256 TEXT NOT NULL,
                    download_url TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );
            """)

        # Tier 3: Quality Audit Tracking Table Setup
        with self.audit_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_gap_logs (
                    gap_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    gap_start_timestamp INTEGER NOT NULL,
                    gap_end_timestamp INTEGER NOT NULL,
                    missing_candles_count INTEGER NOT NULL,
                    severity_level TEXT NOT NULL,
                    detected_at INTEGER NOT NULL
                );
            """)

db_manager = ThreeConcernDatabaseManager()
