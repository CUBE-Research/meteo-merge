# Meteo CSV Merge Tool

Unifies weather CSV files into a single CSV file with support for missing value interpolation.

## Table of Contents

- [Description](#description)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Linux](#linux-installation)
  - [Windows](#windows-installation)
- [Usage](#usage)
- [Interpolation Methods](#interpolation-methods)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Description

This Python script merges multiple CSV files containing weather data into a single CSV file. It supports:

- Automatic merging of all CSV files in a folder
- Missing value interpolation with various methods
- Automatic time column conversion to year, day, and decimal_time
- Detailed operation logging

**Note:** The input CSV files must have a `time` column with timestamps. This column is automatically converted to three separate columns in the output:
- `year`: Year (e.g., 2024)
- `day`: Day of year (1-365 or 1-366 for leap years)
- `decimal_time`: Time in decimal format (e.g., 14.5 for 14:30:00)

## Prerequisites

### Linux

1. **Python 3.8 or higher**

Check if Python is already installed:
```bash
python3 --version
```

If not installed:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install python3 python3-pip
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
```

### Windows

1. **Python 3.8 or higher**

Check if Python is already installed:
```cmd
python --version
```

If not installed:

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: During installation, select the **"Add Python to PATH"** option
4. Complete the installation

After installation, restart the terminal (Command Prompt or PowerShell) and verify:
```cmd
python --version
pip --version
```

## Installation

### Linux Installation

#### 1. Clone or download the repository

```bash
# If using git
git clone <repository-url>
cd meteo-merge

# Or navigate to the project folder
cd /path/to/meteo-merge
```

#### 2. Create a virtual environment

```bash
# Create the virtual environment
python3 -m venv venv
```

#### 3. Activate the virtual environment

```bash
# Activate the venv
source venv/bin/activate
```

You will see `(venv)` appear in the command prompt.

#### 4. Upgrade pip (recommended)

```bash
pip install --upgrade pip
```

#### 5. Install dependencies

```bash
pip install -r requirements.txt
```

#### 6. Verify installation

```bash
python merge_meteo_csv.py --help
```

### Windows Installation

#### 1. Clone or download the repository

```cmd
# If using git
git clone <repository-url>
cd meteo-merge

# Or navigate to the project folder
cd C:\path\to\meteo-merge
```

#### 2. Create a virtual environment

**Command Prompt:**
```cmd
python -m venv venv
```

**PowerShell:**
```powershell
python -m venv venv
```

#### 3. Activate the virtual environment

**Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

If PowerShell returns a script execution error, run first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You will see `(venv)` appear in the command prompt.

#### 4. Upgrade pip (recommended)

```cmd
pip install --upgrade pip
```

#### 5. Install dependencies

```cmd
pip install -r requirements.txt
```

#### 6. Verify installation

```cmd
python merge_meteo_csv.py --help
```

## Usage

### Activating the virtual environment

Every time you want to use the script, activate the virtual environment first:

**Linux:**
```bash
source venv/bin/activate
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

### Deactivating the virtual environment

When finished, deactivate the environment:

```bash
deactivate
```

### Basic syntax

```bash
python merge_meteo_csv.py <input_directory> <output_filename> [options]
```

### Arguments

- `input_directory`: Path to the folder containing CSV files to merge
- `output_filename`: Name of the output CSV file (will be saved in the input folder)
- `-i, --interpolation`: Interpolation method for missing values (default: linear)

### Examples

#### Basic example (Linux):
```bash
python merge_meteo_csv.py /home/user/weather_data merged_output.csv
```

#### Basic example (Windows):
```cmd
python merge_meteo_csv.py C:\Users\Username\weather_data merged_output.csv
```

#### With forward fill interpolation:
```bash
python merge_meteo_csv.py ./data merged.csv --interpolation ffill
```

#### With cubic interpolation:
```bash
python merge_meteo_csv.py /path/to/csv_folder output.csv -i cubic
```

#### Show help:
```bash
python merge_meteo_csv.py --help
```

## Interpolation Methods

| Method | Description | Recommended Use |
|--------|-------------|-----------------|
| `linear` | Linear interpolation (default) | Data with linear trend, small gap coverage |
| `ffill` | Forward fill (fills with last valid value) | Step-wise data, sensors that maintain value |
| `bfill` | Backward fill (fills with next valid value) | Complementary to ffill |
| `nearest` | Nearest value | Discrete, categorical data |
| `zero` | Zero step interpolation | Data that should not be interpolated |
| `slinear` | Linear spline interpolation | Data requiring smoothness |
| `quadratic` | Quadratic spline interpolation | Data with curved trend |
| `cubic` | Cubic spline interpolation | Data requiring high smoothness |

### Recommendations for weather data:

- **Temperature**: `linear` or `cubic`
- **Humidity**: `linear` or `ffill`
- **Precipitation**: `zero` or `nearest` (avoids negative values)
- **Wind**: `linear` or `ffill`
- **Pressure**: `linear` or `cubic`

## Input CSV File Format

CSV files must have:

1. **`time` column**: Required, contains timestamps
2. **Supported format**: Standard CSV with comma as separator
3. **Header**: Column names in the first row

Example of valid CSV file:
```csv
time,temperature,humidity,pressure
2024-01-01 00:00:00,15.5,78,1013.2
2024-01-01 01:00:00,15.2,80,1013.0
2024-01-01 02:00:00,14.9,82,1012.8
```

## Output Format

The output CSV file will have the `time` column replaced with three columns:

- **`year`**: Year (integer, e.g., 2024)
- **`day`**: Day of year (integer, 1-365 or 1-366 for leap years)
- **`decimal_time`**: Time as decimal number (float, e.g., 14.5 for 14:30:00, 14.75 for 14:45:00)

Example output:
```csv
year,day,decimal_time,temperature,humidity,pressure
2024,1,0.0,15.5,78,1013.2
2024,1,1.0,15.2,80,1013.0
2024,1,2.0,14.9,82,1012.8
```

**Decimal Time Calculation:**
- 00:00:00 → 0.0
- 06:00:00 → 6.0
- 12:30:00 → 12.5
- 14:45:00 → 14.75
- 23:59:59 → 23.999722

## Troubleshooting

### Problem: "python: command not found" (Linux)

**Solution**: Use `python3` instead of `python`:
```bash
python3 merge_meteo_csv.py <args>
```

### Problem: "ModuleNotFoundError: No module named 'pandas'"

**Solution**: Make sure you activated the virtual environment and installed dependencies:
```bash
# Activate venv
source venv/bin/activate  # Linux
venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Problem: "Permission denied" (Linux)

**Solution**: Don't use `sudo` with pip in the virtual environment. If it persists, check folder permissions:
```bash
ls -la
# If necessary, fix permissions
chmod 755 .
```

### Problem: PowerShell doesn't execute scripts (Windows)

**Solution**: Modify the execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: "Error: no CSV files found"

**Solution**: Verify that:
- The folder path is correct
- The folder contains files with `.csv` extension
- CSV files are readable

### Problem: "does not contain 'time' column"

**Solution**: Make sure that:
- CSV files have a column named exactly `time`
- The first row contains the header
- There are no extra spaces in the column name

### Problem: Slow interpolation with large datasets

**Solution**: 
- Use `ffill` or `bfill` which are faster
- Consider processing data in smaller batches
- Verify the system has sufficient RAM

## Uninstallation

To completely remove the environment:

1. Deactivate the virtual environment:
```bash
deactivate
```

2. Delete the `venv` folder:
```bash
# Linux
rm -rf venv

# Windows
rmdir /s venv
```

## System Requirements

- **Operating System**: Linux, Windows 10/11, macOS
- **Python**: 3.8 or higher
- **RAM**: Minimum 512MB (2GB recommended for large files)
- **Disk Space**: ~100MB for the virtual environment

## Dependencies

The project requires the following Python libraries:

- `pandas>=3.0.0` - Data manipulation
- `scipy` - Scientific functions for interpolation

## Contributing

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/new-functionality`)
3. Commit your changes (`git commit -am 'Add new functionality'`)
4. Push the branch (`git push origin feature/new-functionality`)
5. Open a Pull Request

## License

This project is distributed under the MIT license. See the `LICENSE` file for details.

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Open an issue on GitHub with:
   - Problem description
   - Operating system and Python version
   - Complete error output
   - Steps to reproduce the problem

## Changelog

### v1.0.0
- Initial release
- CSV file merge support
- 8 interpolation methods
- Linux and Windows compatibility
