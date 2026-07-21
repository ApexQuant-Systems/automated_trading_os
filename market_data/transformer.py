# Component Manifest Contract Header
__module_name__ = "production_canonical_transformer"
__build_version__ = "1.1.0-stable"
__spec_contract_hash__ = "0x106_production_transformer_v2"

import os
import zipfile
import csv
import io
import hashlib
import datetime
from typing import Dict, Any, List, Tuple

class CanonicalTransformer:
    """Validates downloaded source archives and normalizes pricing schemas into standardized matrices."""

    def calculate_file_sha256(self, file_path: str) -> str:
        """Computes the cryptographic SHA256 checksum signature of an archive file block."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def transform_binance_zip(self, file_path: str) -> List[Tuple[int, float, float, float, float, float, float, int]]:
        """Parses raw Binance kline CSV matrices inside compressed zip stores into normalized data lines."""
        canonical_records = []
        if not os.path.exists(file_path) or not zipfile.is_zipfile(file_path):
            return canonical_records

        with zipfile.ZipFile(file_path, 'r') as archive:
            for internal_file in archive.namelist():
                if internal_file.endswith('.csv'):
                    with archive.open(internal_file) as csv_file:
                        text_layer = io.TextIOWrapper(csv_file, encoding='utf-8')
                        csv_reader = csv.reader(text_layer)
                        for row in csv_reader:
                            if not row or row[0].isalpha():
                                continue
                            try:
                                epoch_seconds = int(row[0]) // 1000
                                canonical_records.append((
                                    epoch_seconds, float(row[1]), float(row[2]), 
                                    float(row[3]), float(row[4]), float(row[5]),
                                    float(row[7]), int(row[8])
                                ))
                            except (ValueError, IndexError):
                                continue
        canonical_records.sort(key=lambda x: x[0])
        return canonical_records

    def transform_yahoo_csv(self, file_path: str) -> List[Tuple[int, float, float, float, float, float, float, int]]:
        """Parses flat Yahoo Finance historical CSV tracks into uniform pricing tuples."""
        canonical_records = []
        if not os.path.exists(file_path):
            return canonical_records

        with open(file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            header = next(csv_reader, None) # Strip column text header metrics
            
            for row in csv_reader:
                # Expected format: Date,Open,High,Low,Close,Adj Close,Volume
                if not row or "null" in row:
                    continue
                try:
                    # Convert string dates (YYYY-MM-DD) to normalized UTC epoch integers
                    dt = datetime.datetime.strptime(row[0], "%Y-%m-%d")
                    epoch_seconds = int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())
                    
                    # Map metrics cleanly, defaulting missing crypto-specific parameters to zero
                    canonical_records.append((
                        epoch_seconds,
                        float(row[1]), # Open
                        float(row[2]), # High
                        float(row[3]), # Low
                        float(row[4]), # Close
                        float(row[6]), # Volume
                        0.0,           # Quote Volume Placeholder
                        0              # Trade Count Placeholder
                    ))
                except (ValueError, IndexError):
                    continue
                    
        canonical_records.sort(key=lambda x: x[0])
        return canonical_records

canonical_transformer = CanonicalTransformer()
