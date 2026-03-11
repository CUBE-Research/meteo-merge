#!/usr/bin/env python3
"""
Merge weather CSV files into a single CSV file.

Usage:
    python merge_meteo_csv.py <input_directory> <output_filename> [--interpolation METHOD]

Example:
    python merge_meteo_csv.py /path/to/csv_folder merged_output.csv
    python merge_meteo_csv.py /path/to/csv_folder merged_output.csv --interpolation ffill

Note:
    The 'time' column is automatically converted to five separate columns:
    - 'year': Year (e.g., 2024)
    - 'day': Day of year (1-365 or 1-366 for leap years)
    - 'hour': Hour of day (0-23)
    - 'minute': Minute of hour (0-59)
    - 'decimal_time': Time in decimal format (e.g., 14.5 for 14:30:00)
"""

import argparse
import sys
from pathlib import Path

import pandas as pd


def validate_time_column(csv_file: Path) -> bool:
    """Check if the CSV file contains the 'time' column."""
    try:
        df_header = pd.read_csv(csv_file, nrows=0)
        return "time" in df_header.columns
    except Exception as e:
        print(f"Error reading {csv_file.name}: {e}")
        return False


def load_csv_files(input_dir: Path) -> list[pd.DataFrame]:
    """Load all valid CSV files from the input directory."""
    csv_files = sorted(input_dir.glob("*.csv"))

    if not csv_files:
        print(f"Error: no CSV files found in {input_dir}")
        sys.exit(1)

    dfs = []

    for csv_file in csv_files:
        if not validate_time_column(csv_file):
            print(
                f"Warning: {csv_file.name} does not contain the 'time' column and will not be processed"
            )
            continue

        try:
            print(f"Reading: {csv_file.name}...")
            df = pd.read_csv(csv_file, parse_dates=["time"])
            dfs.append(df)
            print(f"  -> {len(df)} rows loaded")
        except Exception as e:
            print(f"Error loading {csv_file.name}: {e}")
            continue

    return dfs


def merge_dataframes(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """Merge all DataFrames using outer join on the 'time' column."""
    if not dfs:
        print("Error: no valid DataFrame to merge")
        sys.exit(1)

    print(f"\nMerging {len(dfs)} files...")

    merged = dfs[0]
    for i, df in enumerate(dfs[1:], start=2):
        print(f"  Merging file {i}/{len(dfs)}...")
        merged = pd.merge(merged, df, on="time", how="outer")

    return merged


def interpolate_missing_values(
    df: pd.DataFrame, method: str = "linear"
) -> pd.DataFrame:
    """
    Interpolate missing values using the specified method.

    Args:
        df: DataFrame with the data
        method: Interpolation method ('linear', 'ffill', 'bfill', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic')

    Returns:
        DataFrame with interpolated values
    """
    print(f"\nInterpolating missing values (method: {method})...")
    df = df.sort_values("time").reset_index(drop=True)

    missing_before = df.isnull().sum().sum()

    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns

    if method == "ffill":
        df[numeric_columns] = df[numeric_columns].ffill()
    elif method == "bfill":
        df[numeric_columns] = df[numeric_columns].bfill()
    else:
        df[numeric_columns] = df[numeric_columns].interpolate(method=method)

    missing_after = df.isnull().sum().sum()
    filled_count = missing_before - missing_after

    print(f"  -> {filled_count} values interpolated")

    if missing_after > 0:
        print(
            f"  -> Warning: {missing_after} values still missing (probably at the edges)"
        )

    return df


def convert_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the 'time' column to five separate columns: year, day, hour, minute, and decimal_time.

    Args:
        df: DataFrame with a 'time' column containing timestamps

    Returns:
        DataFrame with 'year', 'day', 'hour', 'minute', and 'decimal_time' columns instead of 'time'
    """
    print("\nConverting time column to year, day, hour, minute, and decimal_time...")

    # Extract year
    df["year"] = df["time"].dt.year

    # Extract day of year (1-365 or 1-366)
    df["day"] = df["time"].dt.dayofyear

    # Extract hour (0-23)
    df["hour"] = df["time"].dt.hour

    # Extract minute (0-59)
    df["minute"] = df["time"].dt.minute

    # Calculate decimal time (hour + minute/60 + second/3600)
    df["decimal_time"] = (
        df["time"].dt.hour
        + df["time"].dt.minute / 60
        + df["time"].dt.second / 3600
    )

    # Remove the original time column
    df = df.drop(columns=["time"])

    # Reorder columns to put year, day, hour, minute, decimal_time first
    cols = ["year", "day", "hour", "minute", "decimal_time"] + [
        col for col in df.columns if col not in ["year", "day", "hour", "minute", "decimal_time"]
    ]
    df = df[cols]

    print(f"  -> Time column converted to year, day, hour, minute, decimal_time")

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Merge weather CSV files into a single CSV file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available interpolation methods:
    linear      - Linear interpolation (default)
    ffill       - Forward fill (fills with the last valid value)
    bfill       - Backward fill (fills with the next valid value)
    nearest     - Nearest value
    zero        - Zero step interpolation
    slinear     - Linear spline interpolation
    quadratic   - Quadratic spline interpolation
    cubic       - Cubic spline interpolation

Example:
    python merge_meteo_csv.py /path/to/csv_folder merged_output.csv
    python merge_meteo_csv.py /path/to/csv_folder merged_output.csv --interpolation ffill
        """,
    )

    parser.add_argument(
        "input_directory",
        type=str,
        help="Path of the directory containing the CSV files to merge",
    )

    parser.add_argument(
        "output_filename",
        type=str,
        help="Name of the output CSV file (saved in the input directory)",
    )

    parser.add_argument(
        "-i",
        "--interpolation",
        type=str,
        default="linear",
        choices=[
            "linear",
            "ffill",
            "bfill",
            "nearest",
            "zero",
            "slinear",
            "quadratic",
            "cubic",
        ],
        help="Interpolation method for missing values (default: linear)",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_directory)

    if not input_dir.exists():
        print(f"Error: the path {input_dir} does not exist")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)

    print(f"Input directory: {input_dir.absolute()}")
    print(f"Output file: {args.output_filename}")
    print(f"Interpolation method: {args.interpolation}\n")

    dfs = load_csv_files(input_dir)

    if not dfs:
        print("Error: no valid CSV files found")
        sys.exit(1)

    print(f"\n{len(dfs)} valid CSV files found")

    merged = merge_dataframes(dfs)

    merged = interpolate_missing_values(merged, method=args.interpolation)

    merged = convert_time_columns(merged)

    output_path = input_dir / args.output_filename

    print(f"\nSaving to: {output_path}")
    merged.to_csv(output_path, index=False)

    print(f"\nCompleted!")
    print(f"  -> Merged file: {output_path}")
    print(f"  -> Total rows: {len(merged)}")
    print(f"  -> Columns: {list(merged.columns)}")


if __name__ == "__main__":
    main()
