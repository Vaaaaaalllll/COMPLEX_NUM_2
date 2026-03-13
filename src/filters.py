# WARNING: template code, may need edits

"""Filters for removing noise and outliers from AIS data."""

import numpy as np
import pandas as pd
from loguru import logger
from scipy import stats

from src.config import CleaningConfig
from src.utils import calculate_distance, calculate_time_diff


class AISFilter:
    """Filters for cleaning AIS data."""

    def __init__(self, config: CleaningConfig):
        self.config = config

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records."""
        initial_count = len(df)
        
        # Check if all required columns exist
        subset = [col for col in self.config.duplicates.subset if col in df.columns]
        
        if not subset:
            logger.warning("No columns available for duplicate detection")
            return df
        
        df_clean = df.drop_duplicates(subset=subset, keep=self.config.duplicates.keep)
        
        removed = initial_count - len(df_clean)
        logger.info(f"Removed {removed} duplicate records ({removed/initial_count*100:.2f}%)")
        
        return df_clean

    def remove_temporal_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove records with duplicate timestamps for same MMSI."""
        if not self.config.temporal.remove_duplicate_timestamps:
            return df
        
        if "timestamp" not in df.columns or "mmsi" not in df.columns:
            return df
        
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=["mmsi", "timestamp"], keep="first")
        
        removed = initial_count - len(df_clean)
        if removed > 0:
            logger.info(f"Removed {removed} temporal duplicates")
        
        return df_clean

    def filter_speed_jumps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove records with unrealistic speed changes."""
        if "speed" not in df.columns or "timestamp" not in df.columns:
            return df
        
        df_sorted = df.sort_values(["mmsi", "timestamp"]).copy()
        
        # Calculate speed difference between consecutive points
        df_sorted["speed_diff"] = df_sorted.groupby("mmsi")["speed"].diff().abs()
        df_sorted["time_diff_minutes"] = (
            df_sorted.groupby("mmsi")["timestamp"].diff().dt.total_seconds() / 60
        )
        
        # Calculate acceleration (knots per minute)
        df_sorted["acceleration"] = df_sorted["speed_diff"] / df_sorted["time_diff_minutes"]
        
        # Filter unrealistic accelerations
        valid = (
            df_sorted["acceleration"].isna()
            | (df_sorted["acceleration"] <= self.config.speed.max_acceleration)
        )
        
        removed = (~valid).sum()
        if removed > 0:
            logger.info(f"Removed {removed} records with unrealistic speed jumps")
        
        return df_sorted[valid].drop(columns=["speed_diff", "time_diff_minutes", "acceleration"])

    def filter_distance_jumps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove records with unrealistic position jumps."""
        if not all(col in df.columns for col in ["latitude", "longitude", "timestamp", "mmsi"]):
            return df
        
        df_sorted = df.sort_values(["mmsi", "timestamp"]).copy()
        
        # Calculate distance between consecutive points
        df_sorted["prev_lat"] = df_sorted.groupby("mmsi")["latitude"].shift()
        df_sorted["prev_lon"] = df_sorted.groupby("mmsi")["longitude"].shift()
        
        df_sorted["distance_km"] = calculate_distance(
            df_sorted["prev_lat"],
            df_sorted["prev_lon"],
            df_sorted["latitude"],
            df_sorted["longitude"],
        )
        
        # Filter unrealistic jumps
        valid = (
            df_sorted["distance_km"].isna()
            | (df_sorted["distance_km"] <= self.config.spatial.max_distance_jump)
        )
        
        removed = (~valid).sum()
        if removed > 0:
            logger.info(f"Removed {removed} records with unrealistic position jumps")
        
        return df_sorted[valid].drop(columns=["prev_lat", "prev_lon", "distance_km"])

    def filter_time_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove records with large time gaps."""
        if "timestamp" not in df.columns or "mmsi" not in df.columns:
            return df
        
        df_sorted = df.sort_values(["mmsi", "timestamp"]).copy()
        
        df_sorted["time_gap_hours"] = (
            df_sorted.groupby("mmsi")["timestamp"].diff().dt.total_seconds() / 3600
        )
        
        valid = (
            df_sorted["time_gap_hours"].isna()
            | (df_sorted["time_gap_hours"] <= self.config.temporal.max_time_gap)
        )
        
        removed = (~valid).sum()
        if removed > 0:
            logger.info(f"Removed {removed} records with large time gaps")
        
        return df_sorted[valid].drop(columns=["time_gap_hours"])

    def remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove statistical outliers."""
        if not self.config.outliers.enabled:
            return df
        
        initial_count = len(df)
        valid = pd.Series(True, index=df.index)
        
        for col in self.config.outliers.columns:
            if col not in df.columns:
                continue
            
            # Calculate z-scores
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            outliers = z_scores > self.config.outliers.z_score_threshold
            
            valid.loc[df[col].notna()] &= ~outliers
            
            outlier_count = outliers.sum()
            if outlier_count > 0:
                logger.info(f"Removed {outlier_count} outliers from {col}")
        
        removed = (~valid).sum()
        if removed > 0:
            logger.info(f"Total outliers removed: {removed} ({removed/initial_count*100:.2f}%)")
        
        return df[valid]

    def apply_all_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all filters sequentially."""
        logger.info("Applying filters...")
        initial_count = len(df)
        
        df = self.remove_duplicates(df)
        df = self.remove_temporal_duplicates(df)
        df = self.filter_speed_jumps(df)
        df = self.filter_distance_jumps(df)
        df = self.filter_time_gaps(df)
        df = self.remove_outliers(df)
        
        final_count = len(df)
        total_removed = initial_count - final_count
        logger.info(
            f"Filtering complete: {total_removed} records removed "
            f"({total_removed/initial_count*100:.2f}%)"
        )
        
        return df
