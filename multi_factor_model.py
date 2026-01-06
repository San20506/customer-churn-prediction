"""
MULTI-FACTOR BANKING & CHURN PREDICTION MODEL
==============================================
Hypothesis: State, Retailer, Distributor, and historical behavior affect future banking & churn

Objective:
1. Study existing data to find which factors matter
2. Predict banking points for next 3 months
3. Predict churn probability for next 3 months
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, classification_report

print("="*80)
print("MULTI-FACTOR BANKING & CHURN PREDICTION MODEL")
print("="*80)

# ============================================================================
# 1. LOAD AND PREPARE DATA
# ============================================================================
print("\n" + "="*80)
print("1. LOADING DATA")
print("="*80)

df = pd.read_excel('Plumber banking data Apr 24- Dec 25.xlsx', sheet_name='XYZ')
df['TRXN_DATE'] = pd.to_datetime(df['TRXN_DATE'])
df['month'] = df['TRXN_DATE'].dt.to_period('M')

analysis_date = df['TRXN_DATE'].max()
print(f"Transactions: {len(df):,}")
print(f"Date Range: {df['TRXN_DATE'].min().date()} to {analysis_date.date()}")

# ============================================================================
# 2. FEATURE ENGINEERING
# ============================================================================
print("\n" + "="*80)
print("2. FEATURE ENGINEERING")
print("="*80)

# Customer-level features
print("Building customer profiles...")

customer_data = df.groupby('MEMBERSHIP ID').agg({
    'TRXN_DATE': ['min', 'max', 'count'],
    'STATE': 'first',
    'RETAILER CODE': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown',
    'DISTRIBUTOR CODE': 'first',
    'POINT_AWARDED': ['sum', 'mean', 'std'],
    'QUANTITY': ['sum', 'mean'],
    'INVOICE_NO': 'nunique'
}).reset_index()

customer_data.columns = [
    'customer_id', 'first_purchase', 'last_purchase', 'frequency',
    'state', 'primary_retailer', 'distributor',
    'total_points', 'avg_points_per_txn', 'points_std',
    'total_qty', 'avg_qty',
    'unique_invoices'
]

# Time-based features
customer_data['recency'] = (analysis_date - customer_data['last_purchase']).dt.days
customer_data['tenure'] = (customer_data['last_purchase'] - customer_data['first_purchase']).dt.days
customer_data['avg_purchase_gap'] = customer_data.apply(
    lambda r: r['tenure'] / (r['frequency'] - 1) if r['frequency'] > 1 else 60, axis=1
)

# Monthly banking average (last 6 months)
last_6months = analysis_date - timedelta(days=180)
monthly_banking = df[df['TRXN_DATE'] >= last_6months].groupby('MEMBERSHIP ID')['POINT_AWARDED'].sum() / 6
customer_data = customer_data.merge(
    monthly_banking.reset_index().rename(columns={'POINT_AWARDED': 'monthly_avg_points'}),
    left_on='customer_id', right_on='MEMBERSHIP ID', how='left'
).drop('MEMBERSHIP ID', axis=1)
customer_data['monthly_avg_points'] = customer_data['monthly_avg_points'].fillna(0)

# Banking trend (comparing recent 3 months to previous 3 months)
last_3months = analysis_date - timedelta(days=90)
prev_3months = analysis_date - timedelta(days=180)

recent = df[df['TRXN_DATE'] >= last_3months].groupby('MEMBERSHIP ID')['POINT_AWARDED'].sum()
previous = df[(df['TRXN_DATE'] >= prev_3months) & (df['TRXN_DATE'] < last_3months)].groupby('MEMBERSHIP ID')['POINT_AWARDED'].sum()

trend_df = pd.DataFrame({'recent': recent, 'previous': previous}).fillna(0)
trend_df['trend'] = (trend_df['recent'] - trend_df['previous']) / (trend_df['previous'] + 1)
customer_data = customer_data.merge(
    trend_df['trend'].reset_index().rename(columns={'MEMBERSHIP ID': 'customer_id'}),
    on='customer_id', how='left'
)
customer_data['trend'] = customer_data['trend'].fillna(0)

# Churn label
customer_data['is_churned'] = customer_data['recency'] >= 183

# Points std fill
customer_data['points_std'] = customer_data['points_std'].fillna(0)

print(f"Customers: {len(customer_data):,}")
print(f"Features: {len(customer_data.columns)}")

# ============================================================================
# 3. STATE/RETAILER/DISTRIBUTOR PATTERNS
# ============================================================================
print("\n" + "="*80)
print("3. FACTOR PATTERNS")
print("="*80)

# STATE patterns
state_patterns = customer_data.groupby('state').agg({
    'total_points': 'mean',
    'frequency': 'mean',
    'is_churned': 'mean',
    'avg_purchase_gap': 'median',
    'customer_id': 'count'
}).reset_index()
state_patterns.columns = ['state', 'state_avg_points', 'state_avg_freq', 'state_churn_rate', 'state_avg_gap', 'state_count']

# RETAILER patterns
retailer_patterns = customer_data.groupby('primary_retailer').agg({
    'total_points': 'mean',
    'frequency': 'mean',
    'is_churned': 'mean',
    'customer_id': 'count'
}).reset_index()
retailer_patterns.columns = ['primary_retailer', 'retailer_avg_points', 'retailer_avg_freq', 'retailer_churn_rate', 'retailer_count']
retailer_patterns = retailer_patterns[retailer_patterns['retailer_count'] >= 5]  # Min 5 customers

# DISTRIBUTOR patterns
dist_patterns = customer_data.groupby('distributor').agg({
    'total_points': 'mean',
    'frequency': 'mean',
    'is_churned': 'mean',
    'customer_id': 'count'
}).reset_index()
dist_patterns.columns = ['distributor', 'dist_avg_points', 'dist_avg_freq', 'dist_churn_rate', 'dist_count']
dist_patterns = dist_patterns[dist_patterns['dist_count'] >= 5]

# Merge patterns back
customer_data = customer_data.merge(state_patterns[['state', 'state_avg_points', 'state_churn_rate']], on='state', how='left')
customer_data = customer_data.merge(retailer_patterns[['primary_retailer', 'retailer_avg_points', 'retailer_churn_rate']], on='primary_retailer', how='left')
customer_data = customer_data.merge(dist_patterns[['distributor', 'dist_avg_points', 'dist_churn_rate']], on='distributor', how='left')

# Fill NA
for col in ['retailer_avg_points', 'retailer_churn_rate', 'dist_avg_points', 'dist_churn_rate']:
    customer_data[col] = customer_data[col].fillna(customer_data[col].median())

print("Factor patterns computed:")
print(f"  States: {len(state_patterns)}")
print(f"  Retailers (5+ customers): {len(retailer_patterns)}")
print(f"  Distributors (5+ customers): {len(dist_patterns)}")

# ============================================================================
# 4. FACTOR IMPORTANCE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("4. FACTOR IMPORTANCE ANALYSIS")
print("="*80)

# Prepare features for modeling
features_for_model = [
    # Historical behavior
    'frequency', 'total_points', 'avg_points_per_txn', 'points_std',
    'avg_purchase_gap', 'tenure', 'monthly_avg_points', 'trend',
    # State/Retailer/Distributor effects
    'state_avg_points', 'state_churn_rate',
    'retailer_avg_points', 'retailer_churn_rate',
    'dist_avg_points', 'dist_churn_rate'
]

X = customer_data[features_for_model].copy()
y_churn = customer_data['is_churned'].astype(int)
y_points = customer_data['monthly_avg_points']

# Handle any remaining NaN
X = X.fillna(X.median())

# Train-test split
X_train, X_test, y_churn_train, y_churn_test = train_test_split(X, y_churn, test_size=0.2, random_state=42)
_, _, y_points_train, y_points_test = train_test_split(X, y_points, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -- CHURN MODEL --
print("\n--- CHURN PREDICTION MODEL ---")
churn_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
churn_model.fit(X_train_scaled, y_churn_train)
churn_preds = churn_model.predict(X_test_scaled)
churn_proba = churn_model.predict_proba(X_test_scaled)[:, 1]

print(f"Accuracy: {accuracy_score(y_churn_test, churn_preds)*100:.1f}%")
print("\nFeature Importance for CHURN:")

churn_importance = pd.DataFrame({
    'feature': features_for_model,
    'importance': churn_model.feature_importances_
}).sort_values('importance', ascending=False)

for _, row in churn_importance.head(10).iterrows():
    bar = "█" * int(row['importance'] * 50)
    print(f"  {row['feature']:<25} {row['importance']:.3f} {bar}")

# -- BANKING POINTS MODEL --
print("\n--- BANKING POINTS PREDICTION MODEL ---")
points_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
points_model.fit(X_train_scaled, y_points_train)
points_preds = points_model.predict(X_test_scaled)

r2 = r2_score(y_points_test, points_preds)
mae = mean_absolute_error(y_points_test, points_preds)
print(f"R² Score: {r2:.3f}")
print(f"Mean Absolute Error: {mae:.1f} points")

print("\nFeature Importance for BANKING POINTS:")

points_importance = pd.DataFrame({
    'feature': features_for_model,
    'importance': points_model.feature_importances_
}).sort_values('importance', ascending=False)

for _, row in points_importance.head(10).iterrows():
    bar = "█" * int(row['importance'] * 50)
    print(f"  {row['feature']:<25} {row['importance']:.3f} {bar}")

# ============================================================================
# 5. FACTOR SIGNIFICANCE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("5. STATISTICAL SIGNIFICANCE OF FACTORS")
print("="*80)

print("\n--- Does STATE affect churn? ---")
state_chi2, state_p = stats.chi2_contingency(pd.crosstab(customer_data['state'], customer_data['is_churned']))[:2]
print(f"Chi-Square: {state_chi2:.2f}, p-value: {state_p:.6f}")
print(f"Result: {'SIGNIFICANT' if state_p < 0.05 else 'NOT SIGNIFICANT'}")

print("\n--- Does RETAILER affect churn? (top 10 retailers) ---")
top_retailers = customer_data['primary_retailer'].value_counts().head(10).index
subset = customer_data[customer_data['primary_retailer'].isin(top_retailers)]
ret_chi2, ret_p = stats.chi2_contingency(pd.crosstab(subset['primary_retailer'], subset['is_churned']))[:2]
print(f"Chi-Square: {ret_chi2:.2f}, p-value: {ret_p:.6f}")
print(f"Result: {'SIGNIFICANT' if ret_p < 0.05 else 'NOT SIGNIFICANT'}")

print("\n--- Does DISTRIBUTOR affect churn? ---")
top_dist = customer_data['distributor'].value_counts().head(10).index
subset_dist = customer_data[customer_data['distributor'].isin(top_dist)]
dist_chi2, dist_p = stats.chi2_contingency(pd.crosstab(subset_dist['distributor'], subset_dist['is_churned']))[:2]
print(f"Chi-Square: {dist_chi2:.2f}, p-value: {dist_p:.6f}")
print(f"Result: {'SIGNIFICANT' if dist_p < 0.05 else 'NOT SIGNIFICANT'}")

print("\n--- Does HISTORICAL BEHAVIOR affect churn? ---")
# Compare avg_purchase_gap between churned and active
churned_gap = customer_data[customer_data['is_churned']]['avg_purchase_gap']
active_gap = customer_data[~customer_data['is_churned']]['avg_purchase_gap']
t_stat, t_p = stats.ttest_ind(churned_gap, active_gap)
print(f"T-test (purchase gap): t={t_stat:.2f}, p-value: {t_p:.10f}")
print(f"Result: {'SIGNIFICANT' if t_p < 0.05 else 'NOT SIGNIFICANT'}")

# ============================================================================
# 6. 3-MONTH PREDICTION
# ============================================================================
print("\n" + "="*80)
print("6. 3-MONTH PREDICTION")
print("="*80)

# Use full data for final prediction
X_all = customer_data[features_for_model].fillna(customer_data[features_for_model].median())
X_all_scaled = scaler.transform(X_all)

# Predict churn probability
customer_data['churn_prob'] = churn_model.predict_proba(X_all_scaled)[:, 1]

# Predict next month points (using trend)
customer_data['predicted_monthly_points'] = points_model.predict(X_all_scaled)

# Classify risk
def get_risk(prob):
    if prob >= 0.7:
        return 'HIGH'
    elif prob >= 0.4:
        return 'MEDIUM'
    else:
        return 'LOW'

customer_data['churn_risk'] = customer_data['churn_prob'].apply(get_risk)

# Get next 3 months
current_month = analysis_date.month
months = [(current_month + i - 1) % 12 + 1 for i in range(1, 4)]
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

print(f"\nPredicting for next 3 months: {', '.join([month_names[m-1] for m in months])}")

# Summary
high_risk = (customer_data['churn_risk'] == 'HIGH').sum()
med_risk = (customer_data['churn_risk'] == 'MEDIUM').sum()
low_risk = (customer_data['churn_risk'] == 'LOW').sum()

print(f"\nChurn Risk Distribution:")
print(f"  🔴 HIGH RISK:   {high_risk:,} ({high_risk/len(customer_data)*100:.1f}%)")
print(f"  🟡 MEDIUM RISK: {med_risk:,} ({med_risk/len(customer_data)*100:.1f}%)")
print(f"  🟢 LOW RISK:    {low_risk:,} ({low_risk/len(customer_data)*100:.1f}%)")

# Predicted banking
total_pred_points = customer_data['predicted_monthly_points'].sum() * 3
print(f"\nPredicted Total Banking (3 months): {total_pred_points:,.0f} points")

# ============================================================================
# 7. FACTOR SUMMARY
# ============================================================================
print("\n" + "="*80)
print("7. FACTOR IMPACT SUMMARY")
print("="*80)

print("""
┌────────────────────────────────────────────────────────────────────────────┐
│                     FACTORS AFFECTING BANKING & CHURN                       │
├─────────────────────┬─────────────────────┬────────────────────────────────┤
│ FACTOR              │ SIGNIFICANCE        │ IMPORTANCE (ML Model)          │
├─────────────────────┼─────────────────────┼────────────────────────────────┤""")

factors = [
    ('STATE', 'SIGNIFICANT' if state_p < 0.05 else 'NOT SIGNIFICANT', 
     churn_importance[churn_importance['feature'].str.contains('state')]['importance'].sum()),
    ('RETAILER', 'SIGNIFICANT' if ret_p < 0.05 else 'NOT SIGNIFICANT',
     churn_importance[churn_importance['feature'].str.contains('retailer')]['importance'].sum()),
    ('DISTRIBUTOR', 'SIGNIFICANT' if dist_p < 0.05 else 'NOT SIGNIFICANT',
     churn_importance[churn_importance['feature'].str.contains('dist')]['importance'].sum()),
    ('HISTORICAL BEHAVIOR', 'SIGNIFICANT' if t_p < 0.05 else 'NOT SIGNIFICANT',
     churn_importance[~churn_importance['feature'].str.contains('state|retailer|dist')]['importance'].sum())
]

for factor, sig, imp in factors:
    sig_icon = "✅" if "SIGNIFICANT" in sig else "❌"
    print(f"│ {factor:<19} │ {sig_icon} {sig:<17} │ {imp:.3f} ({imp*100:.1f}%)               │")

print("""└─────────────────────┴─────────────────────┴────────────────────────────────┘""")

# ============================================================================
# 8. SAVE RESULTS
# ============================================================================
print("\n" + "="*80)
print("8. SAVING RESULTS")
print("="*80)

# Prepare output
output_cols = [
    'customer_id', 'state', 'primary_retailer', 'distributor',
    'recency', 'frequency', 'total_points', 'monthly_avg_points', 'trend',
    'churn_prob', 'churn_risk', 'predicted_monthly_points', 'is_churned'
]

predictions = customer_data[output_cols].sort_values('churn_prob', ascending=False)

with pd.ExcelWriter('multi_factor_predictions.xlsx', engine='openpyxl') as writer:
    # Predictions
    predictions.to_excel(writer, sheet_name='Predictions', index=False)
    
    # Factor importance
    combined_importance = pd.concat([
        churn_importance.assign(target='Churn'),
        points_importance.assign(target='Banking Points')
    ])
    combined_importance.to_excel(writer, sheet_name='Feature_Importance', index=False)
    
    # State patterns
    state_patterns.to_excel(writer, sheet_name='State_Patterns', index=False)
    
    # High risk customers
    high_risk_df = predictions[predictions['churn_risk'] == 'HIGH']
    high_risk_df.to_excel(writer, sheet_name='High_Risk_Customers', index=False)
    
    # Summary stats
    summary = pd.DataFrame({
        'Metric': ['Total Customers', 'High Risk', 'Medium Risk', 'Low Risk',
                   'Churn Model Accuracy', 'Points Model R²',
                   'State Significant', 'Retailer Significant', 
                   'Distributor Significant', 'History Significant'],
        'Value': [len(customer_data), high_risk, med_risk, low_risk,
                  f"{accuracy_score(y_churn_test, churn_preds)*100:.1f}%", f"{r2:.3f}",
                  'Yes' if state_p < 0.05 else 'No',
                  'Yes' if ret_p < 0.05 else 'No',
                  'Yes' if dist_p < 0.05 else 'No',
                  'Yes' if t_p < 0.05 else 'No']
    })
    summary.to_excel(writer, sheet_name='Summary', index=False)

print("✅ Saved: multi_factor_predictions.xlsx")
print("\nSheets:")
print("  - Predictions: All customers with churn probability & predicted points")
print("  - Feature_Importance: Which factors matter most")
print("  - State_Patterns: State-level analysis")
print("  - High_Risk_Customers: Customers most likely to churn")
print("  - Summary: Overall statistics")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print(f"""
Your hypothesis has been tested on {len(customer_data):,} plumbers.

FINDINGS:
1. STATE: {'✅ AFFECTS' if state_p < 0.05 else '❌ DOES NOT AFFECT'} churn (p={state_p:.6f})
2. RETAILER: {'✅ AFFECTS' if ret_p < 0.05 else '❌ DOES NOT AFFECT'} churn (p={ret_p:.6f})
3. DISTRIBUTOR: {'✅ AFFECTS' if dist_p < 0.05 else '❌ DOES NOT AFFECT'} churn (p={dist_p:.6f})
4. HISTORY: {'✅ AFFECTS' if t_p < 0.05 else '❌ DOES NOT AFFECT'} churn (p={t_p:.10f})

TOP PREDICTORS OF CHURN:
{churn_importance.head(5).to_string(index=False)}

TOP PREDICTORS OF BANKING POINTS:
{points_importance.head(5).to_string(index=False)}

MODEL PERFORMANCE:
- Churn Prediction Accuracy: {accuracy_score(y_churn_test, churn_preds)*100:.1f}%
- Banking Points R² Score: {r2:.3f}

3-MONTH FORECAST:
- High Risk Customers: {high_risk:,}
- Predicted Banking: {total_pred_points:,.0f} points
""")
