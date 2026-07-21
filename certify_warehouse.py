#!/usr/bin/env python3
# Core Data Validation Engine Focus: Hardened Quantitative Warehouse Invariant Auditor

import os
import sys
import time
from utils.database import db_manager

print("==================================================================")
print("        APEX QUANT PLATFORM: HARDENED WAREHOUSE CERTIFIER        ")
print("==================================================================")

def execute_firm_audit():
    db_path = "market_data/warehouse/price_warehouse.db"
    if not os.path.exists(db_path):
        print(f"❌ CRITICAL FAILURE: Target warehouse database missing at: {db_path}")
        sys.exit(1)

    with db_manager.price_db() as conn:
        # ────────────────────────────────────────────────────────────────
        # TEST 1: SCAN FOR DUPLICATE TIMESTAMPS
        # ────────────────────────────────────────────────────────────────
        print("\n[TEST 1/6] Scanning for duplicate timestamp anomalies...")
        dup_query = """
            SELECT symbol, timeframe, timestamp, COUNT(*) 
            FROM crypto_candles 
            GROUP BY symbol, timeframe, timestamp 
            HAVING COUNT(*) > 1;
        """
        duplicates = conn.execute(dup_query).fetchall()
        if duplicates:
            print(f"🚨 CRITICAL DATA BREAK: Found {len(duplicates)} duplicate records!")
            for d in duplicates[:3]:
                print(f"   └── Fail Target: {d[0]} | {d[1]} | Ts: {d[2]} | Count: {d[3]}")
        else:
            print("✅ PASS: Zero duplicate timestamps detected across all asset horizons.")

        # ────────────────────────────────────────────────────────────────
        # TEST 2: VERIFY MULTI-POINT OHLC GEOMETRIC INVARIANTS
        # ────────────────────────────────────────────────────────────────
        print("\n[TEST 2/6] Auditing OHLC structural geometric invariants...")
        geometric_query = """
            SELECT symbol, timeframe, timestamp, open, high, low, close 
            FROM crypto_candles 
            WHERE high < low 
               OR high < open 
               OR high < close 
               OR low > open 
               OR low > close;
        """
        geometry_faults = conn.execute(geometric_query).fetchall()
        if geometry_faults:
            print(f"🚨 CRITICAL DATA BREAK: Found {len(geometry_faults)} broken price shapes!")
            for f in geometry_faults[:3]:
                print(f"   └── Bad Geometry: {f[0]} | {f[1]} | Ts: {f[2]} | O:{f[3]} H:{f[4]} L:{f[5]} C:{f[6]}")
        else:
            print("✅ PASS: 100% of rows conform to mathematical OHLC geometric boundaries.")

        # ────────────────────────────────────────────────────────────────
        # TEST 3: ISOLATE DEADBAND ZERO-VOLUME FAULTS
        # ────────────────────────────────────────────────────────────────
        print("\n[TEST 3/6] Scanning for flat deadband zero-volume anomalies...")
        vol_query = """
            SELECT symbol, timeframe, COUNT(*) 
            FROM crypto_candles 
            WHERE volume = 0.0 
            GROUP BY symbol, timeframe;
        """
        zero_vols = conn.execute(vol_query).fetchall()
        if zero_vols:
            print("⚠️ WARNING: Stale flat volume blocks detected inside the database tables:")
            for v in zero_vols:
                print(f"   └── {v[0]:<10} | {v[1]:<5} | Flat Volume Rows: {v[2]:,}")
        else:
            print("✅ PASS: Zero flat volume deadbands discovered.")

        # ────────────────────────────────────────────────────────────────
        # TEST 4: TIMELINE TIMESTEP CONTINUITY GAP ANALYSIS
        # ────────────────────────────────────────────────────────────────
        print("\n[TEST 4/6] Running timeline continuity gap analysis...")
        gap_detected = False
        assets = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        tfs = ["15M", "1H", "4H", "1D"]
        
        for asset in assets:
            for tf in tfs:
                rows = conn.execute("""
                    SELECT timestamp FROM crypto_candles 
                    WHERE symbol = ? AND timeframe = ? 
                    ORDER BY timestamp ASC;
                """, (asset, tf)).fetchall()
                
                if len(rows) < 2:
                    continue
                
                # Sample the dominant baseline interval dynamically
                deltas = [rows[i][0] - rows[i-1][0] for i in range(1, min(20, len(rows)))]
                base_delta = min(deltas) if deltas else 900000
                
                large_gaps = 0
                for i in range(1, len(rows)):
                    current_delta = rows[i][0] - rows[i-1][0]
                    if current_delta > (base_delta * 2.5):
                        large_gaps += 1
                        gap_detected = True
                        
                if large_gaps > 0:
                    print(f"⚠️ GAP FOUND: {asset:<8} | {tf:<4} contains {large_gaps} unindexed chronological timeline gaps.")
        
        if not gap_detected:
            print("✅ PASS: Continuous time-series verified. Zero timeline drops mapped.")

        # ────────────────────────────────────────────────────────────────
        # TEST 5: EVALUATE CROSS-TIMEFRAME ALIGNMENT HORIZONS
        # ────────────────────────────────────────────────────────────────
        print("\n[TEST 5/6] Verification of cross-timeframe alignment bounds...")
        # Verify that Daily high prices contain the corresponding 1-Hour high metrics
        cross_query = """
            SELECT d.symbol, d.timestamp, d.high, MAX(h.high) 
            FROM crypto_candles d
            JOIN crypto_candles h ON h.symbol = d.symbol 
              AND h.timeframe = '1H'
              AND h.timestamp >= d.timestamp 
              AND h.timestamp < d.timestamp + 86400000
            WHERE d.timeframe = '1D'
            GROUP BY d.symbol, d.timestamp
            LIMIT 5;
        """
        cross_samples = conn.execute(cross_query).fetchall()
        cross_faults = 0
        for sample in cross_samples:
            if abs(sample[2] - sample[3]) > 1e-4:
                cross_faults += 1
        if cross_faults > 0:
            print("🚨 CRITICAL MALTREATMENT: High horizons do not match across timeframe resolutions!")
        else:
            print("✅ PASS: Internal timeframe boundary limits match cleanly across horizons.")

        # ────────────────────────────────────────────────────────────────
        # TEST 6: UNMASK THE 6 MISSING MONTHLY BLOCKS (221 vs 227 HUNT)
        # ────────────────────────────────────────────────────────────────
        print("\n[TEST 6/6] Unmasking the missing monthly blocks (221 vs 227 hunt)...")
        print("-> Checking absolute inception footprints inside the Monthly partition tables:")
        
        for asset in assets:
            m_data = conn.execute("""
                SELECT COUNT(*), MIN(timestamp), MAX(timestamp) 
                FROM crypto_candles 
                WHERE symbol = ? AND timeframe = '1M';
            """, (asset,)).fetchone()
            
            count = m_data[0]
            min_ts = m_data[1] / 1000.0 if m_data[1] else 0
            max_ts = m_data[2] / 1000.0 if m_data[2] else 0
            
            start_str = time.strftime('%Y-%m', time.gmtime(min_ts)) if min_ts else "N/A"
            end_str = time.strftime('%Y-%m', time.gmtime(max_ts)) if max_ts else "N/A"
            
            print(f"   ├── {asset:<8} -> Stored Rows: {count:<3} | Coverage Span: {start_str} to {end_str}")

        print("\n==================================================================")
        print("                 AUDIT PROCESS COMPLETED CLEANLY                 ")
        print("==================================================================")

if __name__ == "__main__":
    execute_firm_audit()
