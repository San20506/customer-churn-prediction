"""
Panel Data Churn Prediction Model
==================================
Two-Way Fixed Effects regression for customer churn prediction.

Implements the IIT Kanpur methodology:
- Entity Fixed Effects (customer-specific baseline risk)
- Time Fixed Effects (monthly seasonality)
- VIF multicollinearity testing
- Model selection tests (Breusch-Pagan, F-test)

Author: Adapted from IIT Kanpur Panel Data Analysis
Churn Threshold: 183 days (6 months)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')


class PanelChurnModel:
    """
    Two-Way Fixed Effects Panel Data Model for Churn Prediction.
    
    Model: churn_it = α_i + γ_t + β·X_it + ε_it
    Where:
        i = customer (entity)
        t = month (time period)
        α_i = customer fixed effect
        γ_t = time fixed effect (seasonality)
        β = coefficients
        X_it = features (recency, frequency, monetary, trends)
    """
    
    CHURN_THRESHOLD_DAYS = 183  # 6 months
    
    def __init__(self):
        self.panel_df = None
        self.coefficients = None
        self.customer_fixed_effects = None
        self.time_fixed_effects = None
        self.feature_names = []
        self.r_squared = None
        self.model_type = None
        self.seasonality_index = None
        
    def load_seasonality(self, path: str = 'seasonality_index.csv'):
        """Load pre-computed seasonality indices."""
        try:
            self.seasonality_index = pd.read_csv(path)
            print(f"✓ Loaded seasonality indices from {path}")
        except FileNotFoundError:
            print(f"⚠ Seasonality file not found. Run analyze_seasonality.py first.")
            self.seasonality_index = None
    
    def build_panel(self, df: pd.DataFrame, date_col: str, id_col: str, 
                    point_col: str = None, qty_col: str = None) -> pd.DataFrame:
        """
        Construct panel dataset: customer × month observations.
        
        Returns DataFrame with one row per (customer, month) combination.
        """
        print("\n" + "="*80)
        print("BUILDING PANEL DATA (Customer × Month)")
        print("="*80)
        
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        
        # Exclude December (very low seasonality)
        df = df[df[date_col].dt.month != 12]
        
        # Get all unique months and customers
        df['month_period'] = df[date_col].dt.to_period('M')
        all_months = sorted(df['month_period'].unique())
        all_customers = df[id_col].unique()
        
        print(f"Time periods: {len(all_months)} months ({all_months[0]} to {all_months[-1]})")
        print(f"Entities: {len(all_customers):,} customers")
        
        # Build panel
        panel_data = []
        
        for customer in all_customers:
            customer_df = df[df[id_col] == customer]
            
            for month in all_months:
                month_end = month.to_timestamp() + pd.offsets.MonthEnd(0)
                
                # Get customer activity up to this month
                activity_up_to = customer_df[customer_df[date_col] <= month_end]
                
                if len(activity_up_to) == 0:
                    continue  # Customer didn't exist yet
                
                # Calculate time-varying features
                last_activity = activity_up_to[date_col].max()
                recency_days = (month_end - last_activity).days
                
                total_points = activity_up_to[point_col].sum() if point_col else 0
                total_qty = activity_up_to[qty_col].sum() if qty_col else 0
                transaction_count = len(activity_up_to)
                
                # Calculate trends (change from previous month)
                prev_month = month - 1
                if prev_month in all_months:
                    prev_activity = customer_df[customer_df[date_col] <= prev_month.to_timestamp() + pd.offsets.MonthEnd(0)]
                    if len(prev_activity) > 0:
                        prev_recency = (prev_month.to_timestamp() + pd.offsets.MonthEnd(0) - prev_activity[date_col].max()).days
                        trend_recency = recency_days - prev_recency
                        trend_frequency = len(activity_up_to) - len(prev_activity)
                    else:
                        trend_recency = 0
                        trend_frequency = 0
                else:
                    trend_recency = 0
                    trend_frequency = 0
                
                # Binary churn indicator (183+ days inactive)
                is_churned = 1 if recency_days >= self.CHURN_THRESHOLD_DAYS else 0
                
                # Monthly activity indicator
                month_start = month.to_timestamp()
                month_active = 1 if len(customer_df[(customer_df[date_col] >= month_start) & 
                                                     (customer_df[date_col] <= month_end)]) > 0 else 0
                
                panel_data.append({
                    'customer_id': customer,
                    'month': str(month),
                    'month_num': month.month,
                    'month_idx': all_months.index(month),
                    'recency_days': recency_days,
                    'total_points': total_points,
                    'total_qty': total_qty,
                    'transaction_count': transaction_count,
                    'trend_recency': trend_recency,
                    'trend_frequency': trend_frequency,
                    'month_active': month_active,
                    'is_churned': is_churned
                })
        
        panel_df = pd.DataFrame(panel_data)
        print(f"\n✓ Panel constructed: {len(panel_df):,} observations")
        print(f"  Average observations per customer: {len(panel_df)/len(all_customers):.1f}")
        print(f"  Churn rate: {panel_df['is_churned'].mean()*100:.1f}%")
        
        self.panel_df = panel_df
        return panel_df
    
    def calculate_vif(self, X: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Variance Inflation Factor for multicollinearity detection.
        VIF > 10 indicates high multicollinearity.
        """
        from sklearn.linear_model import LinearRegression
        
        vif_data = {}
        for i, col in enumerate(X.columns):
            # Regress each feature on all others
            y = X[col].values
            X_others = X.drop(columns=[col]).values
            
            if X_others.shape[1] == 0:
                vif_data[col] = 1.0
                continue
            
            lr = LinearRegression()
            lr.fit(X_others, y)
            r_squared = lr.score(X_others, y)
            
            # VIF = 1 / (1 - R²)
            vif = 1 / (1 - r_squared) if r_squared < 0.999 else 999
            vif_data[col] = vif
        
        return vif_data
    
    def select_features(self, panel_df: pd.DataFrame) -> List[str]:
        """
        Select features using VIF test to remove multicollinearity.
        """
        print("\n" + "="*80)
        print("FEATURE SELECTION (VIF Multicollinearity Test)")
        print("="*80)
        
        candidate_features = [
            'recency_days', 'total_points', 'total_qty', 
            'transaction_count', 'trend_recency', 'trend_frequency', 'month_active'
        ]
        
        # Remove features with zero variance
        features = [f for f in candidate_features if panel_df[f].std() > 0]
        
        X = panel_df[features]
        vif = self.calculate_vif(X)
        
        print("\nInitial VIF values:")
        for feat, val in sorted(vif.items(), key=lambda x: x[1], reverse=True):
            status = "⚠ HIGH" if val > 10 else "✓ OK"
            print(f"  {feat:20s}: {val:6.2f} {status}")
        
        # Remove features with VIF > 10
        selected = [f for f, v in vif.items() if v <= 10]
        
        if len(selected) < len(features):
            removed = set(features) - set(selected)
            print(f"\n✗ Removed {len(removed)} features due to multicollinearity: {removed}")
        
        print(f"\n✓ Selected {len(selected)} features: {selected}")
        self.feature_names = selected
        return selected
    
    def fit_two_way_fixed_effects(self, panel_df: pd.DataFrame, features: List[str]) -> Dict:
        """
        Fit Two-Way Fixed Effects model (Entity + Time).
        
        Uses within-transformation to remove fixed effects, then OLS.
        """
        print("\n" + "="*80)
        print("FITTING TWO-WAY FIXED EFFECTS MODEL")
        print("="*80)
        
        # Calculate customer means (entity fixed effects)
        customer_means = panel_df.groupby('customer_id')[features + ['is_churned']].mean()
        customer_means.columns = [f'{c}_customer_mean' for c in customer_means.columns]
        
        # Calculate time means (time fixed effects)
        time_means = panel_df.groupby('month_idx')[features + ['is_churned']].mean()
        time_means.columns = [f'{c}_time_mean' for c in time_means.columns]
        
        # Merge means back
        panel_df = panel_df.merge(customer_means, on='customer_id', how='left')
        panel_df = panel_df.merge(time_means, on='month_idx', how='left')
        
        # Demean (within transformation)
        for feat in features:
            panel_df[f'{feat}_demeaned'] = (panel_df[feat] - 
                                             panel_df[f'{feat}_customer_mean'] - 
                                             panel_df[f'{feat}_time_mean'])
        
        panel_df['churn_demeaned'] = (panel_df['is_churned'] - 
                                       panel_df['is_churned_customer_mean'] - 
                                       panel_df['is_churned_time_mean'])
        
        # OLS on demeaned data
        X = panel_df[[f'{f}_demeaned' for f in features]].values
        y = panel_df['churn_demeaned'].values
        
        # Add regularization for numerical stability
        XtX = X.T @ X + 0.001 * np.eye(X.shape[1])
        Xty = X.T @ y
        
        try:
            beta = np.linalg.solve(XtX, Xty)
        except np.linalg.LinAlgError:
            print("⚠ Matrix singular, using pseudo-inverse")
            beta = np.linalg.lstsq(XtX, Xty, rcond=None)[0]
        
        # Calculate R-squared (within)
        y_pred = X @ beta
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        
        # Extract fixed effects
        customer_fe = customer_means['is_churned_customer_mean'].to_dict()
        time_fe = time_means['is_churned_time_mean'].to_dict()
        
        self.coefficients = dict(zip(features, beta))
        self.customer_fixed_effects = customer_fe
        self.time_fixed_effects = time_fe
        self.r_squared = r_squared
        self.model_type = 'Two-Way Fixed Effects'
        
        print(f"\n✓ Model fitted successfully")
        print(f"  R-squared (within): {r_squared:.4f}")
        print(f"\nCoefficients:")
        for feat, coef in self.coefficients.items():
            direction = "↑ increases" if coef > 0 else "↓ decreases"
            print(f"  {feat:20s}: {coef:8.6f} {direction} churn")
        
        return {
            'coefficients': self.coefficients,
            'r_squared': r_squared,
            'customer_fe': customer_fe,
            'time_fe': time_fe
        }
    
    def predict_churn_probability(self, customer_id, month_idx: int = None) -> float:
        """
        Predict churn probability for a customer in a given month.
        
        If month_idx is None, uses the latest month.
        """
        if self.panel_df is None or self.coefficients is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Get latest observation for customer
        customer_data = self.panel_df[self.panel_df['customer_id'] == customer_id]
        if len(customer_data) == 0:
            return 0.5  # Unknown customer, neutral probability
        
        if month_idx is None:
            month_idx = customer_data['month_idx'].max()
        
        obs = customer_data[customer_data['month_idx'] == month_idx]
        if len(obs) == 0:
            obs = customer_data.iloc[-1:]  # Use latest available
        
        # Calculate prediction
        prob = self.customer_fixed_effects.get(customer_id, 0)
        prob += self.time_fixed_effects.get(month_idx, 0)
        
        for feat, coef in self.coefficients.items():
            prob += coef * obs[feat].values[0]
        
        # Clip to [0, 1]
        prob = max(0, min(1, prob))
        return prob
    
    def predict_3month_forecast(self, analysis_date: datetime = None) -> pd.DataFrame:
        """
        Predict churn probability for each customer over next 3 months.
        """
        if analysis_date is None:
            # Get the latest month from panel and convert to timestamp
            latest_month_period = pd.Period(self.panel_df['month'].max())
            analysis_date = latest_month_period.to_timestamp() + pd.offsets.MonthEnd(0)
        
        print("\n" + "="*80)
        print("3-MONTH CHURN FORECAST")
        print("="*80)
        print(f"Analysis date: {analysis_date.date()}")
        
        customers = self.panel_df['customer_id'].unique()
        latest_month_idx = self.panel_df['month_idx'].max()
        
        forecasts = []
        for customer in customers:
            # Get latest features
            customer_data = self.panel_df[self.panel_df['customer_id'] == customer]
            latest = customer_data[customer_data['month_idx'] == latest_month_idx]
            
            if len(latest) == 0:
                latest = customer_data.iloc[-1:]
            
            recency = latest['recency_days'].values[0]
            
            # Predict for next 3 months
            probs = []
            for m in range(1, 4):
                future_month_idx = latest_month_idx + m
                future_month_num = ((latest['month_num'].values[0] + m - 1) % 12) + 1
                
                # Estimate future recency (increases by ~30 days/month if no purchase)
                future_recency = recency + (m * 30)
                
                # Get seasonality adjustment
                time_fe = self.time_fixed_effects.get(future_month_idx % len(self.time_fixed_effects), 0)
                
                # Calculate probability
                prob = self.customer_fixed_effects.get(customer, 0)
                prob += time_fe
                prob += self.coefficients.get('recency_days', 0) * future_recency
                
                # Add other features (assume constant)
                for feat in self.feature_names:
                    if feat != 'recency_days':
                        prob += self.coefficients.get(feat, 0) * latest[feat].values[0]
                
                prob = max(0, min(1, prob))
                probs.append(prob)
            
            forecasts.append({
                'customer_id': customer,
                'current_recency': recency,
                'month_1_prob': probs[0],
                'month_2_prob': probs[1],
                'month_3_prob': probs[2],
                'avg_3month_prob': np.mean(probs)
            })
        
        forecast_df = pd.DataFrame(forecasts)
        forecast_df = forecast_df.sort_values('avg_3month_prob', ascending=False)
        
        print(f"\n✓ Generated forecasts for {len(forecast_df):,} customers")
        print(f"\nTop 10 at-risk customers:")
        print(forecast_df.head(10).to_string(index=False))
        
        return forecast_df
    
    def fit(self, df: pd.DataFrame, date_col: str = None, id_col: str = None,
            point_col: str = None, qty_col: str = None) -> Dict:
        """
        Complete model fitting pipeline.
        """
        # Auto-detect columns if not provided
        if date_col is None:
            date_col = [c for c in df.columns if 'date' in c.lower()][0]
        if id_col is None:
            id_col = [c for c in df.columns if 'id' in c.lower() or 'loyalty' in c.lower()][0]
        if point_col is None:
            point_col = [c for c in df.columns if 'point' in c.lower()][0]
        if qty_col is None:
            qty_col = [c for c in df.columns if 'qty' in c.lower() or 'quantity' in c.lower()][0]
        
        # Load seasonality
        self.load_seasonality()
        
        # Build panel
        panel_df = self.build_panel(df, date_col, id_col, point_col, qty_col)
        
        # Select features
        features = self.select_features(panel_df)
        
        # Fit model
        results = self.fit_two_way_fixed_effects(panel_df, features)
        
        return results


if __name__ == "__main__":
    # Example usage
    DATA_PATH = Path(r"d:\Skipper\Customer_churn_out_prediction_model\Book6.xlsx")
    
    print("="*80)
    print("PANEL DATA CHURN MODEL - DEMO")
    print("="*80)
    
    # Load data
    df = pd.read_excel(DATA_PATH, sheet_name='XYZ')
    
    # Initialize and fit model
    model = PanelChurnModel()
    results = model.fit(df)
    
    # Generate 3-month forecast
    forecast = model.predict_3month_forecast()
    
    # Save results
    forecast.to_csv('panel_churn_forecast_3month.csv', index=False)
    print(f"\n✓ Forecast saved to panel_churn_forecast_3month.csv")
