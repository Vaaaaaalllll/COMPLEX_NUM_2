# WARNING: template code, may need edits

"""Tests for AIS filters."""

import pandas as pd
import pytest

from src.filters import AISFilter


class TestAISFilter:
    """Test AIS filter functions."""

    def test_remove_duplicates(self, cleaner, invalid_ais_data):
        """Test duplicate removal."""
        initial_count = len(invalid_ais_data)
        df_clean = cleaner.filter.remove_duplicates(invalid_ais_data)
        assert len(df_clean) < initial_count

    def test_remove_temporal_duplicates(self, cleaner):
        """Test temporal duplicate removal."""
        df = pd.DataFrame({
            "mmsi": [123456789, 123456789, 234567890],
            "timestamp": pd.to_datetime([
                "2024-01-01 00:00:00",
                "2024-01-01 00:00:00",
                "2024-01-01 00:00:00",
            ], utc=True),
            "latitude": [37.7749, 37.7750, 37.7751],
            "longitude": [-122.4194, -122.4195, -122.4196],
        })
        df_clean = cleaner.filter.remove_temporal_duplicates(df)
        assert len(df_clean) == 2

    def test_filter_speed_jumps(self, cleaner):
        """Test speed jump filtering."""
        df = pd.DataFrame({
            "mmsi": [123456789] * 3,
            "timestamp": pd.to_datetime([
                "2024-01-01 00:00:00",
                "2024-01-01 00:01:00",
                "2024-01-01 00:02:00",
            ], utc=True),
            "latitude": [37.7749, 37.7750, 37.7751],
            "longitude": [-122.4194, -122.4193, -122.4192],
            "speed": [10.0, 50.0, 11.0],  # Unrealistic jump
        })
        df_clean = cleaner.filter.filter_speed_jumps(df)
        assert len(df_clean) < len(df)

    def test_apply_all_filters(self, cleaner, sample_ais_data):
        """Test applying all filters."""
        df_clean = cleaner.filter.apply_all_filters(sample_ais_data)
        assert len(df_clean) <= len(sample_ais_data)
