
import pandas as pd

file = r'd:\Skipper\Customer_churn_out_prediction_model\Plumber banking data Apr 24- Dec 25.xlsx'
try:
    df = pd.read_excel(file)
    if 'STATE' in df.columns:
        print("Unique States:")
        states = df['STATE'].unique()
        for s in states:
            print(f"'{s}'")
    else:
        print("STATE column not found")
except Exception as e:
    print(f"Error: {e}")
