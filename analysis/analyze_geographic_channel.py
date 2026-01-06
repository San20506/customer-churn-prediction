"""
Geographic & Channel Churn Analysis
====================================
Analyzes the impact of State, Retailer, and Distributor on customer churn.
"""

import pandas as pd
import numpy as np
from scipy import stats

print("="*80)
print("GEOGRAPHIC & CHANNEL CHURN ANALYSIS")
print("Testing: Do State, Retailer, Distributor impact churn?")
print("="*80)

# Load data
print("\nLoading data...")
df = pd.read_excel('Plumber banking data Apr 24- Dec 25.xlsx', sheet_name='XYZ')
df['TRXN_DATE'] = pd.to_datetime(df['TRXN_DATE'])

# Calculate customer-level metrics
analysis_date = df['TRXN_DATE'].max()
print(f"Analysis Date: {analysis_date.strftime('%Y-%m-%d')}")

customer_data = df.groupby('MEMBERSHIP ID').agg({
    'TRXN_DATE': 'max',
    'STATE': 'first',
    'RETAILER CODE': 'first',
    'DISTRIBUTOR CODE': 'first',
    'INVOICE_NO': 'count',
    'POINT_AWARDED': 'sum'
}).reset_index()

customer_data.columns = ['customer_id', 'last_purchase', 'state', 'retailer', 'distributor', 'frequency', 'points']
customer_data['recency'] = (analysis_date - customer_data['last_purchase']).dt.days
customer_data['is_churned'] = customer_data['recency'] >= 183

total_customers = len(customer_data)
overall_churn = customer_data['is_churned'].mean() * 100

print(f"Total Customers: {total_customers:,}")
print(f"Overall Churn Rate: {overall_churn:.1f}%")

# ============================================================================
# 1. STATE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("1. CHURN RATE BY STATE")
print("="*80)

state_analysis = customer_data.groupby('state').agg({
    'customer_id': 'count',
    'is_churned': ['sum', 'mean'],
    'frequency': 'mean',
    'points': 'mean'
}).reset_index()
state_analysis.columns = ['state', 'customers', 'churned', 'churn_rate', 'avg_freq', 'avg_points']
state_analysis['churn_rate_pct'] = state_analysis['churn_rate'] * 100
state_analysis = state_analysis.sort_values('churn_rate_pct', ascending=False)

print(f"\n{'State':<20} {'Customers':>10} {'Churned':>10} {'Churn%':>10} {'Avg Freq':>10}")
print("-"*60)
for _, row in state_analysis.iterrows():
    indicator = "⚠️" if row['churn_rate_pct'] > overall_churn + 10 else ("✅" if row['churn_rate_pct'] < overall_churn - 10 else "")
    print(f"{row['state']:<20} {row['customers']:>10,} {row['churned']:>10,.0f} {row['churn_rate_pct']:>9.1f}% {row['avg_freq']:>10.1f} {indicator}")

# Statistical test
state_groups = [group['is_churned'].values for name, group in customer_data.groupby('state') if len(group) > 30]
if len(state_groups) >= 2:
    chi2, p_value = stats.chi2_contingency(pd.crosstab(customer_data['state'], customer_data['is_churned']))[:2]
    print(f"\nChi-Square Test: χ² = {chi2:.2f}, p-value = {p_value:.6f}")
    if p_value < 0.05:
        print("✅ SIGNIFICANT: State significantly impacts churn (p < 0.05)")
    else:
        print("❌ NOT SIGNIFICANT: State does not significantly impact churn")

# ============================================================================
# 2. RETAILER ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("2. CHURN RATE BY RETAILER (Min 20 customers)")
print("="*80)

retailer_analysis = customer_data.groupby('retailer').agg({
    'customer_id': 'count',
    'is_churned': ['sum', 'mean'],
    'frequency': 'mean',
    'points': 'mean'
}).reset_index()
retailer_analysis.columns = ['retailer', 'customers', 'churned', 'churn_rate', 'avg_freq', 'avg_points']
retailer_analysis['churn_rate_pct'] = retailer_analysis['churn_rate'] * 100
retailer_analysis = retailer_analysis[retailer_analysis['customers'] >= 20]
retailer_analysis = retailer_analysis.sort_values('churn_rate_pct', ascending=False)

print(f"\n{'Retailer':<20} {'Customers':>10} {'Churned':>10} {'Churn%':>10} {'Avg Freq':>10}")
print("-"*70)
for _, row in retailer_analysis.head(20).iterrows():
    indicator = "⚠️" if row['churn_rate_pct'] > overall_churn + 15 else ("✅" if row['churn_rate_pct'] < overall_churn - 15 else "")
    retailer_name = str(row['retailer'])[:18]
    print(f"{retailer_name:<20} {row['customers']:>10,} {row['churned']:>10,.0f} {row['churn_rate_pct']:>9.1f}% {row['avg_freq']:>10.1f} {indicator}")

# Variance analysis
retailer_variance = retailer_analysis['churn_rate_pct'].std()
print(f"\nChurn Rate Variance: {retailer_variance:.1f}%")
print(f"Range: {retailer_analysis['churn_rate_pct'].min():.1f}% - {retailer_analysis['churn_rate_pct'].max():.1f}%")

# High/Low performers
high_churn_retailers = retailer_analysis[retailer_analysis['churn_rate_pct'] > overall_churn + 15]
low_churn_retailers = retailer_analysis[retailer_analysis['churn_rate_pct'] < overall_churn - 15]
print(f"\n⚠️ High-churn retailers (>{overall_churn+15:.0f}%): {len(high_churn_retailers)}")
print(f"✅ Low-churn retailers (<{overall_churn-15:.0f}%): {len(low_churn_retailers)}")

# ============================================================================
# 3. DISTRIBUTOR ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("3. CHURN RATE BY DISTRIBUTOR (Min 20 customers)")
print("="*80)

dist_analysis = customer_data.groupby('distributor').agg({
    'customer_id': 'count',
    'is_churned': ['sum', 'mean'],
    'frequency': 'mean',
    'points': 'mean'
}).reset_index()
dist_analysis.columns = ['distributor', 'customers', 'churned', 'churn_rate', 'avg_freq', 'avg_points']
dist_analysis['churn_rate_pct'] = dist_analysis['churn_rate'] * 100
dist_analysis = dist_analysis[dist_analysis['customers'] >= 20]
dist_analysis = dist_analysis.sort_values('churn_rate_pct', ascending=False)

print(f"\n{'Distributor':<15} {'Customers':>10} {'Churned':>10} {'Churn%':>10} {'Avg Freq':>10}")
print("-"*60)
for _, row in dist_analysis.head(20).iterrows():
    indicator = "⚠️" if row['churn_rate_pct'] > overall_churn + 15 else ("✅" if row['churn_rate_pct'] < overall_churn - 15 else "")
    print(f"{row['distributor']:<15} {row['customers']:>10,} {row['churned']:>10,.0f} {row['churn_rate_pct']:>9.1f}% {row['avg_freq']:>10.1f} {indicator}")

# Variance analysis
dist_variance = dist_analysis['churn_rate_pct'].std()
print(f"\nChurn Rate Variance: {dist_variance:.1f}%")
print(f"Range: {dist_analysis['churn_rate_pct'].min():.1f}% - {dist_analysis['churn_rate_pct'].max():.1f}%")

# Statistical test
if len(dist_analysis) >= 2:
    chi2, p_value = stats.chi2_contingency(pd.crosstab(customer_data['distributor'], customer_data['is_churned']))[:2]
    print(f"\nChi-Square Test: χ² = {chi2:.2f}, p-value = {p_value:.6f}")
    if p_value < 0.05:
        print("✅ SIGNIFICANT: Distributor significantly impacts churn (p < 0.05)")
    else:
        print("❌ NOT SIGNIFICANT: Distributor does not significantly impact churn")

# ============================================================================
# 4. COMBINED IMPACT ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("4. COMBINED IMPACT: STATE x DISTRIBUTOR")
print("="*80)

combo_analysis = customer_data.groupby(['state', 'distributor']).agg({
    'customer_id': 'count',
    'is_churned': 'mean'
}).reset_index()
combo_analysis.columns = ['state', 'distributor', 'customers', 'churn_rate']
combo_analysis['churn_rate_pct'] = combo_analysis['churn_rate'] * 100
combo_analysis = combo_analysis[combo_analysis['customers'] >= 10]
combo_analysis = combo_analysis.sort_values('churn_rate_pct', ascending=False)

print("\nHIGHEST CHURN COMBINATIONS:")
print(f"{'State':<15} {'Distributor':>12} {'Customers':>10} {'Churn%':>10}")
print("-"*50)
for _, row in combo_analysis.head(10).iterrows():
    print(f"{row['state']:<15} {row['distributor']:>12} {row['customers']:>10,} {row['churn_rate_pct']:>9.1f}%")

print("\nLOWEST CHURN COMBINATIONS:")
for _, row in combo_analysis.tail(10).iterrows():
    print(f"{row['state']:<15} {row['distributor']:>12} {row['customers']:>10,} {row['churn_rate_pct']:>9.1f}%")

# ============================================================================
# 5. HYPOTHESIS CONCLUSION
# ============================================================================
print("\n" + "="*80)
print("HYPOTHESIS TEST RESULTS")
print("="*80)

# Calculate effect sizes
state_effect = state_analysis['churn_rate_pct'].max() - state_analysis['churn_rate_pct'].min()
retailer_effect = retailer_analysis['churn_rate_pct'].max() - retailer_analysis['churn_rate_pct'].min()
dist_effect = dist_analysis['churn_rate_pct'].max() - dist_analysis['churn_rate_pct'].min()

print(f"""
HYPOTHESIS: State, Retailer, and Distributor impact churn

FINDINGS:

1. STATE IMPACT:
   - Churn rate range: {state_analysis['churn_rate_pct'].min():.1f}% - {state_analysis['churn_rate_pct'].max():.1f}%
   - Effect size: {state_effect:.1f} percentage points
   - Verdict: {'✅ CONFIRMED' if state_effect > 10 else '❌ MINIMAL'}

2. RETAILER IMPACT:
   - Churn rate range: {retailer_analysis['churn_rate_pct'].min():.1f}% - {retailer_analysis['churn_rate_pct'].max():.1f}%
   - Effect size: {retailer_effect:.1f} percentage points
   - High-churn retailers: {len(high_churn_retailers)}
   - Verdict: {'✅ CONFIRMED' if retailer_effect > 20 else '❌ MINIMAL'}

3. DISTRIBUTOR IMPACT:
   - Churn rate range: {dist_analysis['churn_rate_pct'].min():.1f}% - {dist_analysis['churn_rate_pct'].max():.1f}%
   - Effect size: {dist_effect:.1f} percentage points
   - Verdict: {'✅ CONFIRMED' if dist_effect > 15 else '❌ MINIMAL'}

OVERALL CONCLUSION:
""")

significant_factors = []
if state_effect > 10:
    significant_factors.append("State")
if retailer_effect > 20:
    significant_factors.append("Retailer")
if dist_effect > 15:
    significant_factors.append("Distributor")

if significant_factors:
    print(f"✅ HYPOTHESIS CONFIRMED: {', '.join(significant_factors)} significantly impact churn.")
    print("\nRECOMMENDATIONS:")
    if "State" in significant_factors:
        print("   - Investigate high-churn states for regional issues")
    if "Retailer" in significant_factors:
        print("   - Review high-churn retailers for service quality issues")
        print("   - Share best practices from low-churn retailers")
    if "Distributor" in significant_factors:
        print("   - Audit high-churn distributors for supply/service problems")
else:
    print("❌ HYPOTHESIS NOT CONFIRMED: These factors have minimal impact on churn.")
    print("   Focus on customer-level factors (recency, frequency) instead.")

# Save results
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Export detailed analysis
with pd.ExcelWriter('geographic_channel_analysis.xlsx', engine='openpyxl') as writer:
    state_analysis.to_excel(writer, sheet_name='State_Analysis', index=False)
    retailer_analysis.to_excel(writer, sheet_name='Retailer_Analysis', index=False)
    dist_analysis.to_excel(writer, sheet_name='Distributor_Analysis', index=False)
    combo_analysis.to_excel(writer, sheet_name='State_Distributor_Combo', index=False)
    
    # Auto-adjust column widths
    for sheet in writer.sheets:
        ws = writer.sheets[sheet]
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 12), 30)

print("✅ Saved to: geographic_channel_analysis.xlsx")
print("\nSheets included:")
print("   - State_Analysis")
print("   - Retailer_Analysis")
print("   - Distributor_Analysis")
print("   - State_Distributor_Combo")
