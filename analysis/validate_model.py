"""
MODEL VALIDATION - CHECK FOR DATA LEAKAGE
==========================================
99.7% accuracy is suspicious. Let's investigate.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

print("="*80)
print("INVESTIGATING MODEL - IS IT TOO GOOD TO BE TRUE?")
print("="*80)

# Load data
df = pd.read_excel('Plumber banking data Apr 24- Dec 25.xlsx', sheet_name='XYZ')
df['TRXN_DATE'] = pd.to_datetime(df['TRXN_DATE'])
analysis_date = df['TRXN_DATE'].max()

# Build customer data
customer_data = df.groupby('MEMBERSHIP ID').agg({
    'TRXN_DATE': ['min', 'max', 'count'],
    'POINT_AWARDED': ['sum', 'mean'],
    'STATE': 'first'
}).reset_index()
customer_data.columns = ['customer_id', 'first', 'last', 'frequency', 'total_points', 'avg_points', 'state']
customer_data['recency'] = (analysis_date - customer_data['last']).dt.days
customer_data['tenure'] = (customer_data['last'] - customer_data['first']).dt.days
customer_data['is_churned'] = customer_data['recency'] >= 183

print("\n1. CHECKING THE PROBLEM")
print("="*50)
print(f"Churn Definition: recency >= 183 days")
print(f"Is 'recency' used as a feature? YES!")
print("\n⚠️ THIS IS DATA LEAKAGE!")
print("The model learns: if recency >= 183 → churned")
print("This is the DEFINITION, not a prediction!")

# Check correlation
print("\n2. FEATURE CORRELATION WITH TARGET")
print("="*50)
features = ['recency', 'frequency', 'total_points', 'avg_points', 'tenure']
for f in features:
    if f in customer_data.columns:
        corr = customer_data[f].corr(customer_data['is_churned'].astype(float))
        print(f"  {f}: {corr:.3f}")
        if abs(corr) > 0.9:
            print(f"    ⚠️ LEAKAGE! This feature defines the target!")

# Test: What if we REMOVE recency?
print("\n3. MODEL WITHOUT RECENCY (Fair Test)")
print("="*50)

# Features WITHOUT recency
X_fair = customer_data[['frequency', 'total_points', 'avg_points', 'tenure']].fillna(0)
y = customer_data['is_churned'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X_fair, y, test_size=0.3, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)

fair_accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy WITHOUT recency: {fair_accuracy*100:.1f}%")
print("\n Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Active', 'Churned']))

# Feature importance
importance = pd.DataFrame({
    'feature': ['frequency', 'total_points', 'avg_points', 'tenure'],
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nFeature Importance (Fair Model):")
for _, row in importance.iterrows():
    bar = "█" * int(row['importance'] * 30)
    print(f"  {row['feature']:<15} {row['importance']:.3f} {bar}")

# What makes a GOOD model
print("\n4. WHAT MAKES A GOOD CHURN MODEL")
print("="*50)
print("""
A TRUE predictive model should:
1. NOT use recency as a direct feature (it's the target definition!)
2. Use features that were known BEFORE the customer churned
3. Be validated on out-of-time data (train on old, test on new)
4. Achieve 70-85% accuracy (realistic for churn problems)

What the current model does WRONG:
1. Uses recency → directly encodes the target definition
2. Uses current state metrics → not available before churn
3. No time-based validation → sees future data
4. 99.7% accuracy → too good to be real

HOW TO FIX:
1. Define target: "Will churn in NEXT 3 months"
2. Use only features from BEFORE the prediction date
3. Train on customers who were active 6 months ago
4. Test on customers who became active more recently
""")

# Better approach: Predicting FUTURE churn
print("\n5. PROPER MODEL: Predict FUTURE Churn")
print("="*50)

# Use data from 6 months ago to predict if customer churned by now
cutoff_date = analysis_date - pd.Timedelta(days=183)

# Features calculated as of cutoff_date
old_data = df[df['TRXN_DATE'] <= cutoff_date]
old_customers = old_data.groupby('MEMBERSHIP ID').agg({
    'TRXN_DATE': ['min', 'max', 'count'],
    'POINT_AWARDED': ['sum', 'mean']
}).reset_index()
old_customers.columns = ['customer_id', 'first', 'last_at_cutoff', 'frequency', 'total_points', 'avg_points']
old_customers['recency_at_cutoff'] = (cutoff_date - old_customers['last_at_cutoff']).dt.days
old_customers['tenure'] = (old_customers['last_at_cutoff'] - old_customers['first']).dt.days

# Target: Did they churn after cutoff?
current_last = df.groupby('MEMBERSHIP ID')['TRXN_DATE'].max().reset_index()
current_last.columns = ['customer_id', 'final_purchase']
old_customers = old_customers.merge(current_last, on='customer_id')

# Churned if no purchase after cutoff
old_customers['did_churn'] = old_customers['final_purchase'] <= cutoff_date

print(f"Customers active as of {cutoff_date.date()}: {len(old_customers)}")
print(f"Did churn after: {old_customers['did_churn'].sum()} ({old_customers['did_churn'].mean()*100:.1f}%)")

# Proper model
X_proper = old_customers[['frequency', 'total_points', 'avg_points', 'tenure', 'recency_at_cutoff']].fillna(0)
y_proper = old_customers['did_churn'].astype(int)

# Note: We can use recency_at_cutoff because it's measured BEFORE the prediction window
X_train2, X_test2, y_train2, y_test2 = train_test_split(X_proper, y_proper, test_size=0.3, random_state=42)

scaler2 = StandardScaler()
X_train2_scaled = scaler2.fit_transform(X_train2)
X_test2_scaled = scaler2.transform(X_test2)

model2 = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model2.fit(X_train2_scaled, y_train2)
y_pred2 = model2.predict(X_test2_scaled)

proper_accuracy = accuracy_score(y_test2, y_pred2)
print(f"\nProper Model Accuracy: {proper_accuracy*100:.1f}%")
print("\n Classification Report:")
print(classification_report(y_test2, y_pred2, target_names=['Still Active', 'Churned']))

print("\n6. CONCLUSION")
print("="*50)
print(f"""
ORIGINAL MODEL: 99.7% accuracy
- ⚠️ DATA LEAKAGE: Uses recency which DEFINES churn
- Not a real prediction - just memorizing the definition

FAIR MODEL (no recency): {fair_accuracy*100:.1f}% accuracy
- Removes the leaky feature
- Still not ideal - doesn't predict FUTURE

PROPER MODEL (time-based): {proper_accuracy*100:.1f}% accuracy
- Uses only data from BEFORE prediction window
- Predicts if customer will churn in future
- THIS is the realistic performance

RECOMMENDATION:
Report {proper_accuracy*100:.1f}% as realistic accuracy, not 99.7%.
A good churn model typically achieves 65-80% accuracy.
""")
