"""
Multi-Factor Churn Analysis
============================
Calculates churn considering State, Retailer, and Customer-Retailer relationship.

Factors:
1. State - Regional buying patterns
2. Retailer - Retailer-specific patterns
3. Customer-Retailer Loyalty - How loyal is customer to specific retailer
"""

import pandas as pd
import numpy as np

print("="*80)
print("MULTI-FACTOR CHURN ANALYSIS")
print("State + Retailer + Customer-Retailer Relationship")
print("="*80)

# Load data
print("\n1. Loading data...")
df = pd.read_excel('Plumber banking data Apr 24- Dec 25.xlsx', sheet_name='XYZ')
df['TRXN_DATE'] = pd.to_datetime(df['TRXN_DATE'])
analysis_date = df['TRXN_DATE'].max()

print(f"   Transactions: {len(df):,}")
print(f"   Analysis Date: {analysis_date}")

# ============================================================================
# BUILD CUSTOMER PROFILE
# ============================================================================
print("\n2. Building customer profiles...")

# Customer-level aggregation
customer_data = df.groupby('MEMBERSHIP ID').agg({
    'TRXN_DATE': ['min', 'max', 'count'],
    'STATE': 'first',
    'RETAILER CODE': lambda x: x.mode()[0] if len(x) > 0 else None,  # Primary retailer
    'DISTRIBUTOR CODE': 'first',
    'POINT_AWARDED': 'sum',
    'INVOICE_NO': 'nunique'
}).reset_index()

customer_data.columns = ['customer_id', 'first_purchase', 'last_purchase', 'frequency',
                         'state', 'primary_retailer', 'distributor', 'total_points', 'unique_invoices']

customer_data['recency'] = (analysis_date - customer_data['last_purchase']).dt.days
customer_data['lifetime'] = (customer_data['last_purchase'] - customer_data['first_purchase']).dt.days
customer_data['avg_gap'] = customer_data.apply(
    lambda r: r['lifetime'] / (r['frequency'] - 1) if r['frequency'] > 1 else 60, axis=1
)

# Customer-Retailer relationship
print("\n3. Analyzing Customer-Retailer relationships...")
cust_retailer = df.groupby(['MEMBERSHIP ID', 'RETAILER CODE']).agg({
    'INVOICE_NO': 'count',
    'TRXN_DATE': ['min', 'max']
}).reset_index()
cust_retailer.columns = ['customer_id', 'retailer', 'txn_count', 'first_txn', 'last_txn']
cust_retailer['relationship_days'] = (cust_retailer['last_txn'] - cust_retailer['first_txn']).dt.days

# Get primary retailer metrics
primary_metrics = cust_retailer.loc[
    cust_retailer.groupby('customer_id')['txn_count'].idxmax()
][['customer_id', 'txn_count', 'relationship_days']]
primary_metrics.columns = ['customer_id', 'primary_retailer_txns', 'retailer_relationship_days']

customer_data = customer_data.merge(primary_metrics, on='customer_id', how='left')

# Calculate retailer loyalty score (0-1)
customer_data['retailer_loyalty'] = customer_data['primary_retailer_txns'] / customer_data['frequency']

print(f"   Unique Customers: {len(customer_data):,}")
print(f"   Unique States: {customer_data['state'].nunique()}")
print(f"   Unique Retailers: {customer_data['primary_retailer'].nunique()}")

# ============================================================================
# CALCULATE FACTOR-SPECIFIC PATTERNS
# ============================================================================
print("\n4. Calculating factor patterns...")

# STATE patterns
state_patterns = customer_data.groupby('state').agg({
    'avg_gap': 'median',
    'frequency': 'median',
    'customer_id': 'count'
}).reset_index()
state_patterns.columns = ['state', 'state_median_gap', 'state_median_freq', 'state_customers']
state_patterns['state_threshold'] = state_patterns['state_median_gap'].apply(
    lambda x: int(min(max(x * 3, 90), 365))
)

print("\nState Patterns:")
print(state_patterns.to_string(index=False))

# RETAILER patterns (top 20 by customer count)
retailer_patterns = customer_data.groupby('primary_retailer').agg({
    'avg_gap': 'median',
    'frequency': 'median',
    'customer_id': 'count'
}).reset_index()
retailer_patterns.columns = ['retailer', 'retailer_median_gap', 'retailer_median_freq', 'retailer_customers']
retailer_patterns = retailer_patterns[retailer_patterns['retailer_customers'] >= 10]
retailer_patterns['retailer_threshold'] = retailer_patterns['retailer_median_gap'].apply(
    lambda x: int(min(max(x * 3, 90), 365))
)

print(f"\nRetailer Patterns ({len(retailer_patterns)} retailers with 10+ customers)")

# ============================================================================
# APPLY MULTI-FACTOR CHURN CALCULATION
# ============================================================================
print("\n5. Calculating multi-factor churn...")

FLAT_THRESHOLD = 183

# Map thresholds
state_thresh_map = state_patterns.set_index('state')['state_threshold'].to_dict()
retailer_thresh_map = retailer_patterns.set_index('retailer')['retailer_threshold'].to_dict()

customer_data['state_threshold'] = customer_data['state'].map(state_thresh_map).fillna(FLAT_THRESHOLD)
customer_data['retailer_threshold'] = customer_data['primary_retailer'].map(retailer_thresh_map).fillna(FLAT_THRESHOLD)

# Combined threshold: weighted average based on retailer loyalty
# Higher loyalty = use retailer threshold more
customer_data['combined_threshold'] = (
    customer_data['retailer_loyalty'] * customer_data['retailer_threshold'] +
    (1 - customer_data['retailer_loyalty']) * customer_data['state_threshold']
).astype(int)

# Ensure bounds
customer_data['combined_threshold'] = customer_data['combined_threshold'].clip(90, 365)

# Calculate churn under different methods
customer_data['churned_flat'] = customer_data['recency'] >= FLAT_THRESHOLD
customer_data['churned_state'] = customer_data['recency'] >= customer_data['state_threshold']
customer_data['churned_retailer'] = customer_data['recency'] >= customer_data['retailer_threshold']
customer_data['churned_combined'] = customer_data['recency'] >= customer_data['combined_threshold']

# ============================================================================
# RESULTS COMPARISON
# ============================================================================
print("\n" + "="*80)
print("RESULTS COMPARISON")
print("="*80)

total = len(customer_data)
methods = {
    'Flat (183d)': 'churned_flat',
    'State-Adjusted': 'churned_state',
    'Retailer-Adjusted': 'churned_retailer',
    'Combined (State+Retailer)': 'churned_combined'
}

print(f"\n{'Method':<30} {'Churned':>10} {'Active':>10} {'Churn Rate':>12}")
print("-"*65)
for name, col in methods.items():
    churned = customer_data[col].sum()
    print(f"{name:<30} {churned:>10,} {total-churned:>10,} {churned/total*100:>11.1f}%")

# ============================================================================
# BREAKDOWN BY STATE
# ============================================================================
print("\n" + "="*80)
print("CHURN BY STATE (All Methods)")
print("="*80)

state_breakdown = customer_data.groupby('state').agg({
    'customer_id': 'count',
    'state_threshold': 'first',
    'churned_flat': 'mean',
    'churned_state': 'mean',
    'churned_combined': 'mean'
}).reset_index()
state_breakdown.columns = ['state', 'customers', 'threshold', 'flat_rate', 'state_rate', 'combined_rate']
state_breakdown = state_breakdown.sort_values('customers', ascending=False)

print(f"\n{'State':<20} {'Customers':>10} {'Thresh':>8} {'Flat%':>8} {'State%':>8} {'Combined%':>10}")
print("-"*70)
for _, row in state_breakdown.iterrows():
    print(f"{row['state']:<20} {row['customers']:>10,} {row['threshold']:>7.0f}d {row['flat_rate']*100:>7.1f}% {row['state_rate']*100:>7.1f}% {row['combined_rate']*100:>9.1f}%")

# ============================================================================
# TOP RETAILERS ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("TOP 15 RETAILERS (by customer count)")
print("="*80)

retailer_breakdown = customer_data.groupby('primary_retailer').agg({
    'customer_id': 'count',
    'retailer_threshold': 'first',
    'churned_flat': 'mean',
    'churned_retailer': 'mean',
    'churned_combined': 'mean',
    'retailer_loyalty': 'mean'
}).reset_index()
retailer_breakdown.columns = ['retailer', 'customers', 'threshold', 'flat_rate', 'retailer_rate', 'combined_rate', 'avg_loyalty']
retailer_breakdown = retailer_breakdown[retailer_breakdown['customers'] >= 10]
retailer_breakdown = retailer_breakdown.sort_values('customers', ascending=False)

print(f"\n{'Retailer':<20} {'Cust':>8} {'Thresh':>7} {'Flat%':>7} {'Ret%':>7} {'Comb%':>7} {'Loyalty':>8}")
print("-"*75)
for _, row in retailer_breakdown.head(15).iterrows():
    retailer_name = str(row['retailer'])[:18]
    print(f"{retailer_name:<20} {row['customers']:>8,} {row['threshold']:>6.0f}d {row['flat_rate']*100:>6.1f}% {row['retailer_rate']*100:>6.1f}% {row['combined_rate']*100:>6.1f}% {row['avg_loyalty']:>7.1%}")

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

with pd.ExcelWriter('multi_factor_churn_analysis.xlsx', engine='openpyxl') as writer:
    
    # Summary by state
    state_breakdown.to_excel(writer, sheet_name='State_Breakdown', index=False)
    
    # Summary by retailer
    retailer_breakdown.to_excel(writer, sheet_name='Retailer_Breakdown', index=False)
    
    # Full customer data
    customer_data.to_excel(writer, sheet_name='All_Customers', index=False)
    
    # State patterns
    state_patterns.to_excel(writer, sheet_name='State_Patterns', index=False)
    
    # Retailer patterns
    retailer_patterns.to_excel(writer, sheet_name='Retailer_Patterns', index=False)
    
    # Auto-size columns
    for sheet in writer.sheets:
        ws = writer.sheets[sheet]
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 12), 30)

print("✅ Saved: multi_factor_churn_analysis.xlsx")
print("\nSheets:")
print("  - State_Breakdown: Churn by state (all methods)")
print("  - Retailer_Breakdown: Churn by retailer (all methods)")
print("  - All_Customers: Full customer data with all thresholds")
print("  - State_Patterns: State-level buying patterns")
print("  - Retailer_Patterns: Retailer-level buying patterns")

# Summary
print("\n" + "="*80)
print("KEY FINDINGS")
print("="*80)

flat_churn = customer_data['churned_flat'].mean() * 100
combined_churn = customer_data['churned_combined'].mean() * 100
diff = combined_churn - flat_churn

print(f"""
Multi-Factor Analysis considers:
  1. STATE patterns (median purchase gap per state)
  2. RETAILER patterns (median purchase gap per retailer)
  3. CUSTOMER-RETAILER LOYALTY (how loyal customer is to primary retailer)

Combined Threshold Formula:
  threshold = (loyalty × retailer_threshold) + ((1-loyalty) × state_threshold)

Results:
  - Flat Method: {flat_churn:.1f}% churn
  - Combined Method: {combined_churn:.1f}% churn
  - Difference: {diff:+.1f}%
  
Recommendation: 
  Use Combined method for more accurate, personalized churn detection.
""")
