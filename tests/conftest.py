# WARNING: template code, may need edits

"""Pytest configuration and fixtures."""

import pandas as pd
import pytest
from pathlib import Path
import tempfile

from src.config import CleaningConfig
from src.cleaner import AISCleaner


@pytest.fixture
def sample_ais_data():
    """Generate sample AIS data for testing."""
    return pd.DataFrame({
        "mmsi": [123456789, 234567890, 345678901, 123456789, 456789012],
        "timestamp": pd.to_datetime([
            "2024-01-01 00:00:00",
            "2024-01-01 00:05:00",
            "2024-01-01 00:10:00",
            "2024-01-01 00:15:00",
            "2024-01-01 00:20:00",
        ], utc=True),
        "latitude": [37.7749, 37.7750, 37.7751, 37.7752, 37.7753],
        "longitude": [-122.4194, -122.4193, -122.4192, -122.4191, -122.4190],
        "speed": [10.5, 11.2, 10.8, 11.0, 10.9],
        "course": [45.0, 46.0, 45.5, 45.8, 45.3],
    })


@pytest.fixture
def invalid_ais_data():
    """Generate invalid AIS data for testing."""
    return pd.DataFrame({
        "mmsi": [123456789, 999999999, 0, -1, 123456789],
        "timestamp": pd.to_datetime([
            "2024-01-01 00:00:00",
            "2024-01-01 00:05:00",
            "2024-01-01 00:10:00",
            "2024-01-01 00:15:00",
            "2024-01-01 00:00:00",  # Duplicate
        ], utc=True),
        "latitude": [37.7749, 91.0, 0.0, 37.7751, 37.7749],  # Invalid: >90, null island
        "longitude": [-122.4194, -122.4193, 0.0, -122.4191, -122.4194],
        "speed": [10.5, 100.0, 10.8, -5.0, 10.5],  # Invalid: >max, negative
        "course": [45.0, 46.0, 400.0, 45.8, 45.0],  # Invalid: >360
    })


@pytest.fixture
def default_config():
    """Default cleaning configuration."""
    return CleaningConfig()


@pytest.fixture
def cleaner(default_config):
    """AIS Cleaner instance."""
    return AISCleaner(default_config)


@pytest.fixture
def temp_parquet_file(sample_ais_data):
    """Create temporary Parquet file."""
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
        temp_path = Path(f.name)
    
    sample_ais_data.to_parquet(temp_path)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()
