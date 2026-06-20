"""
run_checks.py — Configurable data quality framework for supply chain datasets.
Runs completeness, validity, uniqueness, and consistency checks.
"""
import pandas as pd, numpy as np, os
from datetime import datetime

np.random.seed(42)
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(BASE,"outputs"); os.makedirs(OUT,exist_ok=True)

# ── GENERATE TEST DATA (with intentional issues) ──────────────────
def make_test_data(n=300):
    df=pd.DataFrame({
        "waybill_no":[f"WB{i:06d}" for i in range(n)],
        "site_id":[f"SITE_{np.random.randint(1,51):03d}" for _ in range(n)],
        "vendor":np.random.choice(["FastFuel","NigerDiesel","SwiftHaul"],n),
        "delivery_date":pd.date_range("2023-01-01",periods=n,freq="12h"),
        "qty_ordered":np.random.randint(500,5000,n).astype(float),
        "qty_delivered":np.random.randint(400,5100,n).astype(float),
    })
    # Inject issues
    df.loc[0:4,"site_id"]=None           # missing values
    df.loc[5,"qty_delivered"]=-100        # negative qty
    df.loc[6,"qty_ordered"]=0             # zero ordered
    df.loc[7,"qty_delivered"]=df.loc[7,"qty_ordered"]*3  # delivery > 2x
    df.loc[8,"delivery_date"]=pd.Timestamp("2099-01-01")  # future date
    df=pd.concat([df,df.iloc[[10]]])       # duplicate row
    return df.reset_index(drop=True)

# ── QUALITY CHECKS ─────────────────────────────────────────────────
class DataQualityChecker:
    def __init__(self, df, dataset_name="dataset"):
        self.df=df; self.name=dataset_name
        self.results=[]; self.run_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _add(self, category, check, failures, total, detail=""):
        pct=round(failures/total*100,2) if total>0 else 0
        status="PASS" if failures==0 else ("WARN" if pct<5 else "FAIL")
        self.results.append({"category":category,"check":check,
            "failures":failures,"total":total,"failure_pct":pct,"status":status,"detail":detail})

    def check_completeness(self):
        for col in self.df.columns:
            n=self.df[col].isna().sum()
            self._add("Completeness",f"No nulls in [{col}]",n,len(self.df))

    def check_validity(self):
        if "qty_delivered" in self.df.columns:
            self._add("Validity","qty_delivered >= 0",(self.df["qty_delivered"]<0).sum(),len(self.df))
        if "qty_ordered" in self.df.columns:
            self._add("Validity","qty_ordered > 0",(self.df["qty_ordered"]<=0).sum(),len(self.df))
        if "delivery_date" in self.df.columns:
            self._add("Validity","delivery_date not in future",
                (self.df["delivery_date"]>pd.Timestamp("today")).sum(),len(self.df))

    def check_uniqueness(self):
        if "waybill_no" in self.df.columns:
            self._add("Uniqueness","No duplicate waybill_no",
                self.df["waybill_no"].duplicated().sum(),len(self.df))

    def check_consistency(self):
        if "qty_delivered" in self.df.columns and "qty_ordered" in self.df.columns:
            n=(self.df["qty_delivered"]>self.df["qty_ordered"]*2).sum()
            self._add("Consistency","qty_delivered <= 2x qty_ordered",n,len(self.df))

    def run_all(self):
        self.check_completeness(); self.check_validity()
        self.check_uniqueness(); self.check_consistency()
        return self

    def report(self):
        rdf=pd.DataFrame(self.results)
        total=len(rdf); passed=(rdf["status"]=="PASS").sum()
        warns=(rdf["status"]=="WARN").sum(); fails=(rdf["status"]=="FAIL").sum()
        print(f"\n{'='*60}")
        print(f"  DATA QUALITY REPORT — {self.name}")
        print(f"  Run time: {self.run_time}")
        print(f"{'='*60}")
        print(f"  Total checks: {total} | ✅ PASS: {passed} | ⚠️  WARN: {warns} | ❌ FAIL: {fails}")
        print(f"  Overall score: {passed/total*100:.1f}%\n")
        for _,row in rdf.iterrows():
            icon={"PASS":"✅","WARN":"⚠️ ","FAIL":"❌"}[row["status"]]
            if row["status"]!="PASS":
                print(f"  {icon} [{row['category']}] {row['check']}: {row['failures']} failures ({row['failure_pct']}%)")
        rdf.to_csv(f"{OUT}/quality_report.csv",index=False)
        print(f"\n  Full report: {OUT}/quality_report.csv")
        return rdf

if __name__=="__main__":
    df=make_test_data()
    print(f"Loaded test dataset: {len(df)} rows x {df.shape[1]} cols")
    checker=DataQualityChecker(df,"supply_chain_deliveries")
    checker.run_all().report()
