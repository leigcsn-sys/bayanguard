import json
import pandas as pd
from pathlib import Path
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

REFERENCE_PATH = "data/featured_transactions.csv"
DRIFT_REPORT_PATH = "data/drift_report.json"

def run_drift_check(current_df: pd.DataFrame, feature_cols: list) -> dict:
    print("Running drift detection...")
    
    reference_df = pd.read_csv(REFERENCE_PATH, nrows=10000)
    numeric_cols = [c for c in feature_cols if reference_df[c].dtype in ["float64", "int64"]]
    
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_df[numeric_cols], current_data=current_df[numeric_cols])
    
    json_report = report.as_dict()
    drift_score = json_report["metrics"][0]["result"]["dataset_drift"]
    
    result = {
        "drift_detected": drift_score,
        "timestamp": pd.Timestamp.now().isoformat(),
        "n_features_drifted": json_report["metrics"][0]["result"].get("number_of_drifted_columns", 0),
    }
    
    with open(DRIFT_REPORT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Drift detected: {drift_score}")
    return result

if __name__ == "__main__":
    df = pd.read_csv(REFERENCE_PATH, nrows=5000)
    import json
    with open("data/feature_columns.json") as f:
        cols = json.load(f)
    run_drift_check(df, cols)