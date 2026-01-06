"""
STATE FACTOR HYPOTHESIS TEST
=============================
Hypothesis: State significantly affects customer churn rates

We will prove this through:
1. Descriptive Statistics - Show differences in churn rates
2. Chi-Square Test - Statistical significance test
3. Effect Size - How big is the impact
4. Buying Pattern Analysis - Why states differ
"""

import pandas as pd
import numpy as np
from scipy import stats

print("="*80)
print("HYPOTHESIS TEST: STATE AFFECTS CHURN")
print("="*80)

# Load data
print("\n1. LOADING DATA...")
df = pd.read_excel('Plumber banking data Apr 24- Dec 25.xlsx', sheet_name='XYZ')
df['TRXN_DATE'] = pd.to_datetime(df['TRXN_DATE'])
analysis_date = df['TRXN_DATE'].max()

# Build customer data
customer_data = df.groupby('MEMBERSHIP ID').agg({
    'TRXN_DATE': ['min', 'max', 'count'],
    'STATE': 'first',
    'POINT_AWARDED': 'sum'
}).reset_index()
customer_data.columns = ['customer_id', 'first_purchase', 'last_purchase', 'frequency', 'state', 'points']
customer_data['recency'] = (analysis_date - customer_data['last_purchase']).dt.days
customer_data['lifetime'] = (customer_data['last_purchase'] - customer_data['first_purchase']).dt.days
customer_data['avg_gap'] = customer_data.apply(
    lambda r: r['lifetime'] / (r['frequency'] - 1) if r['frequency'] > 1 else 60, axis=1
)
customer_data['is_churned'] = customer_data['recency'] >= 183

total_customers = len(customer_data)
overall_churn_rate = customer_data['is_churned'].mean()

print(f"   Total Customers: {total_customers:,}")
print(f"   Overall Churn Rate: {overall_churn_rate*100:.2f}%")

# ============================================================================
# 2. DESCRIPTIVE STATISTICS - Show State Differences
# ============================================================================
print("\n" + "="*80)
print("2. STATE-LEVEL CHURN RATES")
print("="*80)

state_stats = customer_data.groupby('state').agg({
    'customer_id': 'count',
    'is_churned': ['sum', 'mean'],
    'avg_gap': 'median',
    'frequency': 'median',
    'recency': 'median'
}).reset_index()
state_stats.columns = ['state', 'customers', 'churned', 'churn_rate', 'median_gap', 'median_freq', 'median_recency']
state_stats['churn_pct'] = state_stats['churn_rate'] * 100
state_stats = state_stats.sort_values('customers', ascending=False)

print(f"\n{'State':<20} {'Customers':>10} {'Churned':>10} {'Churn%':>10} {'Med Gap':>10} {'Med Freq':>10}")
print("-"*75)
for _, row in state_stats.iterrows():
    # Mark if significantly different from average
    diff = row['churn_pct'] - overall_churn_rate*100
    indicator = "⚠️ HIGH" if diff > 10 else ("✅ LOW" if diff < -10 else "")
    print(f"{row['state']:<20} {row['customers']:>10,} {row['churned']:>10,.0f} {row['churn_pct']:>9.2f}% {row['median_gap']:>9.1f}d {row['median_freq']:>10.1f} {indicator}")

# ============================================================================
# 3. CHI-SQUARE TEST - Statistical Significance
# ============================================================================
print("\n" + "="*80)
print("3. STATISTICAL SIGNIFICANCE TEST (Chi-Square)")
print("="*80)

# Create contingency table
contingency = pd.crosstab(customer_data['state'], customer_data['is_churned'])
print("\nContingency Table (State × Churn Status):")
contingency.columns = ['Active', 'Churned']
print(contingency)

# Chi-square test
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

print(f"\nChi-Square Statistic: χ² = {chi2:.4f}")
print(f"Degrees of Freedom: {dof}")
print(f"P-Value: {p_value:.10f}")

if p_value < 0.001:
    print("\n✅ RESULT: HIGHLY SIGNIFICANT (p < 0.001)")
    print("   State has a STATISTICALLY SIGNIFICANT effect on churn.")
    print("   The probability this difference is due to chance is < 0.1%")
elif p_value < 0.05:
    print("\n✅ RESULT: SIGNIFICANT (p < 0.05)")
    print("   State has a statistically significant effect on churn.")
else:
    print("\n❌ RESULT: NOT SIGNIFICANT (p >= 0.05)")
    print("   State does NOT have a statistically significant effect on churn.")

# ============================================================================
# 4. EFFECT SIZE - How Big is the Impact?
# ============================================================================
print("\n" + "="*80)
print("4. EFFECT SIZE (Cramér's V)")
print("="*80)

n = contingency.sum().sum()
min_dim = min(contingency.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))

print(f"\nCramér's V = {cramers_v:.4f}")

if cramers_v < 0.1:
    effect_label = "NEGLIGIBLE"
elif cramers_v < 0.3:
    effect_label = "SMALL"
elif cramers_v < 0.5:
    effect_label = "MEDIUM"
else:
    effect_label = "LARGE"

print(f"Effect Size: {effect_label}")
print("""
Effect Size Interpretation:
  < 0.1  = Negligible (no practical impact)
  0.1-0.3 = Small (some impact)
  0.3-0.5 = Medium (moderate impact)
  > 0.5  = Large (strong impact)
""")

# ============================================================================
# 5. BUYING PATTERN DIFFERENCES - Why States Differ
# ============================================================================
print("\n" + "="*80)
print("5. WHY STATES DIFFER - Buying Pattern Analysis")
print("="*80)

print("\nKey Metrics by State:")
print(f"\n{'State':<20} {'Med Gap':>12} {'Med Freq':>12} {'Med Recency':>15} {'Implied Threshold':>18}")
print("-"*80)

for _, row in state_stats.iterrows():
    implied_thresh = int(min(max(row['median_gap'] * 3, 90), 365))
    print(f"{row['state']:<20} {row['median_gap']:>11.1f}d {row['median_freq']:>12.1f} {row['median_recency']:>14.1f}d {implied_thresh:>17}d")

# Compare extremes
if len(state_stats) >= 2:
    high_churn_states = state_stats[state_stats['churn_pct'] > overall_churn_rate*100 + 5]
    low_churn_states = state_stats[state_stats['churn_pct'] < overall_churn_rate*100 - 5]
    
    print("\n" + "="*80)
    print("6. KEY FINDING: State Pattern Comparison")
    print("="*80)
    
    # Compare West Bengal (largest) to average
    wb = state_stats[state_stats['state'] == 'West Bengal'].iloc[0]
    
    print(f"""
WEST BENGAL (Main Market - {wb['customers']:,} customers):
  - Churn Rate: {wb['churn_pct']:.1f}% (Overall: {overall_churn_rate*100:.1f}%)
  - Median Purchase Gap: {wb['median_gap']:.1f} days
  - Median Frequency: {wb['median_freq']:.1f} orders
  
  This means West Bengal customers buy every ~{wb['median_gap']:.0f} days on average.
  If we use 183-day threshold, we're waiting {183/wb['median_gap']:.1f}x their normal gap!
  
  Suggested threshold for WB: {int(min(max(wb['median_gap']*3, 90), 365))} days
""")

# ============================================================================
# 7. CONCLUSION
# ============================================================================
print("\n" + "="*80)
print("7. CONCLUSION - HYPOTHESIS VERDICT")
print("="*80)

# Calculate the range of churn rates
churn_range = state_stats['churn_pct'].max() - state_stats['churn_pct'].min()

print(f"""
HYPOTHESIS: "State affects customer churn"

EVIDENCE:
1. Chi-Square Test: χ² = {chi2:.2f}, p-value = {p_value:.2e}
   → {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'} at α = 0.05

2. Effect Size: Cramér's V = {cramers_v:.3f}
   → {effect_label} effect

3. Churn Rate Range: {state_stats['churn_pct'].min():.1f}% to {state_stats['churn_pct'].max():.1f}%
   → {churn_range:.1f} percentage point spread

4. Buying Patterns Differ:
   - States have different median purchase gaps ({state_stats['median_gap'].min():.1f}d to {state_stats['median_gap'].max():.1f}d)
   - This explains why a flat 183-day threshold doesn't work equally well

VERDICT: {'✅ HYPOTHESIS CONFIRMED' if p_value < 0.05 and cramers_v >= 0.05 else '❌ HYPOTHESIS NOT CONFIRMED'}
""")

if p_value < 0.05:
    print("""
RECOMMENDATION:
Use state-adjusted thresholds for more accurate churn prediction.
Each state has unique buying patterns that should be considered.
""")

# Save detailed results
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

with pd.ExcelWriter('state_hypothesis_test_results.xlsx', engine='openpyxl') as writer:
    state_stats.to_excel(writer, sheet_name='State_Statistics', index=False)
    contingency.to_excel(writer, sheet_name='Contingency_Table')
    
    # Test results summary
    test_results = pd.DataFrame({
        'Metric': ['Chi-Square', 'P-Value', 'Degrees of Freedom', 'Cramers V', 'Effect Size', 
                   'Overall Churn Rate', 'Churn Rate Range', 'Verdict'],
        'Value': [chi2, p_value, dof, cramers_v, effect_label,
                  f"{overall_churn_rate*100:.2f}%", f"{churn_range:.1f}%", 
                  'CONFIRMED' if p_value < 0.05 else 'NOT CONFIRMED']
    })
    test_results.to_excel(writer, sheet_name='Test_Results', index=False)

print("✅ Saved: state_hypothesis_test_results.xlsx")
