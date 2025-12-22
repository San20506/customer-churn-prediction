import pandas as pd

cust = pd.read_excel('multi_factor_churn_analysis.xlsx', sheet_name='All_Customers')
total = len(cust)

print("="*60)
print("MULTI-FACTOR CHURN COMPARISON")
print("="*60)
print(f"Total Customers: {total:,}")
print()

methods = [
    ('Flat 183-day', 'churned_flat'),
    ('State-Adjusted', 'churned_state'),
    ('Retailer-Adjusted', 'churned_retailer'),
    ('Combined', 'churned_combined')
]

print(f"{'Method':<25} {'Churned':>10} {'Rate':>10}")
print("-"*45)
for name, col in methods:
    churned = cust[col].sum()
    rate = churned / total * 100
    print(f"{name:<25} {churned:>10,} {rate:>9.1f}%")

print()
print("="*60)
print("BY STATE:")
print("="*60)
state_df = pd.read_excel('multi_factor_churn_analysis.xlsx', sheet_name='State_Breakdown')
for _, r in state_df.iterrows():
    state = r['state']
    customers = r['customers']
    flat = r['flat_rate'] * 100
    combined = r['combined_rate'] * 100
    thresh = r['threshold']
    print(f"{state}: {customers:,} cust, Flat={flat:.1f}%, Combined={combined:.1f}% (thresh={thresh:.0f}d)")
