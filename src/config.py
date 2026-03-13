# WARNING: template code, may need edits

"""Configuration management for AIS Data Cleaner."""

from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field, validator


class CoordinateConfig(BaseModel):
    """Coordinate validation configuration."""
    latitude_min: float = -90.0
    latitude_max: float = 90.0
    longitude_min: float = -180.0
    longitude_max: float = 180.0
    remove_null_island: bool = True


class MMSIConfig(BaseModel):
    """MMSI validation configuration."""
    min_value: int = 100000000
    max_value: int = 999999999
    remove_test_mmsi: bool = True


class SpeedConfig(BaseModel):
    """Speed validation configuration."""
    min_value: float = 0.0
    max_value: float = 50.0
    max_acceleration: float = 10.0


class CourseConfig(BaseModel):
    """Course validation configuration."""
    min_value: float = 0.0
    max_value: float = 360.0


class TemporalConfig(BaseModel):
    """Temporal validation configuration."""
    remove_duplicate_timestamps: bool = True
    max_time_gap: int = 24
    min_time_between_updates: int = 1


class SpatialConfig(BaseModel):
    """Spatial validation configuration."""
    remove_on_land: bool = False
    max_distance_jump: float = 500.0


class DuplicatesConfig(BaseModel):
    """Duplicate removal configuration."""
    subset: List[str] = ["mmsi", "timestamp", "latitude", "longitude"]
    keep: str = "first"


class OutliersConfig(BaseModel):
    """Outlier detection configuration."""
    enabled: bool = True
    z_score_threshold: float = 3.5
    columns: List[str] = ["speed", "course"]


class OutputConfig(BaseModel):
    """Output configuration."""
    compression: str = "snappy"
    add_metadata: bool = True
    generate_report: bool = True


class CleaningConfig(BaseModel):
    """Main cleaning configuration."""
    coordinates: CoordinateConfig = Field(default_factory=CoordinateConfig)
    mmsi: MMSIConfig = Field(default_factory=MMSIConfig)
    speed: SpeedConfig = Field(default_factory=SpeedConfig)
    course: CourseConfig = Field(default_factory=CourseConfig)
    temporal: TemporalConfig = Field(default_factory=TemporalConfig)
    spatial: SpatialConfig = Field(default_factory=SpatialConfig)
    duplicates: DuplicatesConfig = Field(default_factory=DuplicatesConfig)
    outliers: OutliersConfig = Field(default_factory=OutliersConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)

    @classmethod
    def from_yaml(cls, path: Path) -> "CleaningConfig":
        """Load configuration from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)


def load_config(config_path: Optional[Path] = None) -> CleaningConfig:
    """Load cleaning configuration."""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "cleaning_rules.yaml"
    
    if config_path.exists():
        return CleaningConfig.from_yaml(config_path)
    return CleaningConfig()
