# APEX QUANT OS — PHASE 1A CORE DATA PLATFORM (FROZEN)

## 1. System Identity
* **Status:** FROZEN
* **Version:** 1.0.0
* **Date:** July 2026
* **Dependencies:** ccxt, sqlite3, pandas
* **Downstream Consumers:** Module 2.1 (Candles), Module 2.2 (Swings), Module 2.3 (Structure)

## 2. Architecture & Schema
* **Database:** SQLite (Local)
* **File:** `price_warehouse.db`
* **Table:** `crypto_candles`
* **Primary Key:** `(symbol, timeframe, timestamp)`
* **Indexes:** `idx_sym_tf_ts`

## 3. APIs & Workflows
* **Data Ingestion:** `deep_downloader.py` (CCXT Binance integration, handles rate limits, respects primary key constraints).
* **Data Consumption:** Downstream modules must strictly use `ReplayLoader.get_history()`. Direct `sqlite3` imports in Phase 2+ are permanently forbidden.

## 4. Validation Rules Passed
* [x] No `NULL` values.
* [x] No negative volumes.
* [x] OHLC Geometric integrity (`High >= max(Open, Close)`, `Low <= min(Open, Close)`).
* [x] No duplicate timestamps.
* [x] 100% Temporal Continuity (Zero missing candles).
* [x] Replay API Unit Tests (Limits, Chronology, Schema, Error Handling).

## 5. Known Limitations (Deferred to Phase 1B)
* Incremental scheduling (`cron` or daemon) is manual.
* System is currently read-only for backtesting; live websocket feeds will be integrated in Phase 1B prior to paper trading.
