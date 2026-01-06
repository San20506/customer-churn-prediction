
import pandas as pd
file = r'd:\Skipper\Customer_churn_out_prediction_model\retailer_risk_analysis.xlsx'
try:
    df = pd.read_excel(file, sheet_name='State Classification')
    print(f"Segments found: {df.columns.tolist()}")
    
    print("\nSample counts:")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
