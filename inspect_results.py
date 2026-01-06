
import pandas as pd
import os

files = [
    r'd:\Skipper\Customer_churn_out_prediction_model\churn_analysis_results.xlsx',
]

for file in files:
    try:
        print(f"--- {os.path.basename(file)} ---")
        df = pd.read_excel(file, nrows=5)
        print("Columns:")
        for col in df.columns:
            print(f"  - {col}")
        print("\nSample values for risk columns if any:")
        # Look for columns that might contain 'Risk'
        risk_cols = [c for c in df.columns if 'Risk' in str(c) or 'risk' in str(c) or 'Category' in str(c)]
        for col in risk_cols:
             print(f" {col}: {df[col].unique()}")
    except Exception as e:
        print(f"Error reading {file}: {e}\n")
