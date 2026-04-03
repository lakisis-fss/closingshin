---
name: VCP Scanner (Korean Stock Market)
description: Analyzes KOSPI/KOSDAQ stocks to find Volatility Contraction Patterns (VCP).
version: 1.0.0
---

# VCP Scanner (Korean Stock Market)

## Description
This skill scans the Korean stock market (KOSPI & KOSDAQ) to identify stocks exhibiting Mark Minervini's **Video Contraction Pattern (VCP)**. It filters stocks based on recent momentum (price increase ranking) and then analyzes their price action for volatility contraction characteristics.

## Prerequisites
*   Python 3.8+
*   `pykrx`, `pandas` installed in the environment.

## Usage

You can run this skill using the provided python script `run_scan.py`.

### Parameters

| Parameter | Flag | Default | Description |
| :--- | :--- | :--- | :--- |
| **Lookback Days** | `--lookback` | `50` | Number of days to calculate price percentage change for ranking (Momentum). |
| **Top N** | `--top_n` | `30` | Number of top performing stocks to select from each market (KOSPI/KOSDAQ). |
| **Min Contractions** | `--min_contraction` | `2` | Minimum number of volatility contractions required (e.g., 2T, 3T). |
| **Output File** | `--output` | `vcp_scan_result.csv` | Path to save the result CSV file. |

### Example Commands

**1. Basic Scan (Default settings)**
```bash
python run_scan.py
```

**2. Focus on recent strong momentum (Top 50 stocks over last 20 days)**
```bash
python run_scan.py --lookback 20 --top_n 50 --output fast_movers.csv
```

**3. Strict VCP criteria (At least 3 contractions)**
```bash
python run_scan.py --min_contraction 3 --output tight_vcp.csv
```

## Output Format (CSV)
The resulting CSV file contains:
*   `date`: Scan date
*   `ticker`: Stock code (6 digits)
*   `name`: Stock name
*   `market`: KOSPI or KOSDAQ
*   `close`: Closing price
*   `contractions_cnt`: Number of contractions found
*   `last_depth_pct`: Percentage depth of the last contraction (smaller is better)
*   `vol_dry_up`: Whether volume has dried up (True/False)
*   `vol_ratio`: Current volume ratio compared to 50-day average
