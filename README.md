# price-monitoring-report-service

Generate monitoring reports and alert files from price snapshot CSV inputs.

## What it does
- Computes percentage change per item
- Flags items above/below alert threshold
- Produces report markdown + CSV exports

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/build_price_report.py --input examples/prices.csv --output out --alert-threshold 10
```

## Outputs
- `out/price_changes.csv`
- `out/alerts.csv`
- `out/weekly_report.md`
