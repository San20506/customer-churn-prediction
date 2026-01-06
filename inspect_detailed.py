
import pandas as pd
import os

result_file = r'd:\Skipper\Customer_churn_out_prediction_model\churn_analysis_results.xlsx'
data_file = r'd:\Skipper\Customer_churn_out_prediction_model\Plumber banking data Apr 24- Dec 25.xlsx'

try:
    print(f"--- {os.path.basename(result_file)} ---")
    df_res = pd.read_excel(result_file)
    print(f"Columns: {df_res.columns.tolist()}")
    if 'segment' in df_res.columns:
        print(f"Unique segments: {df_res['segment'].unique()}")
    if 'action_priority' in df_res.columns:
        print(f"Unique action_priority: {df_res['action_priority'].unique()}")
except Exception as e:
    print(f"Error reading result file: {e}")

try:
    print(f"\n--- {os.path.basename(data_file)} ---")
    df_data = pd.read_excel(data_file, nrows=100)
    print(f"Columns: {df_data.columns.tolist()}")
    # Check if 'MEMBERSHIP ID' matches 'customer_id' format
    if 'MEMBERSHIP ID' in df_data.columns:
        print(f"Sample IDs: {df_data['MEMBERSHIP ID'].head().tolist()}")
    # Check for State
    if 'STATE' in df_data.columns:
        print(f"Sample States: {df_data['STATE'].unique()[:5]}")
except Exception as e:
    print(f"Error reading data file: {e}")
