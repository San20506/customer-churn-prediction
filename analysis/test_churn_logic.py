"""
Test Fixed Churn Logic
=======================
Verify that churned customers are properly categorized.
"""

import pandas as pd
from multi_level_churn import MultiLevelChurnSystem

print("="*80)
print("TESTING FIXED CHURN LOGIC")
print("="*80)

# Load data
print("\n1. Loading data...")
df = pd.read_excel('Plumber banking data Apr 24- Dec 25.xlsx', sheet_name='XYZ')
print(f"   ✓ Loaded {len(df):,} transactions")

# Run analysis
print("\n2. Running analysis...")
system = MultiLevelChurnSystem(churn_threshold=183)
results = system.run(df)

rfm_df = results['rfm']

print("\n3. SEGMENT BREAKDOWN:")
print("="*80)

segment_counts = rfm_df['segment'].value_counts().sort_index()
for segment, count in segment_counts.items():
    pct = count / len(rfm_df) * 100
    print(f"   {segment:<30} {count:>5,} ({pct:>5.1f}%)")

print("\n4. CHURN VERIFICATION:")
print("="*80)

# Count by churn status
total_customers = len(rfm_df)
active_customers = len(rfm_df[rfm_df['is_churned'] == False])
churned_customers = len(rfm_df[rfm_df['is_churned'] == True])

print(f"   Total Customers:        {total_customers:>6,}")
print(f"   Active (< 183 days):    {active_customers:>6,}")
print(f"   Churned (183+ days):    {churned_customers:>6,}")
print(f"   Sum check:              {active_customers + churned_customers:>6,} ✓")

# Breakdown of churned
recently_churned = len(rfm_df[rfm_df['segment'] == 'CHURNED_OUT_RECENTLY'])
long_term_churned = len(rfm_df[rfm_df['segment'] == 'CHURNED_OUT_LONG_TERM'])

print(f"\n   Churned Breakdown:")
print(f"   Recently (183-365):     {recently_churned:>6,}")
print(f"   Long-term (365+):       {long_term_churned:>6,}")
print(f"   Total churned:          {recently_churned + long_term_churned:>6,}")

# Verify logic
assert recently_churned + long_term_churned == churned_customers, "Churned breakdown doesn't match total!"
assert active_customers + churned_customers == total_customers, "Active + Churned doesn't equal total!"

print(f"   ✓ Logic verified!")

# Active segments
print(f"\n   Active Customer Segments:")
at_risk_hv = len(rfm_df[rfm_df['segment'] == 'AT_RISK_HIGH_VALUE'])
at_risk = len(rfm_df[rfm_df['segment'] == 'AT_RISK'])
loyal = len(rfm_df[rfm_df['segment'] == 'LOYAL_ACTIVE'])
active = len(rfm_df[rfm_df['segment'] == 'ACTIVE'])
dormant = len(rfm_df[rfm_df['segment'] == 'DORMANT'])
occasional = len(rfm_df[rfm_df['segment'] == 'NEW_OR_OCCASIONAL'])
moderate = len(rfm_df[rfm_df['segment'] == 'MODERATE'])

print(f"   AT_RISK_HIGH_VALUE:     {at_risk_hv:>6,} (PRIORITY 1)")
print(f"   AT_RISK:                {at_risk:>6,}")
print(f"   LOYAL_ACTIVE:           {loyal:>6,}")
print(f"   ACTIVE:                 {active:>6,}")
print(f"   DORMANT:                {dormant:>6,}")
print(f"   NEW_OR_OCCASIONAL:      {occasional:>6,}")
print(f"   MODERATE:               {moderate:>6,}")

active_sum = at_risk_hv + at_risk + loyal + active + dormant + occasional + moderate
print(f"   Active segments sum:    {active_sum:>6,}")

assert active_sum == active_customers, "Active segments don't sum correctly!"
print(f"   ✓ Active segments verified!")

print("\n5. PRIORITY RANKING:")
print("="*80)

priority_df = system.get_priority_list()
print("\nTop 10 Priority Customers:")
print(priority_df[['customer_id', 'segment', 'action_priority', 'recency_days', 'frequency']].head(10).to_string(index=False))

print("\n6. EXPORT TEST:")
print("="*80)

# Export recently churned
recently_churned_df = system.rfm_analyzer.get_recently_churned()
recently_churned_df.to_excel('test_churned_out_recently.xlsx', index=False)
print(f"   ✓ Exported {len(recently_churned_df)} recently churned customers")

# Export all churned
all_churned_df = system.rfm_analyzer.get_churned_out()
all_churned_df.to_excel('test_all_churned_out.xlsx', index=False)
print(f"   ✓ Exported {len(all_churned_df)} total churned customers")

print("\n" + "="*80)
print("✅ ALL TESTS PASSED - LOGIC IS CORRECT!")
print("="*80)

print("\n📊 SUMMARY:")
print(f"   Total: {total_customers:,}")
print(f"   Active: {active_customers:,} ({active_customers/total_customers*100:.1f}%)")
print(f"   Churned: {churned_customers:,} ({churned_customers/total_customers*100:.1f}%)")
print(f"     ├─ Recently (183-365): {recently_churned:,}")
print(f"     └─ Long-term (365+): {long_term_churned:,}")
print(f"\n   Priority 1 (At-Risk High Value): {at_risk_hv:,}")
