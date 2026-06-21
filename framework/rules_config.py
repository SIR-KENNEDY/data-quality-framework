"""
rules_config.py
===============
Configuration file defining data quality rules for each dataset/column.
Modify this file to add new rules without changing the core framework code.
"""

# Rule format:
# (check_type, column, *args)
# check_types: "no_nulls", "positive", "no_negatives", "no_duplicates",
#              "not_future", "value_range", "allowed_values"

DELIVERY_RULES = [
    ("no_nulls",      "site_id",        ),
    ("no_nulls",      "vendor",         ),
    ("no_nulls",      "qty_ordered",    ),
    ("no_nulls",      "qty_delivered",  ),
    ("no_nulls",      "date",           ),
    ("no_duplicates", "waybill_no",     ),
    ("positive",      "qty_ordered",    ),
    ("no_negatives",  "qty_delivered",  ),
    ("not_future",    "date",           ),
    ("value_range",   "qty_ordered",    100, 50000),
    ("value_range",   "qty_delivered",  0,   60000),
    ("allowed_values","vendor",         ["FastFuel","NigerDiesel","SwiftHaul"]),
]

ALARM_RULES = [
    ("no_nulls",      "alarm_id",       ),
    ("no_nulls",      "site_id",        ),
    ("no_nulls",      "severity",       ),
    ("no_nulls",      "start_time",     ),
    ("no_duplicates", "alarm_id",       ),
    ("allowed_values","severity",       ["Critical","Major","Minor","Warning"]),
    ("no_negatives",  "duration_hrs",   ),
]

FUEL_READING_RULES = [
    ("no_nulls",      "site_id",             ),
    ("no_nulls",      "date",                ),
    ("no_nulls",      "daily_consumption_litres"),
    ("positive",      "daily_consumption_litres"),
    ("not_future",    "date",                ),
    ("value_range",   "daily_consumption_litres", 10, 2000),
    ("value_range",   "grid_reliability_score",   0.0, 1.0),
]

DATASET_RULES = {
    "deliveries":  DELIVERY_RULES,
    "alarms":      ALARM_RULES,
    "fuel_readings": FUEL_READING_RULES,
}
