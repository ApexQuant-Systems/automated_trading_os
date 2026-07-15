# Component Manifest Contract Header
__module_name__ = "centralized_logging_engine"
__build_version__ = "0.2.0-stable"
__spec_contract_hash__ = "0x01_logger_core"
__regression_suite_hash__ = "0x01_logger_verify"

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

class CentralizedLogger:
    """Thread-safe framework managing unified text stream tracking and persistence logs operations."""

    def __init__(self, log_dir: str = "logs", log_file: str = "runtime.log"):
        self.log_dir = log_dir
        self.log_path = os.path.join(self.log_dir, log_file)
        
        # Ensure target logging infrastructure directory footprint exists safely on disk
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize base root logging allocation references
        self.logger = logging.getLogger("APEX_CORE")
        self.logger.setLevel(logging.INFO)
        
        # Prevent handler duplication leaks across double instantiation paths
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [logger]: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # 1. Standard Console Output Stream Handler Definition
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # 2. Institutional Rotation File Persistence Handler Definition
            # Prevents hard drive bloat by rolling over files at a 10MB ceiling constraint limit
            file_handler = RotatingFileHandler(
                self.log_path, 
                maxBytes=10 * 1024 * 1024, 
                backupCount=5, 
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)

    def fetch_log_path(self) -> str:
        """Returns physical placement coordinate reference for analytical review auditing."""
        return self.log_path

logger = CentralizedLogger()
