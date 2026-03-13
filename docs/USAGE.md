# WARNING: template code, may need edits

# Usage Guide

## Installation

```bash
pip install -e .
```

## Command Line Interface

### Clean a Single File

```bash
ais-cleaner clean input.parquet --output cleaned.parquet
```

### Clean a Directory

```bash
ais-cleaner clean data/raw/ --output data/processed/
```

### Validate Without Cleaning

```bash
ais-cleaner validate input.parquet
```

### Display File Information

```bash
ais-cleaner info input.parquet
```

## Python API

### Basic Usage

```python
from src.cleaner import AISCleaner

cleaner = AISCleaner()
df_clean = cleaner.clean_file('input.parquet', 'output.parquet')
```

### Custom Configuration

```python
from src.config import CleaningConfig, SpeedConfig

config = CleaningConfig(
    speed=SpeedConfig(
        min_value=0.0,
        max_value=30.0,
        max_acceleration=5.0
    )
)

cleaner = AISCleaner(config)
df_clean = cleaner.clean_dataframe(df)
```

### Batch Processing

```python
from pathlib import Path

cleaner = AISCleaner()
cleaner.clean_directory(
    input_dir=Path('data/raw'),
    output_dir=Path('data/processed'),
    pattern='*.parquet'
)
```

## Configuration

Edit `config/cleaning_rules.yaml` to customize cleaning parameters:

```yaml
coordinates:
  latitude_min: -90.0
  latitude_max: 90.0
  remove_null_island: true

speed:
  min_value: 0.0
  max_value: 50.0
  max_acceleration: 10.0
```

## Output

- Cleaned Parquet files
- Cleaning reports (if enabled)
- Statistics and logs
