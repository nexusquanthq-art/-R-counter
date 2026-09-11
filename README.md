# Project Ironmind - Trading Journal & R-Multiple Tracker

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
- Handles liquidation scenarios
- Overflow protection for extreme inputs

## How R-Multiples Work

R = Risk unit. If you risk 5% per trade:

- +10% profit = +2R
- -5% loss = -1R
- +25% profit = +5R

This tool tracks your performance in R, which is the professional way to measure trading success.

## Installation

No external libraries needed. Uses only Python standard library.

## How To Run
python Rcounter.py

Features
Dashboard

    Current balance

    Total R accumulated

    Target amount

    R needed to reach goal

Trade Logging

    Enter P/L as percentage (e.g., +12 or -8)

    Automatic R calculation

    Balance updates with compounding

    Trade saved to history

Target Setting

    Set a dollar target

    Shows R needed to reach it

    Goal reached notification

Trade History

    View all logged trades

    Date, P/L %, R value, balance after

    Clean table view

Safety Features

    Overflow protection - Caps R at 10,000 to prevent crashes

    Liquidation detection - If balance drops below 1% of initial, triggers liquidation

    Negative balance prevention - Balance never goes below zero

    Data validation - Checks for corrupted data file

Liquidation Handling

If your balance drops below 1% of initial balance, the app considers you liquidated. You can:

    Start Over - Delete all data and begin fresh

    Add New Balance - Keep history but add new capital

Configuration
Change Risk Per Trade

Open Rcounter.py and go to line 12:
python

RISK_PERCENT = 0.05    # 1R = 5%

Change 0.05 to your preferred risk:

    0.01 = 1% risk per trade

    0.02 = 2% risk per trade

    0.05 = 5% risk per trade

    0.10 = 10% risk per trade

The app automatically recalculates everything based on this value.
Change Starting Balance

Also on line 13:
python

DEFAULT_BALANCE = 100

Change to your starting balance (only used on first run).
Change Liquidation Threshold

On line 14:
python

LIQUIDATION_THRESHOLD = 0.01  # 1% of initial

Change to:

    0.001 = 0.1% (harder to liquidate)

    0.01 = 1% (default)

    0.05 = 5% (easier to liquidate)

Change Max R Cap

On line 15:
python

MAX_R = 10000

Maximum R value allowed in a single trade.
File Structure

    Rcounter.py - Main application

    trading_tracker.json - Auto-generated data file

Data Format

The JSON file stores:
json

{
  "balance": 150.00,
  "initial_balance": 100.00,
  "total_R": 10,
  "target": 500.00,
  "trades": [
    {
      "timestamp": "2025-01-15T10:30:00",
      "percentage": 12.0,
      "rounded_R": 2,
      "balance_after": 112.00
    }
  ]
}

License

All Rights Reserved - See LICENSE file
Author

Nexus

    Telegram: @Nexushqh
