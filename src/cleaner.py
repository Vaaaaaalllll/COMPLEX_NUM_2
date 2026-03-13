# WARNING: template code, may need edits

"""Main AIS Data Cleaner class."""

import time
from pathlib import Path
from typing import Optional, Dict, Any

import pandas as pd
from loguru import logger

from src.config import CleaningConfig, load_config
from src.validators import AISValidator
from src.filters import AISFilter
from src.report import CleaningReport


class AISCleaner:
    """Main class for cleaning AIS data from Parquet files."""

    def __init__(self, config: Optional[CleaningConfig] = None):
        """Initialize AIS Cleaner.
        
        Args:
            config: Cleaning configuration. If None, loads from default config file.
        """
        self.config = config or load_config()
        self.validator = AISValidator(self.config)
        self.filter = AISFilter(self.config)
        self.stats: Dict[str, Any] = {}

    def read_parquet(self, file_path: Path) -> pd.DataFrame:
        """Read AIS data from Parquet file."""
        logger.info(f"Reading Parquet file: {file_path}")
        
        df = pd.read_parquet(file_path)
        logger.info(f"Loaded {len(df)} records")
        
        # Standardize column names (lowercase)
        df.columns = df.columns.str.lower()
        
        # Parse timestamp if exists
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        
        return df

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean AIS dataframe."""
        logger.info("Starting data cleaning pipeline...")
        start_time = time.time()
        
        initial_count = len(df)
        self.stats["initial_count"] = initial_count
        
        # Validation phase
        valid_mask = self.validator.validate_all(df)
        df_valid = df[valid_mask].copy()
        self.stats["validation_removed"] = initial_count - len(df_valid)
        
        # Filtering phase
        df_clean = self.filter.apply_all_filters(df_valid)
        self.stats["filtering_removed"] = len(df_valid) - len(df_clean)
        
        # Final statistics
        self.stats["final_count"] = len(df_clean)
        self.stats["total_removed"] = initial_count - len(df_clean)
        self.stats["removal_percentage"] = (
            self.stats["total_removed"] / initial_count * 100
        )
        self.stats["processing_time"] = time.time() - start_time
        
        logger.info(
            f"Cleaning complete: {self.stats['total_removed']} records removed "
            f"({self.stats['removal_percentage']:.2f}%) in {self.stats['processing_time']:.2f}s"
        )
        
        # Add metadata if configured
        if self.config.output.add_metadata:
            df_clean["cleaned_at"] = pd.Timestamp.now()
            df_clean["cleaner_version"] = "0.1.0"
        
        return df_clean

    def save_parquet(self, df: pd.DataFrame, output_path: Path) -> None:
        """Save cleaned data to Parquet file."""
        logger.info(f"Saving cleaned data to: {output_path}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_parquet(
            output_path,
            compression=self.config.output.compression,
            index=False,
        )
        
        file_size = output_path.stat().st_size
        logger.info(f"Saved {len(df)} records ({file_size / 1024 / 1024:.2f} MB)")

    def clean_file(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        generate_report: bool = None,
    ) -> pd.DataFrame:
        """Clean AIS data from Parquet file.
        
        Args:
            input_path: Path to input Parquet file
            output_path: Path to output Parquet file. If None, uses input_path with '_clean' suffix
            generate_report: Whether to generate cleaning report. If None, uses config setting
        
        Returns:
            Cleaned DataFrame
        """
        input_path = Path(input_path)
        
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_clean.parquet"
        else:
            output_path = Path(output_path)
        
        # Read data
        df = self.read_parquet(input_path)
        
        # Clean data
        df_clean = self.clean_dataframe(df)
        
        # Save cleaned data
        self.save_parquet(df_clean, output_path)
        
        # Generate report if configured
        if generate_report is None:
            generate_report = self.config.output.generate_report
        
        if generate_report:
            report = CleaningReport(self.stats, self.config)
            report_path = output_path.parent / f"{output_path.stem}_report.txt"
            report.save(report_path)
        
        return df_clean

    def clean_directory(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
        pattern: str = "*.parquet",
    ) -> None:
        """Clean all Parquet files in a directory.
        
        Args:
            input_dir: Directory containing input Parquet files
            output_dir: Directory for output files. If None, uses input_dir
            pattern: File pattern to match
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir) if output_dir else input_dir
        
        parquet_files = list(input_dir.glob(pattern))
        logger.info(f"Found {len(parquet_files)} Parquet files to clean")
        
        for i, input_file in enumerate(parquet_files, 1):
            logger.info(f"Processing file {i}/{len(parquet_files)}: {input_file.name}")
            output_file = output_dir / f"{input_file.stem}_clean.parquet"
            
            try:
                self.clean_file(input_file, output_file)
            except Exception as e:
                logger.error(f"Error processing {input_file.name}: {e}")
                continue
        
        logger.info(f"Batch cleaning complete: {len(parquet_files)} files processed")
