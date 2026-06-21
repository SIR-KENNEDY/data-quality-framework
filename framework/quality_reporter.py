"""
quality_reporter.py
===================
Formats and outputs the data quality report in multiple formats:
  - Console (coloured text summary)
  - CSV report file
  - JSON report file (for integration with monitoring systems)

Usage: from framework.quality_reporter import QualityReporter
"""
import pandas as pd
import json
import os
from datetime import datetime

class QualityReporter:
    def __init__(self, dataset_name: str, results_df: pd.DataFrame):
        self.name    = dataset_name
        self.results = results_df
        self.run_at  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def summary(self) -> dict:
        total   = len(self.results)
        passed  = (self.results["status"] == "PASS").sum()
        warned  = (self.results["status"] == "WARN").sum()
        failed  = (self.results["status"] == "FAIL").sum()
        score   = round(passed / total * 100, 1) if total > 0 else 0
        return {"dataset":self.name,"run_at":self.run_at,
                "total_checks":total,"passed":int(passed),
                "warnings":int(warned),"failures":int(failed),"quality_score":score}

    def print_report(self):
        s = self.summary()
        print(f"
{'='*60}")
        print(f"  DATA QUALITY REPORT — {s['dataset'].upper()}")
        print(f"  Run: {s['run_at']}")
        print(f"{'='*60}")
        print(f"  Quality Score: {s['quality_score']}%  |  "
              f"✅ {s['passed']} passed  |  ⚠️  {s['warnings']} warned  |  ❌ {s['failures']} failed")
        print()
        for _, row in self.results.iterrows():
            if row["status"] != "PASS":
                icon = {"WARN":"⚠️ ","FAIL":"❌"}[row["status"]]
                pct  = round(row["failures"]/row.get("total",1)*100,1) if row.get("total",0)>0 else 0
                print(f"  {icon} {row['check']}: {row['failures']} failures ({pct}%)")
        if s["failures"] == 0 and s["warnings"] == 0:
            print("  ✅ All checks passed — dataset is clean.")

    def save_csv(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        path = f"{output_dir}/quality_report_{self.name}.csv"
        self.results.to_csv(path, index=False)
        return path

    def save_json(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        path = f"{output_dir}/quality_report_{self.name}.json"
        report = self.summary()
        report["checks"] = self.results.to_dict("records")
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        return path
