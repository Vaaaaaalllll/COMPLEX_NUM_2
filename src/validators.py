# WARNING: template code, may need edits

"""Validators for AIS data fields."""

import numpy as np
import pandas as pd
from loguru import logger

from src.config import CleaningConfig


class AISValidator:
    """Validates AIS data according to configuration rules."""

    def __init__(self, config: CleaningConfig):
        self.config = config

    def validate_coordinates(self, df: pd.DataFrame) -> pd.Series:
        """Validate latitude and longitude."""
        lat_valid = (
            (df["latitude"] >= self.config.coordinates.latitude_min)
            & (df["latitude"] <= self.config.coordinates.latitude_max)
        )
        lon_valid = (
            (df["longitude"] >= self.config.coordinates.longitude_min)
            & (df["longitude"] <= self.config.coordinates.longitude_max)
        )
        
        valid = lat_valid & lon_valid
        
        if self.config.coordinates.remove_null_island:
            null_island = (df["latitude"] == 0) & (df["longitude"] == 0)
            valid = valid & ~null_island
            logger.info(f"Removed {null_island.sum()} null island points")
        
        invalid_count = (~valid).sum()
        if invalid_count > 0:
            logger.info(f"Found {invalid_count} invalid coordinates")
        
        return valid

    def validate_mmsi(self, df: pd.DataFrame) -> pd.Series:
        """Validate MMSI numbers."""
        valid = (
            (df["mmsi"] >= self.config.mmsi.min_value)
            & (df["mmsi"] <= self.config.mmsi.max_value)
        )
        
        if self.config.mmsi.remove_test_mmsi:
            # MMSI starting with 0 are test vessels
            test_mmsi = df["mmsi"].astype(str).str.startswith("0")
            valid = valid & ~test_mmsi
            logger.info(f"Removed {test_mmsi.sum()} test MMSI records")
        
        invalid_count = (~valid).sum()
        if invalid_count > 0:
            logger.info(f"Found {invalid_count} invalid MMSI values")
        
        return valid

    def validate_speed(self, df: pd.DataFrame) -> pd.Series:
        """Validate speed over ground."""
        if "speed" not in df.columns:
            return pd.Series(True, index=df.index)
        
        valid = (
            (df["speed"] >= self.config.speed.min_value)
            & (df["speed"] <= self.config.speed.max_value)
        )
        
        invalid_count = (~valid).sum()
        if invalid_count > 0:
            logger.info(f"Found {invalid_count} invalid speed values")
        
        return valid

    def validate_course(self, df: pd.DataFrame) -> pd.Series:
        """Validate course over ground."""
        if "course" not in df.columns:
            return pd.Series(True, index=df.index)
        
        valid = (
            (df["course"] >= self.config.course.min_value)
            & (df["course"] <= self.config.course.max_value)
        )
        
        invalid_count = (~valid).sum()
        if invalid_count > 0:
            logger.info(f"Found {invalid_count} invalid course values")
        
        return valid

    def validate_timestamp(self, df: pd.DataFrame) -> pd.Series:
        """Validate timestamps."""
        if "timestamp" not in df.columns:
            return pd.Series(True, index=df.index)
        
        # Check for null timestamps
        valid = df["timestamp"].notna()
        
        # Check for future timestamps
        if valid.any():
            future = df.loc[valid, "timestamp"] > pd.Timestamp.now()
            if future.any():
                logger.warning(f"Found {future.sum()} future timestamps")
                valid.loc[valid] = valid.loc[valid] & ~future
        
        invalid_count = (~valid).sum()
        if invalid_count > 0:
            logger.info(f"Found {invalid_count} invalid timestamps")
        
        return valid

    def validate_all(self, df: pd.DataFrame) -> pd.Series:
        """Run all validators and return combined mask."""
        logger.info("Running validation checks...")
        
        valid = pd.Series(True, index=df.index)
        
        valid &= self.validate_coordinates(df)
        valid &= self.validate_mmsi(df)
        valid &= self.validate_speed(df)
        valid &= self.validate_course(df)
        valid &= self.validate_timestamp(df)
        
        total_invalid = (~valid).sum()
        logger.info(f"Total invalid records: {total_invalid} ({total_invalid/len(df)*100:.2f}%)")
        
        return valid
