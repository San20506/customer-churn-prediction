"""
Sample Data Generator
=====================
Generates synthetic customer transaction data for testing the churn prediction system.

Usage:
    python generate_sample.py
    
This creates a sample_transactions.xlsx file with realistic synthetic data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(
    n_customers: int = 1000,
    n_transactions: int = 15000,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-15"
) -> pd.DataFrame:
    """
    Generate synthetic transaction data.
    
    Args:
        n_customers: Number of unique customers
        n_transactions: Total number of transactions
        start_date: Start date for transactions
        end_date: End date for transactions
        
    Returns:
        DataFrame with synthetic transaction data
    """
    np.random.seed(42)
    random.seed(42)
    
    # Date range
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    date_range = (end - start).days
    
    # States
    states = ['California', 'Texas', 'Florida', 'New York', 'Illinois', 
              'Pennsylvania', 'Ohio', 'Georgia', 'Michigan', 'Arizona']
    
    # Channels
    channels = ['Retail', 'Online', 'Wholesale', 'Direct']
    
    # Generate customer profiles
    customers = []
    for i in range(1, n_customers + 1):
        # Customer behavior type
        behavior = np.random.choice(['loyal', 'occasional', 'churning', 'new'], 
                                    p=[0.3, 0.3, 0.2, 0.2])
        
        customers.append({
            'customer_id': 10000 + i,
            'state': random.choice(states),
            'channel': random.choice(channels),
            'behavior': behavior,
            'avg_frequency': {'loyal': 15, 'occasional': 5, 'churning': 8, 'new': 3}[behavior],
            'avg_points': np.random.randint(50, 300),
            'churn_recency': {'loyal': 20, 'occasional': 60, 'churning': 150, 'new': 30}[behavior]
        })
    
    customer_df = pd.DataFrame(customers)
    
    # Generate transactions
    transactions = []
    
    for _, cust in customer_df.iterrows():
        # Number of transactions for this customer
        n_txn = max(1, int(np.random.poisson(cust['avg_frequency'])))
        
        # Last transaction date (based on behavior)
        last_txn_offset = max(1, int(np.random.exponential(cust['churn_recency'])))
        last_txn_date = end - timedelta(days=min(last_txn_offset, date_range - 30))
        
        # Generate transaction dates
        for j in range(n_txn):
            # Random date before last transaction
            days_before = np.random.randint(0, min(date_range, (last_txn_date - start).days + 1))
            txn_date = last_txn_date - timedelta(days=days_before)
            
            # Points with some variance
            points = max(10, int(np.random.normal(cust['avg_points'], cust['avg_points'] * 0.3)))
            
            transactions.append({
                'CUSTOMER_ID': cust['customer_id'],
                'TRANSACTION_DATE': txn_date,
                'POINTS_AWARDED': points,
                'STATE': cust['state'],
                'CHANNEL': cust['channel'],
                'QUANTITY': np.random.randint(1, 10)
            })
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    df = df.sort_values('TRANSACTION_DATE').reset_index(drop=True)
    
    return df


def main():
    """Generate and save sample data."""
    print("Generating sample transaction data...")
    
    df = generate_sample_data(
        n_customers=1000,
        n_transactions=15000
    )
    
    # Save to Excel
    output_path = "sample_transactions.xlsx"
    df.to_excel(output_path, sheet_name='Transactions', index=False)
    
    print(f"✅ Generated {len(df):,} transactions for {df['CUSTOMER_ID'].nunique():,} customers")
    print(f"   Date range: {df['TRANSACTION_DATE'].min().date()} to {df['TRANSACTION_DATE'].max().date()}")
    print(f"   Saved to: {output_path}")
    
    # Summary stats
    print("\n📊 Summary:")
    print(f"   States: {df['STATE'].nunique()}")
    print(f"   Channels: {df['CHANNEL'].nunique()}")
    print(f"   Avg transactions per customer: {len(df) / df['CUSTOMER_ID'].nunique():.1f}")
    print(f"   Avg points per transaction: {df['POINTS_AWARDED'].mean():.1f}")


if __name__ == "__main__":
    main()
