# WARNING: template code, may need edits

"""Utility functions for AIS data processing."""

import numpy as np
import pandas as pd
from typing import Union


def calculate_distance(
    lat1: Union[float, pd.Series],
    lon1: Union[float, pd.Series],
    lat2: Union[float, pd.Series],
    lon2: Union[float, pd.Series],
) -> Union[float, pd.Series]:
    """Calculate great circle distance between points using Haversine formula.
    
    Args:
        lat1, lon1: Starting point coordinates (degrees)
        lat2, lon2: Ending point coordinates (degrees)
    
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Earth radius in kilometers
    r = 6371.0
    
    return r * c


def calculate_bearing(
    lat1: Union[float, pd.Series],
    lon1: Union[float, pd.Series],
    lat2: Union[float, pd.Series],
    lon2: Union[float, pd.Series],
) -> Union[float, pd.Series]:
    """Calculate initial bearing between two points.
    
    Args:
        lat1, lon1: Starting point coordinates (degrees)
        lat2, lon2: Ending point coordinates (degrees)
    
    Returns:
        Bearing in degrees (0-360)
    """
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    
    x = np.sin(dlon) * np.cos(lat2_rad)
    y = np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(dlon)
    
    bearing = np.arctan2(x, y)
    bearing_degrees = np.degrees(bearing)
    
    # Normalize to 0-360
    return (bearing_degrees + 360) % 360


def calculate_time_diff(timestamps: pd.Series) -> pd.Series:
    """Calculate time difference between consecutive timestamps.
    
    Args:
        timestamps: Series of timestamps
    
    Returns:
        Series of time differences in seconds
    """
    return timestamps.diff().dt.total_seconds()


def knots_to_kmh(knots: Union[float, pd.Series]) -> Union[float, pd.Series]:
    """Convert speed from knots to km/h."""
    return knots * 1.852


def kmh_to_knots(kmh: Union[float, pd.Series]) -> Union[float, pd.Series]:
    """Convert speed from km/h to knots."""
    return kmh / 1.852


def normalize_mmsi(mmsi: Union[int, pd.Series]) -> Union[str, pd.Series]:
    """Normalize MMSI to 9-digit string format."""
    if isinstance(mmsi, pd.Series):
        return mmsi.astype(str).str.zfill(9)
    return str(mmsi).zfill(9)


def parse_timestamp(timestamp: Union[str, pd.Series]) -> Union[pd.Timestamp, pd.Series]:
    """Parse timestamp to pandas Timestamp."""
    return pd.to_datetime(timestamp, utc=True)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def format_size(bytes_size: int) -> str:
    """Format file size to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}TB"
