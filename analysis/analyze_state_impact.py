"""
State-Adjusted Churn Analysis
==============================
Calculates churn with state-level grouping effects and compares to flat threshold.

Hypothesis: Different states have different buying patterns, so a flat 183-day 
threshold may not accurately capture churn for all regions.

Approach:
1. Calculate average purchase gap per state
2. Define state-specific churn threshold as: avg_gap * 3 (3x normal gap = churn)
3. Compare results with flat 183-day threshold
"""

import pandas as pd
import numpy as np

print("="*80)
print("STATE-ADJUSTED CHURN ANALYSIS")
print("="*80)

# Load data
print("\n1. Loading data...")
df = pd.read_excel('Plumber banking data Apr 24- Dec 25.xlsx', sheet_name='XYZ')
df['TRXN_DATE'] = pd.to_datetime(df['TRXN_DATE'])
analysis_date = df['TRXN_DATE'].max()
print(f"   Transactions: {len(df):,}")
print(f"   Analysis Date: {analysis_date.strftime('%Y-%m-%d')}")

# Calculate customer-level metrics
print("\n2. Building customer profiles...")
customer_data = df.groupby('MEMBERSHIP ID').agg({
    'TRXN_DATE': ['min', 'max', 'count'],
    'STATE': 'first',
    'POINT_AWARDED': 'sum'
}).reset_index()

customer_data.columns = ['customer_id', 'first_purchase', 'last_purchase', 'frequency', 'state', 'points']
customer_data['recency'] = (analysis_date - customer_data['last_purchase']).dt.days
customer_data['lifetime'] = (customer_data['last_purchase'] - customer_data['first_purchase']).dt.days

# Calculate average purchase gap per customer
customer_data['avg_gap'] = customer_data.apply(
    lambda r: r['lifetime'] / (r['frequency'] - 1) if r['frequency'] > 1 else 60,
    axis=1
)

total_customers = len(customer_data)
print(f"   Unique Customers: {total_customers:,}")

# ============================================================================
# METHOD 1: FLAT THRESHOLD (183 days for everyone)
# ============================================================================
print("\n" + "="*80)
print("METHOD 1: FLAT THRESHOLD (183 days)")
print("="*80)

FLAT_THRESHOLD = 183
customer_data['churned_flat'] = customer_data['recency'] >= FLAT_THRESHOLD

flat_churned = customer_data['churned_flat'].sum()
flat_churn_rate = flat_churned / total_customers * 100

print(f"\n   Threshold: {FLAT_THRESHOLD} days for ALL customers")
print(f"   Churned: {flat_churned:,} ({flat_churn_rate:.1f}%)")
print(f"   Active: {total_customers - flat_churned:,} ({100-flat_churn_rate:.1f}%)")

# Breakdown by state (flat method)
flat_by_state = customer_data.groupby('state').agg({
    'customer_id': 'count',
    'churned_flat': ['sum', 'mean']
}).reset_index()
flat_by_state.columns = ['state', 'customers', 'churned', 'churn_rate']
flat_by_state['churn_rate_pct'] = flat_by_state['churn_rate'] * 100

# ============================================================================
# METHOD 2: STATE-ADJUSTED THRESHOLD
# ============================================================================
print("\n" + "="*80)
print("METHOD 2: STATE-ADJUSTED THRESHOLD")
print("="*80)

# Calculate state-level purchase patterns
state_patterns = customer_data.groupby('state').agg({
    'avg_gap': 'median',
    'frequency': 'median',
    'customer_id': 'count'
}).reset_index()
state_patterns.columns = ['state', 'median_gap', 'median_freq', 'customers']

# State-specific threshold: 3x median gap, with min 90 and max 365
state_patterns['adjusted_threshold'] = state_patterns['median_gap'].apply(
    lambda x: min(max(x * 3, 90), 365)
)

print("\nState-Specific Thresholds:")
print(f"{'State':<20} {'Med Gap':>10} {'Threshold':>12} {'Customers':>10}")
print("-"*55)
for _, row in state_patterns.sort_values('customers', ascending=False).iterrows():
    print(f"{row['state']:<20} {row['median_gap']:>10.0f} {row['adjusted_threshold']:>11.0f}d {row['customers']:>10,}")

# Apply state-specific threshold
threshold_map = state_patterns.set_index('state')['adjusted_threshold'].to_dict()
customer_data['state_threshold'] = customer_data['state'].map(threshold_map)
customer_data['churned_adjusted'] = customer_data['recency'] >= customer_data['state_threshold']

adjusted_churned = customer_data['churned_adjusted'].sum()
adjusted_churn_rate = adjusted_churned / total_customers * 100

print(f"\n   Using State-Specific Thresholds")
print(f"   Churned: {adjusted_churned:,} ({adjusted_churn_rate:.1f}%)")
print(f"   Active: {total_customers - adjusted_churned:,} ({100-adjusted_churn_rate:.1f}%)")

# Breakdown by state (adjusted method)
adjusted_by_state = customer_data.groupby('state').agg({
    'customer_id': 'count',
    'churned_adjusted': ['sum', 'mean'],
    'state_threshold': 'first'
}).reset_index()
adjusted_by_state.columns = ['state', 'customers', 'churned', 'churn_rate', 'threshold']
adjusted_by_state['churn_rate_pct'] = adjusted_by_state['churn_rate'] * 100

# ============================================================================
# COMPARISON
# ============================================================================
print("\n" + "="*80)
print("COMPARISON: FLAT vs STATE-ADJUSTED")
print("="*80)

# Merge for comparison
comparison = flat_by_state[['state', 'customers', 'churn_rate_pct']].merge(
    adjusted_by_state[['state', 'churn_rate_pct', 'threshold']],
    on='state',
    suffixes=('_flat', '_adjusted')
)
comparison['difference'] = comparison['churn_rate_pct_adjusted'] - comparison['churn_rate_pct_flat']
comparison = comparison.sort_values('difference')

print(f"\n{'State':<20} {'Customers':>10} {'Flat %':>10} {'Adj %':>10} {'Diff':>10} {'Threshold':>10}")
print("-"*75)
for _, row in comparison.iterrows():
    diff_indicator = "↓" if row['difference'] < 0 else ("↑" if row['difference'] > 0 else "=")
    print(f"{row['state']:<20} {row['customers']:>10,} {row['churn_rate_pct_flat']:>9.1f}% {row['churn_rate_pct_adjusted']:>9.1f}% {row['difference']:>+9.1f}% {row['threshold']:>9.0f}d")

# Overall summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"""
┌─────────────────────────────────────────────────────────────────┐
│                     CHURN CALCULATION COMPARISON                 │
├────────────────────────┬────────────────────────────────────────┤
│ Method                 │ Flat 183-day     │ State-Adjusted      │
├────────────────────────┼──────────────────┼─────────────────────┤
│ Total Customers        │ {total_customers:>16,} │ {total_customers:>18,} │
│ Churned Customers      │ {flat_churned:>16,} │ {adjusted_churned:>18,} │
│ Churn Rate             │ {flat_churn_rate:>15.1f}% │ {adjusted_churn_rate:>17.1f}% │
│ Active Customers       │ {total_customers - flat_churned:>16,} │ {total_customers - adjusted_churned:>18,} │
├────────────────────────┴──────────────────┴─────────────────────┤
│                                                                  │
│  DIFFERENCE: {adjusted_churned - flat_churned:+,} customers ({adjusted_churn_rate - flat_churn_rate:+.1f}%)             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
""")

# Identify reclassified customers
reclassified = customer_data[customer_data['churned_flat'] != customer_data['churned_adjusted']]
now_active = reclassified[reclassified['churned_adjusted'] == False]
now_churned = reclassified[reclassified['churned_adjusted'] == True]

print(f"RECLASSIFIED CUSTOMERS:")
print(f"  → Now ACTIVE (was churned in flat):  {len(now_active):,}")
print(f"  → Now CHURNED (was active in flat):  {len(now_churned):,}")

print("\nBy State:")
reclass_by_state = reclassified.groupby('state').agg({
    'customer_id': 'count',
    'churned_adjusted': 'mean'
}).reset_index()
reclass_by_state.columns = ['state', 'reclassified', 'now_churned_pct']
reclass_by_state = reclass_by_state.sort_values('reclassified', ascending=False)

for _, row in reclass_by_state.iterrows():
    direction = "→ Churned" if row['now_churned_pct'] > 0.5 else "→ Active"
    print(f"  {row['state']}: {row['reclassified']:,} customers {direction}")

# Save detailed results
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

with pd.ExcelWriter('state_adjusted_churn_analysis.xlsx', engine='openpyxl') as writer:
    # Comparison summary
    comparison.to_excel(writer, sheet_name='State_Comparison', index=False)
    
    # Reclassified customers
    reclassified[['customer_id', 'state', 'recency', 'frequency', 'state_threshold', 
                  'churned_flat', 'churned_adjusted']].to_excel(
        writer, sheet_name='Reclassified_Customers', index=False
    )
    
    # State patterns
    state_patterns.to_excel(writer, sheet_name='State_Patterns', index=False)
    
    # Full customer data
    customer_data.to_excel(writer, sheet_name='All_Customers', index=False)
    
    # Auto-adjust column widths
    for sheet in writer.sheets:
        ws = writer.sheets[sheet]
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 12), 30)

print("✅ Saved: state_adjusted_churn_analysis.xlsx")
print("\nSheets:")
print("  - State_Comparison: Side-by-side comparison")
print("  - Reclassified_Customers: Changed status customers")
print("  - State_Patterns: State-level buying patterns")
print("  - All_Customers: Full dataset with both methods")

# Recommendation
print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)

diff_pct = abs(adjusted_churn_rate - flat_churn_rate)
if diff_pct > 5:
    print(f"""
⚠️  SIGNIFICANT DIFFERENCE ({diff_pct:.1f}%)

The state-adjusted method shows a {'HIGHER' if adjusted_churn_rate > flat_churn_rate else 'LOWER'} churn rate.

RECOMMENDATION: Consider using state-adjusted thresholds because:
1. Different regions have different buying patterns
2. A customer in a low-activity state shouldn't be judged by high-activity standards
3. The {len(reclassified):,} reclassified customers may need different interventions
""")
else:
    print(f"""
✅ MINIMAL DIFFERENCE ({diff_pct:.1f}%)

The flat 183-day threshold is working well for your data.
State patterns don't significantly impact the churn calculation.

RECOMMENDATION: Continue using the flat 183-day threshold for simplicity.
""")
