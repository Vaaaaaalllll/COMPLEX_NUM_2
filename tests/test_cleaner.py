# WARNING: template code, may need edits

"""Tests for AIS Cleaner."""

import pandas as pd
import pytest
from pathlib import Path


class TestAISCleaner:
    """Test AIS Cleaner main functionality."""

    def test_read_parquet(self, cleaner, temp_parquet_file):
        """Test reading Parquet file."""
        df = cleaner.read_parquet(temp_parquet_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_clean_dataframe(self, cleaner, sample_ais_data):
        """Test cleaning dataframe."""
        df_clean = cleaner.clean_dataframe(sample_ais_data)
        assert isinstance(df_clean, pd.DataFrame)
        assert len(df_clean) <= len(sample_ais_data)

    def test_clean_dataframe_removes_invalid(self, cleaner, invalid_ais_data):
        """Test that cleaning removes invalid data."""
        df_clean = cleaner.clean_dataframe(invalid_ais_data)
        assert len(df_clean) < len(invalid_ais_data)

    def test_save_parquet(self, cleaner, sample_ais_data, tmp_path):
        """Test saving Parquet file."""
        output_path = tmp_path / "test_output.parquet"
        cleaner.save_parquet(sample_ais_data, output_path)
        assert output_path.exists()

    def test_clean_file(self, cleaner, temp_parquet_file, tmp_path):
        """Test cleaning file end-to-end."""
        output_path = tmp_path / "cleaned.parquet"
        df_clean = cleaner.clean_file(temp_parquet_file, output_path)
        
        assert isinstance(df_clean, pd.DataFrame)
        assert output_path.exists()

    def test_stats_populated(self, cleaner, sample_ais_data):
        """Test that statistics are populated after cleaning."""
        cleaner.clean_dataframe(sample_ais_data)
        
        assert "initial_count" in cleaner.stats
        assert "final_count" in cleaner.stats
        assert "total_removed" in cleaner.stats
        assert "processing_time" in cleaner.stats
