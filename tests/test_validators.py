# WARNING: template code, may need edits

"""Tests for AIS validators."""

import pandas as pd
import pytest

from src.validators import AISValidator
from src.config import CleaningConfig


class TestAISValidator:
    """Test AIS validator functions."""

    def test_validate_coordinates_valid(self, cleaner, sample_ais_data):
        """Test coordinate validation with valid data."""
        valid = cleaner.validator.validate_coordinates(sample_ais_data)
        assert valid.all()

    def test_validate_coordinates_invalid_latitude(self, cleaner):
        """Test coordinate validation with invalid latitude."""
        df = pd.DataFrame({
            "latitude": [91.0, -91.0, 45.0],
            "longitude": [0.0, 0.0, 0.0],
        })
        valid = cleaner.validator.validate_coordinates(df)
        assert valid.sum() == 1

    def test_validate_coordinates_null_island(self, cleaner):
        """Test removal of null island coordinates."""
        df = pd.DataFrame({
            "latitude": [0.0, 45.0],
            "longitude": [0.0, -122.0],
        })
        valid = cleaner.validator.validate_coordinates(df)
        assert valid.sum() == 1

    def test_validate_mmsi_valid(self, cleaner, sample_ais_data):
        """Test MMSI validation with valid data."""
        valid = cleaner.validator.validate_mmsi(sample_ais_data)
        assert valid.all()

    def test_validate_mmsi_invalid(self, cleaner):
        """Test MMSI validation with invalid data."""
        df = pd.DataFrame({
            "mmsi": [123456789, 99999999, 1000000000, -1],
        })
        valid = cleaner.validator.validate_mmsi(df)
        assert valid.sum() == 1

    def test_validate_speed_valid(self, cleaner, sample_ais_data):
        """Test speed validation with valid data."""
        valid = cleaner.validator.validate_speed(sample_ais_data)
        assert valid.all()

    def test_validate_speed_invalid(self, cleaner):
        """Test speed validation with invalid data."""
        df = pd.DataFrame({
            "speed": [10.0, -5.0, 100.0, 25.0],
        })
        valid = cleaner.validator.validate_speed(df)
        assert valid.sum() == 2

    def test_validate_all(self, cleaner, sample_ais_data):
        """Test combined validation."""
        valid = cleaner.validator.validate_all(sample_ais_data)
        assert valid.all()
