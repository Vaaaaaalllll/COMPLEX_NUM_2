# WARNING: template code, may need edits

"""Tests for utility functions."""

import pandas as pd
import pytest
import numpy as np

from src.utils import (
    calculate_distance,
    calculate_bearing,
    knots_to_kmh,
    kmh_to_knots,
    normalize_mmsi,
)


class TestUtils:
    """Test utility functions."""

    def test_calculate_distance(self):
        """Test distance calculation."""
        # San Francisco to Los Angeles (approx 559 km)
        distance = calculate_distance(37.7749, -122.4194, 34.0522, -118.2437)
        assert 550 < distance < 570

    def test_calculate_distance_same_point(self):
        """Test distance calculation for same point."""
        distance = calculate_distance(37.7749, -122.4194, 37.7749, -122.4194)
        assert distance < 0.001

    def test_calculate_bearing(self):
        """Test bearing calculation."""
        # North
        bearing = calculate_bearing(0, 0, 1, 0)
        assert 0 <= bearing <= 360

    def test_knots_to_kmh(self):
        """Test knots to km/h conversion."""
        kmh = knots_to_kmh(10)
        assert abs(kmh - 18.52) < 0.01

    def test_kmh_to_knots(self):
        """Test km/h to knots conversion."""
        knots = kmh_to_knots(18.52)
        assert abs(knots - 10) < 0.01

    def test_normalize_mmsi(self):
        """Test MMSI normalization."""
        mmsi = normalize_mmsi(123456789)
        assert mmsi == "123456789"
        
        mmsi = normalize_mmsi(12345)
        assert mmsi == "000012345"

    def test_calculate_distance_series(self):
        """Test distance calculation with pandas Series."""
        lat1 = pd.Series([37.7749, 34.0522])
        lon1 = pd.Series([-122.4194, -118.2437])
        lat2 = pd.Series([34.0522, 37.7749])
        lon2 = pd.Series([-118.2437, -122.4194])
        
        distances = calculate_distance(lat1, lon1, lat2, lon2)
        assert isinstance(distances, pd.Series)
        assert len(distances) == 2
