# 📓 Data Quality Framework — Guide

## Why Data Quality Matters
In supply chain and telecom operations, bad data causes:
- Incorrect procurement decisions (wrong quantities ordered)
- False alarms or missed alerts
- Inaccurate KPI reporting to management
- Reconciliation disputes with vendors

A systematic data quality framework catches these issues early — before they affect decisions.

## How to Run
```bash
pip install -r requirements.txt
python framework/run_checks.py         # Run checks on sample dataset
python framework/kpi_definitions.py    # View configured rules
```

## Framework Components
| File | Purpose |
|------|---------|
| `run_checks.py` | Main entry point — generates test data and runs all checks |
| `rules_config.py` | Define rules per dataset (no code changes needed) |
| `validators.py` (in supply-chain-etl-pipeline) | Reusable validator functions |
| `quality_reporter.py` | Formats and saves reports (CSV + JSON) |

## Check Categories

### Completeness
Are all required fields populated? Catches missing site IDs, empty quantities etc.

### Validity
Are values in acceptable ranges? Catches negative quantities, future dates, zero denominators.

### Uniqueness
Are primary keys truly unique? Catches duplicate waybill numbers, alarm IDs.

### Consistency
Do related fields agree? Catches impossible combinations (e.g. delivered > 3× ordered).

### Referential Integrity
Do foreign keys exist in reference tables? Catches unknown vendor names, invalid site IDs.

## Adding New Rules
Edit `framework/rules_config.py`:
```python
DELIVERY_RULES = [
    ("no_nulls",      "site_id"),          # Required: no missing site IDs
    ("positive",      "qty_ordered"),       # Must be > 0
    ("not_future",    "delivery_date"),     # Can't be in the future
    ("value_range",   "qty_ordered", 100, 50000),  # Reasonable range
    ("allowed_values","vendor", ["Vendor A", "Vendor B"]),  # Only known vendors
]
```
No changes to core framework code required.

## Output Formats
- **Console** — colour-coded summary with PASS/WARN/FAIL status
- **CSV** — full check results for Excel review
- **JSON** — structured output for integration with monitoring dashboards
