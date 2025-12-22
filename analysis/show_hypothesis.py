import pandas as pd

# Read and display results
print("="*70)
print("STATE HYPOTHESIS TEST RESULTS")
print("="*70)

# Test results
test = pd.read_excel('state_hypothesis_test_results.xlsx', sheet_name='Test_Results')
print("\n--- STATISTICAL TEST ---")
for _, row in test.iterrows():
    print(f"  {row['Metric']}: {row['Value']}")

# State stats
print("\n--- STATE BREAKDOWN ---")
stats = pd.read_excel('state_hypothesis_test_results.xlsx', sheet_name='State_Statistics')
print(f"\n{'State':<15} {'Custs':>8} {'Churn%':>8} {'MedGap':>8} {'MedFreq':>8}")
print("-"*55)
for _, r in stats.iterrows():
    print(f"{r['state']:<15} {r['customers']:>8,} {r['churn_pct']:>7.1f}% {r['median_gap']:>7.1f}d {r['median_freq']:>8.1f}")
