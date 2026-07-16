#!/usr/bin/env python3
# Component Manifest Contract Header
__module_name__ = "data_platform_cli_gateway"
__build_version__ = "1.0.0-production"

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from market_data.planner import download_planner
from market_data.scheduler import job_scheduler
from utils.database import db_manager

def main():
    print("==================================================================")
    print("            APEX QUANT DATA PLATFORM CORE COMMAND RUNTIME         ")
    print("==================================================================")
    
    # 1. Initialize the decoupled database environments
    print("-> Verifying multi-dataspace database infrastructures partitions...")
    db_manager.initialize_all_schemas()
    
    # 2. Compute full matrix layout tracks via the Planner
    print("-> Calculating required timeline chunk matrix grid metrics...")
    full_job_list = download_planner.generate_job_matrix()
    total_calculated_chunks = len(full_job_list)
    print(f"✓ Total target tasks mapped across the research universe: {total_calculated_chunks}")
    
    # 3. Seed configurations into the persistent database queue scheduler
    print("-> Synchronizing targets array records to persistent storage scheduler...")
    new_jobs_seeded = job_scheduler.enqueue_job_matrix(full_job_list)
    print(f"✓ State Machine Synced: Added {new_jobs_seeded} new job records to metadata database queue.")
    
    # Fetch progress telemetry indices straight from metadata tables
    with db_manager.metadata_db() as conn:
        total_pending = conn.execute("SELECT COUNT(*) as count FROM job_scheduler WHERE status = 'PENDING';").fetchone()["count"]
        total_ready = conn.execute("SELECT COUNT(*) as count FROM job_scheduler WHERE status = 'RESEARCH_READY';").fetchone()["count"]
        total_failed = conn.execute("SELECT COUNT(*) as count FROM job_scheduler WHERE status = 'FAILED';").fetchone()["count"]

    print("------------------------------------------------------------------")
    print("                      DATA PLATFORM PROGRESS REPORT               ")
    print("------------------------------------------------------------------")
    print(f" Total Calculated Grid Jobs : {total_calculated_chunks}")
    print(f" Pending Ingestion Jobs     : {total_pending}")
    print(f" Completed Research-Ready   : {total_ready}")
    print(f" Terminated / Failed Jobs   : {total_failed}")
    print("==================================================================\n")

if __name__ == "__main__":
    main()
