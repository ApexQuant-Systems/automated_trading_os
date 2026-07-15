# Component Manifest Contract Header
__module_name__ = "relational_persistence_layer"
__build_version__ = "4.0.0-stable"
__spec_contract_hash__ = "0x04_db_lean"
__regression_suite_hash__ = "0x04_db_verify"

import sqlite3
import os
from contextlib import contextmanager
from logs.logger import logger

DB_PATH = "apex_production.db"

class DatabaseManager:
    """Manages SQLite transactions using clean, localized session context scopes."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.initialize_schema()

    @contextmanager
    def connection(self):
        """Provides a safe database connection scope, ensuring atomic commits or rollbacks."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction failure. State rolled back safely.", e)
            raise e
        finally:
            conn.close()

    def initialize_schema(self):
        """Instantiates the simplified, decoupled tables required to support development."""
        with self.connection() as conn:
            # 1. Market Data Storage (Composite primary key handles duplication protection)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    PRIMARY KEY (symbol, timeframe, timestamp)
                )
            """)

            # 2. Closed Loop Execution Trades Tracker
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    exit_price REAL,
                    realized_pnl REAL,
                    status TEXT NOT NULL
                )
            """)

            # 3. System Metadata Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Versioning seed injection
            conn.execute("""
                INSERT OR IGNORE INTO system_metadata (key, value, updated_at)
                VALUES ('schema_version', '4.0.0', datetime('now'))
            """)
            
        logger.info("Database schemas securely mapped and validated.")

db = DatabaseManager()