# Trading Journal & R-Multiple Tracker

A GUI-based trading journal that tracks your balance, R-multiples, and progress toward financial goals.

## What It Does

- Tracks your trading balance
- Calculates total R accumulated
- Sets financial targets
- Shows how many R needed to reach goal
- Logs every trade with P/L percentage
- Saves all data automatically to JSON
- Shows complete trade history in a table
- Clean Tkinter GUI interface

## How R-Multiples Work

R = Risk unit. If you risk 5% per trade:

- +10% profit = +2R
- -5% loss = -1R
- +25% profit = +5R

This tool tracks your performance in R, which is the professional way to measure trading success.

## Installation

No external libraries needed. Uses only Python standard library.

## How To Run

```bash
python Rcounter.py
```

## Features

- First-run setup wizard
- Dashboard with balance, total R, target, R needed
- Trade logging with automatic R calculation
- Target setting with progress tracking
- Trade history viewer
- Auto-save to JSON file
- Data validation and error handling

## Configuration

### Change Risk Per Trade

Open `Rcounter.py` and go to **line 12**:

```python
RISK_PERCENT = 0.05    # 1R = 5%
```

Change `0.05` to your preferred risk:

- `0.01` = 1% risk per trade
- `0.02` = 2% risk per trade
- `0.05` = 5% risk per trade
- `0.10` = 10% risk per trade

The bot automatically recalculates everything based on this value.

### Change Starting Balance

Also on **line 13**:

```python
DEFAULT_BALANCE = 0.81
```

Change to your starting balance (only used on first run).

## File Structure

- `Rcounter.py` - Main application
- `trading_tracker.json` - Auto-generated data file

## License

All Rights Reserved - See LICENSE file

## Author

Nexus
- Telegram: @Nexushqh
```