# WARNING: template code, may need edits

# API Reference

## AISCleaner

Main class for cleaning AIS data.

### Methods

#### `__init__(config: Optional[CleaningConfig] = None)`

Initialize the cleaner.

**Parameters:**
- `config`: Cleaning configuration. If None, loads default configuration.

#### `clean_file(input_path: Path, output_path: Optional[Path] = None, generate_report: bool = None) -> pd.DataFrame`

Clean AIS data from a Parquet file.

**Parameters:**
- `input_path`: Path to input Parquet file
- `output_path`: Path to output file (optional)
- `generate_report`: Whether to generate report (optional)

**Returns:**
- Cleaned DataFrame

#### `clean_dataframe(df: pd.DataFrame) -> pd.DataFrame`

Clean AIS DataFrame.

**Parameters:**
- `df`: Input DataFrame

**Returns:**
- Cleaned DataFrame

#### `clean_directory(input_dir: Path, output_dir: Optional[Path] = None, pattern: str = '*.parquet')`

Clean all Parquet files in a directory.

**Parameters:**
- `input_dir`: Input directory
- `output_dir`: Output directory (optional)
- `pattern`: File pattern to match

## AISValidator

Validates AIS data fields.

### Methods

#### `validate_coordinates(df: pd.DataFrame) -> pd.Series`

Validate latitude and longitude.

#### `validate_mmsi(df: pd.DataFrame) -> pd.Series`

Validate MMSI numbers.

#### `validate_speed(df: pd.DataFrame) -> pd.Series`

Validate speed values.

#### `validate_all(df: pd.DataFrame) -> pd.Series`

Run all validators.

## AISFilter

Filters for removing noise and outliers.

### Methods

#### `remove_duplicates(df: pd.DataFrame) -> pd.DataFrame`

Remove duplicate records.

#### `filter_speed_jumps(df: pd.DataFrame) -> pd.DataFrame`

Remove records with unrealistic speed changes.

#### `filter_distance_jumps(df: pd.DataFrame) -> pd.DataFrame`

Remove records with unrealistic position jumps.

#### `apply_all_filters(df: pd.DataFrame) -> pd.DataFrame`

Apply all filters sequentially.

## Utility Functions

### `calculate_distance(lat1, lon1, lat2, lon2) -> float`

Calculate great circle distance between points.

### `calculate_bearing(lat1, lon1, lat2, lon2) -> float`

Calculate initial bearing between points.

### `knots_to_kmh(knots) -> float`

Convert speed from knots to km/h.

### `kmh_to_knots(kmh) -> float`

Convert speed from km/h to knots.
