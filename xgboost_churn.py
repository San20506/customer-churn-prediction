"""
XGBoost Churn Prediction Model
==============================
Binary classifier to predict WHO will churn.

Features:
- Recency (days since last purchase)
- Frequency (number of transactions)
- Monetary (total points/value)
- Average transaction value
- Days active (first to last purchase)
- Transaction trend (increasing/decreasing)
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import pickle
from pathlib import Path
from datetime import datetime

class ChurnPredictor:
    """XGBoost-based churn prediction model."""
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame, date_col: str, id_col: str, 
                         point_col: str = None, qty_col: str = None,
                         analysis_date: datetime = None) -> pd.DataFrame:
        """
        Create features for each customer.
        
        Returns DataFrame with one row per customer.
        """
        if analysis_date is None:
            analysis_date = df[date_col].max()
        
        # Group by customer
        customer_features = []
        
        for customer_id in df[id_col].unique():
            cust_df = df[df[id_col] == customer_id]
            
            # Basic RFM features
            last_purchase = cust_df[date_col].max()
            first_purchase = cust_df[date_col].min()
            recency = (analysis_date - last_purchase).days
            frequency = len(cust_df)
            
            # Monetary features
            total_points = cust_df[point_col].sum() if point_col and point_col in cust_df.columns else 0
            total_qty = cust_df[qty_col].sum() if qty_col and qty_col in cust_df.columns else 0
            
            # Derived features
            days_active = (last_purchase - first_purchase).days
            avg_points_per_txn = total_points / frequency if frequency > 0 else 0
            avg_qty_per_txn = total_qty / frequency if frequency > 0 else 0
            
            # Transaction frequency (transactions per active day)
            txn_frequency = frequency / max(days_active, 1)
            
            # Trend: compare first half vs second half activity
            mid_date = first_purchase + (last_purchase - first_purchase) / 2
            first_half = len(cust_df[cust_df[date_col] < mid_date])
            second_half = len(cust_df[cust_df[date_col] >= mid_date])
            trend = (second_half - first_half) / max(first_half, 1)  # Positive = increasing
            
            # Months since first purchase
            months_since_start = (analysis_date - first_purchase).days / 30
            
            customer_features.append({
                'customer_id': customer_id,
                'recency_days': recency,
                'frequency': frequency,
                'total_points': total_points,
                'total_qty': total_qty,
                'days_active': days_active,
                'avg_points_per_txn': avg_points_per_txn,
                'avg_qty_per_txn': avg_qty_per_txn,
                'txn_frequency': txn_frequency,
                'trend': trend,
                'months_since_start': months_since_start
            })
        
        features_df = pd.DataFrame(customer_features)
        return features_df
    
    def create_labels(self, features_df: pd.DataFrame, churn_threshold: int = 60) -> pd.DataFrame:
        """
        Create churn labels based on recency threshold.
        
        Churned = 1 if recency_days >= churn_threshold
        """
        features_df = features_df.copy()
        features_df['churned'] = (features_df['recency_days'] >= churn_threshold).astype(int)
        return features_df
    
    def train(self, features_df: pd.DataFrame, label_col: str = 'churned'):
        """
        Train XGBoost classifier.
        """
        # Separate features and labels
        self.feature_names = [c for c in features_df.columns 
                              if c not in ['customer_id', label_col]]
        
        X = features_df[self.feature_names]
        y = features_df[label_col]
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # XGBoost parameters
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        
        # Train
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='accuracy')
        
        return {
            'accuracy': round(accuracy, 4),
            'roc_auc': round(roc_auc, 4),
            'cv_mean': round(cv_scores.mean(), 4),
            'cv_std': round(cv_scores.std(), 4),
            'feature_importance': dict(zip(self.feature_names, 
                                           self.model.feature_importances_)),
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def predict(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict churn probability for each customer.
        """
        if not self.is_trained:
            raise Exception("Model not trained yet!")
        
        X = features_df[self.feature_names]
        
        # Get probabilities
        probs = self.model.predict_proba(X)[:, 1]
        preds = self.model.predict(X)
        
        result = features_df.copy()
        result['churn_probability'] = probs
        result['churn_prediction'] = preds
        result['risk_level'] = pd.cut(
            probs,
            bins=[0, 0.3, 0.5, 0.7, 1.0],
            labels=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        )
        
        return result
    
    def save_model(self, path: str):
        """Save trained model to file."""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_names': self.feature_names
            }, f)
    
    def load_model(self, path: str):
        """Load model from file."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.feature_names = data['feature_names']
            self.is_trained = True


# Test the model
if __name__ == "__main__":
    DATA_PATH = Path(r"d:\Skipper\Customer_churn_out_prediction_model\Book6.xlsx")
    
    print("=" * 60)
    print("XGBOOST CHURN PREDICTION MODEL")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    df = pd.read_excel(DATA_PATH, sheet_name="XYZ")  # Use larger sheet
    
    # Find columns
    date_col = [c for c in df.columns if 'date' in c.lower()][0]
    id_col = [c for c in df.columns if 'id' in c.lower() or 'loyalty' in c.lower()][0]
    point_col = [c for c in df.columns if 'point' in c.lower()]
    point_col = point_col[0] if point_col else None
    qty_col = [c for c in df.columns if 'qty' in c.lower() or 'quantity' in c.lower()]
    qty_col = qty_col[0] if qty_col else None
    
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df = df[df[date_col].dt.month != 12]  # Exclude December
    
    print(f"Loaded {len(df)} rows, {df[id_col].nunique()} unique customers")
    
    # Initialize predictor
    predictor = ChurnPredictor()
    
    # Prepare features
    print("\nPreparing features...")
    features = predictor.prepare_features(df, date_col, id_col, point_col, qty_col)
    print(f"Created {len(features)} customer feature rows")
    
    # Create labels
    features = predictor.create_labels(features, churn_threshold=60)
    churned_count = features['churned'].sum()
    print(f"Churned customers: {churned_count} ({churned_count/len(features)*100:.1f}%)")
    
    # Train model
    print("\nTraining XGBoost model...")
    results = predictor.train(features)
    
    print(f"\nModel Performance:")
    print(f"  Accuracy: {results['accuracy']*100:.2f}%")
    print(f"  ROC-AUC: {results['roc_auc']:.4f}")
    print(f"  Cross-validation: {results['cv_mean']*100:.2f}% (+/- {results['cv_std']*100:.2f}%)")
    
    print(f"\nFeature Importance:")
    sorted_features = sorted(results['feature_importance'].items(), 
                            key=lambda x: x[1], reverse=True)
    for feat, imp in sorted_features:
        print(f"  {feat}: {imp:.4f}")
    
    # Make predictions
    print("\nMaking predictions...")
    predictions = predictor.predict(features)
    
    # Show top 10 at-risk customers
    print("\nTop 10 At-Risk Customers:")
    top_risk = predictions.nlargest(10, 'churn_probability')
    print(top_risk[['customer_id', 'churn_probability', 'risk_level', 'recency_days']].to_string())
    
    # Save model
    model_path = "xgboost_churn_model.pkl"
    predictor.save_model(model_path)
    print(f"\nModel saved to {model_path}")
    
    # Save predictions
    predictions.to_csv("churn_predictions.csv", index=False)
    print("Predictions saved to churn_predictions.csv")
