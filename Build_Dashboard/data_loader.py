"""
Data Loader Module - Handles Excel file detection and loading
"""
import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
COMBINED_KEY = "_combined"


class DataLoader:
    """Handles loading and caching of Excel files"""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cached_data: Dict[str, pd.DataFrame] = {}
        self.file_hashes: Dict[str, str] = {}

    def get_excel_files(self) -> List[str]:
        """Get list of all Excel files in data directory"""
        excel_extensions = {'.xlsx', '.xls', '.csv'}
        files = [
            f.name for f in self.data_dir.iterdir()
            if f.is_file() and f.suffix.lower() in excel_extensions
        ]
        return sorted(files)

    def _load_single(self, filename: str) -> pd.DataFrame:
        """Load one Excel/CSV file, using cache when available."""
        if filename in self.cached_data:
            return self.cached_data[filename]

        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        if filename.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        logger.info(f"Loaded {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
        self.cached_data[filename] = df
        return df

    def load_combined(self) -> pd.DataFrame:
        """Concatenate every file in the data folder into one DataFrame.

        A '_source' column records which file each row came from so the
        combined dataset can still be filtered or grouped by source file.
        """
        files = self.get_excel_files()
        if not files:
            return pd.DataFrame()

        dfs = []
        for filename in files:
            try:
                df = self._load_single(filename).copy()
                df["_source"] = filename
                dfs.append(df)
            except Exception as e:
                logger.warning(f"Skipped {filename} in combined load: {e}")

        if not dfs:
            return pd.DataFrame()

        combined = pd.concat(dfs, ignore_index=True, sort=False)
        logger.info(f"Combined dataset: {combined.shape[0]} rows, {combined.shape[1]} columns from {len(dfs)} file(s)")
        return combined

    def load_file(self, filename: str) -> pd.DataFrame:
        """Load a file by name, or the combined dataset when filename is '__all__'."""
        if filename == COMBINED_KEY:
            return self.load_combined()
        return self._load_single(filename)
    
    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all Excel files"""
        data = {}
        for filename in self.get_excel_files():
            try:
                data[filename] = self._load_single(filename)
            except Exception as e:
                logger.warning(f"Skipped {filename}: {str(e)}")
        return data

    def get_file_info(self) -> List[Dict]:
        """Get information about all available data files"""
        info = []
        for filename in self.get_excel_files():
            file_path = self.data_dir / filename
            try:
                df = self._load_single(filename)
                info.append({
                    "name": filename,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "size_mb": file_path.stat().st_size / (1024 * 1024),
                    "headers": df.columns.tolist()
                })
            except Exception as e:
                logger.warning(f"Could not get info for {filename}: {str(e)}")
        return info


def get_loader() -> DataLoader:
    """Get singleton DataLoader instance"""
    return DataLoader()
