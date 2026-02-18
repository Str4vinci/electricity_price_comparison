# Electricity Price Comparison

A Python tool to compare electricity contracts, including support for **Portuguese Time-of-Use (TOU)** tariffs.

## New Features: TOU Support
- **Portuguese Market Support**: Includes built-in logic for Daily/Weekly cycles and 2025 schedules.
- **Consumption Estimation**: Uses a normalized load profile (RLP) to estimate annual consumption based on a single month's bill.
- **Tariff Types**: Supports Simple, Bi-hourly (Bi-horário), and Tri-hourly (Tri-horário) tariffs.

> [!NOTE]  
> The load profile used for estimation (`rlp/EREDES_2025_BTN_1000kwh_15min.csv`) is specific to standard residential consumers (**BTN C**) in **Portugal**. Results may vary for other regions or profiles.

## Usage

### Interactive Mode
Run the script and follow the prompts to select tariff type, cycle, and input rates:
```bash
python compare_price.py
```

### Command Line Mode

#### Simple Tariff
```bash
python price_comparison_argparse.py \
  --price1 0.15 --fee1 0.50 \
  --price2 0.14 --fee2 0.60 \
  --ref-kwh 3500
```

#### TOU Tariff (Bi-hourly Daily)
```bash
python price_comparison_argparse.py \
  --tariff-type bi-hourly \
  --cycle daily \
  --price1 0.20 0.10 --fee1 0.50 \
  --price2 0.18 0.12 --fee2 0.40 \
  --ref-kwh 500 --ref-month 1
```
*Note: `--ref-month 1` means the 500 kWh consumption is for January. The tool estimates annual consumption based on this.*

## Features
- Calculates annual cost for Simple and TOU contracts.
- Identifies the cheaper contract.
- Detailed breakdown of consumption per TOU period.
- Break-even analysis (Simple tariff only).
