# Component Manifest Contract Header
__module_name__ = "production_job_scheduler"
__build_version__ = "1.4.0-stable"
__spec_contract_hash__ = "0x104_production_scheduler"

import time
from typing import List, Dict, Any, Optional
from utils.database import db_manager

class JobScheduler:
    """Manages the persistent lifecycle, task lockouts, and state tracking for data jobs."""

    def enqueue_job_matrix(self, jobs: List[Dict[str, Any]]) -> int:
        """Seeds computed job profiles into the metadata database table, skipping existing records."""
        inserted = 0
        with db_manager.metadata_db() as conn:
            for job in jobs:
                cursor = conn.execute("""
                    INSERT OR IGNORE INTO job_scheduler (
                        job_id, symbol, timeframe, chunk_year, chunk_month, status, retries
                    ) VALUES (?, ?, ?, ?, ?, ?, 0);
                """, (
                    job["job_id"], job["symbol"], job["timeframe"], 
                    job["chunk_year"], job["chunk_month"], "PENDING"
                ))
                inserted += cursor.rowcount
        return inserted

    def acquire_next_pending_job(self) -> Optional[Dict[str, Any]]:
        """Queries the queue in a thread-safe transaction block to fetch and lock the next eligible task."""
        with db_manager.metadata_db() as conn:
            cursor = conn.execute("""
                SELECT * FROM job_scheduler 
                WHERE status = 'PENDING' AND retries < 3 
                ORDER BY chunk_year ASC, chunk_month ASC 
                LIMIT 1;
            """)
            row = cursor.fetchone()
            if not row:
                return None
                
            job_dict = dict(row)
            # Atomically advance the state to DOWNLOADING to lock out competing workers
            conn.execute("""
                UPDATE job_scheduler 
                SET status = 'DOWNLOADING', started_at = ? 
                WHERE job_id = ?;
            """, (int(time.time()), job_dict["job_id"]))
            
            return job_dict

    def update_job_status(self, job_id: str, status: str, error_msg: str = None) -> None:
        """Updates a job's status and logs timestamp changes or processing failures."""
        with db_manager.metadata_db() as conn:
            if status.upper() in ["RESEARCH_READY", "FAILED"]:
                conn.execute("""
                    UPDATE job_scheduler 
                    SET status = ?, finished_at = ?, error_msg = ? 
                    WHERE job_id = ?;
                """, (status.upper(), int(time.time()), error_msg, job_id))
            else:
                conn.execute("""
                    UPDATE job_scheduler 
                    SET status = ?, error_msg = ? 
                    WHERE job_id = ?;
                """, (status.upper(), error_msg, job_id))

    def increment_retry_counter(self, job_id: str, error_msg: str) -> None:
        """Increments a job's network failure counter, shifting its status back to PENDING if below the cap."""
        with db_manager.metadata_db() as conn:
            cursor = conn.execute("SELECT retries FROM job_scheduler WHERE job_id = ?;", (job_id,))
            row = cursor.fetchone()
            if not row:
                return
                
            current_retries = row["retries"] + 1
            next_status = "FAILED" if current_retries >= 3 else "PENDING"
            
            conn.execute("""
                UPDATE job_scheduler 
                SET retries = ?, status = ?, error_msg = ? 
                WHERE job_id = ?;
            """, (current_retries, next_status, error_msg, job_id))

job_scheduler = JobScheduler()
