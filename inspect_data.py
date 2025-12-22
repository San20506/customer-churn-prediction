
import pandas as pd
import os

files = [
    r'd:\Skipper\Customer_churn_out_prediction_model\Book6.xlsx',
    r'd:\Skipper\Customer_churn_out_prediction_model\Plumber banking data Apr 24- Dec 25.xlsx'
]

for file in files:
    try:
        print(f"--- {os.path.basename(file)} ---")
        # Load just the first few rows to get headers
        df = pd.read_excel(file, nrows=5)
        print("Columns:")
        for col in df.columns:
            print(f"  - {col}")
        print("\n")
    except Exception as e:
        print(f"Error reading {file}: {e}\n")
