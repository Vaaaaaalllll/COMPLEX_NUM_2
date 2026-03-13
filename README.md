# AIS Data Cleaner

# WARNING: template code, may need edits

A production-ready tool for cleaning and denoising AIS (Automatic Identification System) data from Parquet files.

## Features

- Read AIS data from Parquet files
- Remove duplicate records
- Filter invalid coordinates
- Remove noise and outliers
- Validate vessel identifiers (MMSI)
- Speed and course validation
- Temporal consistency checks
- Export cleaned data to Parquet

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from src.cleaner import AISCleaner

cleaner = AISCleaner()
df_clean = cleaner.clean_file('input.parquet', 'output_clean.parquet')
```

## Configuration

Edit `config/cleaning_rules.yaml` to customize cleaning parameters.

## Project Structure

- `src/` - Main source code
- `tests/` - Unit and integration tests
- `config/` - Configuration files
- `data/` - Sample data and outputs
- `notebooks/` - Analysis notebooks
- `docs/` - Documentation

## License

MIT
