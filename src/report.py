# WARNING: template code, may need edits

"""Generate cleaning reports."""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from src.config import CleaningConfig
from src.utils import format_duration


class CleaningReport:
    """Generate cleaning report from statistics."""

    def __init__(self, stats: Dict[str, Any], config: CleaningConfig):
        self.stats = stats
        self.config = config

    def generate(self) -> str:
        """Generate report text."""
        lines = [
            "="*60,
            "AIS DATA CLEANING REPORT",
            "="*60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SUMMARY",
            "-"*60,
            f"Initial records:        {self.stats.get('initial_count', 0):,}",
            f"Final records:          {self.stats.get('final_count', 0):,}",
            f"Records removed:        {self.stats.get('total_removed', 0):,}",
            f"Removal percentage:     {self.stats.get('removal_percentage', 0):.2f}%",
            f"Processing time:        {format_duration(self.stats.get('processing_time', 0))}",
            "",
            "REMOVAL BREAKDOWN",
            "-"*60,
            f"Validation phase:       {self.stats.get('validation_removed', 0):,}",
            f"Filtering phase:        {self.stats.get('filtering_removed', 0):,}",
            "",
            "CONFIGURATION",
            "-"*60,
            f"Coordinate validation:  Enabled",
            f"  Latitude range:       [{self.config.coordinates.latitude_min}, {self.config.coordinates.latitude_max}]",
            f"  Longitude range:      [{self.config.coordinates.longitude_min}, {self.config.coordinates.longitude_max}]",
            f"  Remove null island:   {self.config.coordinates.remove_null_island}",
            "",
            f"MMSI validation:        Enabled",
            f"  Valid range:          [{self.config.mmsi.min_value}, {self.config.mmsi.max_value}]",
            f"  Remove test MMSI:     {self.config.mmsi.remove_test_mmsi}",
            "",
            f"Speed validation:       Enabled",
            f"  Valid range:          [{self.config.speed.min_value}, {self.config.speed.max_value}] knots",
            f"  Max acceleration:     {self.config.speed.max_acceleration} knots/min",
            "",
            f"Spatial filtering:      Enabled",
            f"  Max distance jump:    {self.config.spatial.max_distance_jump} km",
            "",
            f"Temporal filtering:     Enabled",
            f"  Max time gap:         {self.config.temporal.max_time_gap} hours",
            f"  Remove duplicates:    {self.config.temporal.remove_duplicate_timestamps}",
            "",
            f"Outlier detection:      {'Enabled' if self.config.outliers.enabled else 'Disabled'}",
        ]
        
        if self.config.outliers.enabled:
            lines.extend([
                f"  Z-score threshold:    {self.config.outliers.z_score_threshold}",
                f"  Columns:              {', '.join(self.config.outliers.columns)}",
            ])
        
        lines.extend([
            "",
            "="*60,
            "END OF REPORT",
            "="*60,
        ])
        
        return "\n".join(lines)

    def save(self, output_path: Path) -> None:
        """Save report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(self.generate())

    def print(self) -> None:
        """Print report to console."""
        print(self.generate())
