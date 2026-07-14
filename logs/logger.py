# Component Manifest Contract Header
__module_name__ = "central_repository_logger"
__build_version__ = "4.0.0-stable"
__spec_contract_hash__ = "logs_998a12c"
__regression_suite_hash__ = "logs_782b5e3"

import logging
import os
import sys
from datetime import datetime

class ApexLogger:
    """Centralized neutral logging interface tracking headless system metrics."""
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        self.logger = logging.getLogger("APEX_OS")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        
        # Standardized microsecond configuration mapping layout contract
        formatter = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(module)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        file_name = f"apex_runtime_{datetime.utcnow().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(os.path.join(self.log_dir, file_name), encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(f"WARNING: {msg}")

    def error(self, msg: str, exception: Exception = None):
        error_payload = f"CRITICAL_EXCEPTION: {msg}"
        if exception:
            error_payload += f" | Details: {str(exception)}"
        self.logger.error(error_payload, exc_info=True)

logger = ApexLogger()