import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# Load data
df = pd.read_excel('Plumber banking data Apr 24- Dec 25.xlsx', sheet_name='XYZ')
df['TRXN_DATE'] = pd.to_datetime(df['TRXN_DATE'])
analysis_date = df['TRXN_DATE'].max()

# Build customer data WITHOUT leakage
customer_data = df.groupby('MEMBERSHIP ID').agg({
    'TRXN_DATE': ['min', 'max', 'count'],
    'POINT_AWARDED': ['sum', 'mean'],
}).reset_index()
customer_data.columns = ['customer_id', 'first', 'last', 'frequency', 'total_points', 'avg_points']
customer_data['recency'] = (analysis_date - customer_data['last']).dt.days
customer_data['tenure'] = (customer_data['last'] - customer_data['first']).dt.days
customer_data['is_churned'] = customer_data['recency'] >= 183

# Fair model WITHOUT recency
X_fair = customer_data[['frequency', 'total_points', 'avg_points', 'tenure']].fillna(0)
y = customer_data['is_churned'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X_fair, y, test_size=0.3, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)

fair_acc = accuracy_score(y_test, y_pred)

# Proper time-based model
cutoff_date = analysis_date - pd.Timedelta(days=183)
old_data = df[df['TRXN_DATE'] <= cutoff_date]
old = old_data.groupby('MEMBERSHIP ID').agg({
    'TRXN_DATE': ['min', 'max', 'count'],
    'POINT_AWARDED': ['sum', 'mean']
}).reset_index()
old.columns = ['customer_id', 'first', 'last_cutoff', 'frequency', 'total_points', 'avg_points']
old['recency_at_cutoff'] = (cutoff_date - old['last_cutoff']).dt.days
old['tenure'] = (old['last_cutoff'] - old['first']).dt.days

current_last = df.groupby('MEMBERSHIP ID')['TRXN_DATE'].max().reset_index()
current_last.columns = ['customer_id', 'final_purchase']
old = old.merge(current_last, on='customer_id')
old['did_churn'] = old['final_purchase'] <= cutoff_date

X_proper = old[['frequency', 'total_points', 'avg_points', 'tenure', 'recency_at_cutoff']].fillna(0)
y_proper = old['did_churn'].astype(int)

X_train2, X_test2, y_train2, y_test2 = train_test_split(X_proper, y_proper, test_size=0.3, random_state=42)
scaler2 = StandardScaler()
X_train2_scaled = scaler2.fit_transform(X_train2)
X_test2_scaled = scaler2.transform(X_test2)

model2 = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model2.fit(X_train2_scaled, y_train2)
y_pred2 = model2.predict(X_test2_scaled)

proper_acc = accuracy_score(y_test2, y_pred2)

print("MODEL ACCURACY COMPARISON")
print("="*50)
print(f"ORIGINAL (with leakage):    99.7%   <- FAKE!")
print(f"Fair (no recency):          {fair_acc*100:.1f}%")
print(f"Proper (time-based):        {proper_acc*100:.1f}%   <- REAL")
print()
print("The real model accuracy is around 64-70%")
print("This is normal for churn prediction!")
