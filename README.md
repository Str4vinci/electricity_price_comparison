# Electricity Price Comparison

A simple Python tool to compare two electricity contracts and find the break-even point based on annual consumption.

## Requirements
- Python 3.x
- No external dependencies required


## Usage

### Interactive Mode
Run the script and follow the prompts:
```bash
python compare_price.py
```

### Command Line Mode
Pass contract details as arguments:
```bash
python price_comparison_argparse.py \
  --price1 0.15 --fee1 0.50 \
  --price2 0.14 --fee2 0.60 \
  --consumption 3500
```

## features
- Calculates total annual cost for two contracts.
- Identifies the cheaper contract for a given consumption.
- Computes the break-even consumption point where both contracts cost the same.
