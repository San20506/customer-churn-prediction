
import pandas as pd
file = r'd:\Skipper\Customer_churn_out_prediction_model\retailer_risk_analysis.xlsx'
try:
    xl = pd.ExcelFile(file)
    print(f"Sheets: {xl.sheet_names}")
    for sheet in xl.sheet_names:
        df = pd.read_excel(file, sheet_name=sheet)
        print(f"\n--- {sheet} ---")
        print(f"Shape: {df.shape}")
        if not df.empty:
            print(df.head())
        else:
            print("Empty dataframe")
except Exception as e:
    print(f"Error: {e}")
