#!/usr/bin/env python3
"""
Unifica file CSV meteo in un unico file CSV.

Usage:
    python merge_meteo_csv.py <input_directory> <output_filename> [--interpolation METHOD]

Example:
    python merge_meteo_csv.py /path/to/csv_folder merged_output.csv
    python merge_meteo_csv.py /path/to/csv_folder merged_output.csv --interpolation ffill
"""

import argparse
import sys
from pathlib import Path

import pandas as pd


def validate_time_column(csv_file: Path) -> bool:
    """Verifica se il file CSV contiene la colonna 'time'."""
    try:
        df_header = pd.read_csv(csv_file, nrows=0)
        return "time" in df_header.columns
    except Exception as e:
        print(f"Errore durante la lettura di {csv_file.name}: {e}")
        return False


def load_csv_files(input_dir: Path) -> list[pd.DataFrame]:
    """Carica tutti i file CSV validi dalla cartella di input."""
    csv_files = sorted(input_dir.glob("*.csv"))

    if not csv_files:
        print(f"Errore: nessun file CSV trovato in {input_dir}")
        sys.exit(1)

    dfs = []

    for csv_file in csv_files:
        if not validate_time_column(csv_file):
            print(
                f"Warning: {csv_file.name} non contiene la colonna 'time' e non verrà processato"
            )
            continue

        try:
            print(f"Lettura: {csv_file.name}...")
            df = pd.read_csv(csv_file, parse_dates=["time"])
            dfs.append(df)
            print(f"  -> {len(df)} righe caricate")
        except Exception as e:
            print(f"Errore durante il caricamento di {csv_file.name}: {e}")
            continue

    return dfs


def merge_dataframes(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """Esegue il merge di tutti i DataFrame usando outer join sulla colonna 'time'."""
    if not dfs:
        print("Errore: nessun DataFrame valido da unire")
        sys.exit(1)

    print(f"\nMerge di {len(dfs)} file...")

    merged = dfs[0]
    for i, df in enumerate(dfs[1:], start=2):
        print(f"  Merge file {i}/{len(dfs)}...")
        merged = pd.merge(merged, df, on="time", how="outer")

    return merged


def interpolate_missing_values(
    df: pd.DataFrame, method: str = "linear"
) -> pd.DataFrame:
    """
    Interpola i valori mancanti usando il metodo specificato.

    Args:
        df: DataFrame con i dati
        method: Metodo di interpolazione ('linear', 'ffill', 'bfill', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic')

    Returns:
        DataFrame con valori interpolati
    """
    print(f"\nInterpolazione valori mancanti (metodo: {method})...")
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

    print(f"  -> {filled_count} valori interpolati")

    if missing_after > 0:
        print(
            f"  -> Warning: {missing_after} valori ancora mancanti (probabilmente ai bordi)"
        )

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Unifica file CSV meteo in un unico file CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Metodi di interpolazione disponibili:
    linear      - Interpolazione lineare (default)
    ffill       - Forward fill (riempie con l'ultimo valore valido)
    bfill       - Backward fill (riempie con il prossimo valore valido)
    nearest     - Valore più vicino
    zero        - Interpolazione a gradino zero
    slinear     - Interpolazione lineare spline
    quadratic   - Interpolazione quadratica spline
    cubic       - Interpolazione cubica spline

Esempio:
    python merge_meteo_csv.py /path/to/csv_folder merged_output.csv
    python merge_meteo_csv.py /path/to/csv_folder merged_output.csv --interpolation ffill
        """,
    )

    parser.add_argument(
        "input_directory",
        type=str,
        help="Percorso della cartella contenente i file CSV da unificare",
    )

    parser.add_argument(
        "output_filename",
        type=str,
        help="Nome del file CSV di output (salvato nella cartella di input)",
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
        help="Metodo di interpolazione per valori mancanti (default: linear)",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_directory)

    if not input_dir.exists():
        print(f"Errore: il percorso {input_dir} non esiste")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"Errore: {input_dir} non è una cartella")
        sys.exit(1)

    print(f"Cartella di input: {input_dir.absolute()}")
    print(f"File di output: {args.output_filename}")
    print(f"Metodo interpolazione: {args.interpolation}\n")

    dfs = load_csv_files(input_dir)

    if not dfs:
        print("Errore: nessun file CSV valido trovato")
        sys.exit(1)

    print(f"\n{len(dfs)} file CSV validi trovati")

    merged = merge_dataframes(dfs)

    merged = interpolate_missing_values(merged, method=args.interpolation)

    output_path = input_dir / args.output_filename

    print(f"\nSalvataggio in: {output_path}")
    merged.to_csv(output_path, index=False)

    print(f"\nCompletato!")
    print(f"  -> File unificato: {output_path}")
    print(f"  -> Righe totali: {len(merged)}")
    print(f"  -> Colonne: {list(merged.columns)}")


if __name__ == "__main__":
    main()
