
import pandas as pd
import os

# File paths
results_file = r'd:\Skipper\Customer_churn_out_prediction_model\churn_analysis_results.xlsx'
banking_file = r'd:\Skipper\Customer_churn_out_prediction_model\Plumber banking data Apr 24- Dec 25.xlsx'
output_file = r'd:\Skipper\Customer_churn_out_prediction_model\retailer_risk_analysis.xlsx'

def analyze():
    print("Loading data...")
    try:
        df_results = pd.read_excel(results_file)
        df_banking = pd.read_excel(banking_file)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # Normalize columns
    df_results.columns = [c.strip() for c in df_results.columns]
    df_banking.columns = [c.strip() for c in df_banking.columns]
    
    # Rename for consistency if needed
    if 'MEMBERSHIP ID' in df_banking.columns and 'customer_id' not in df_banking.columns:
        df_banking.rename(columns={'MEMBERSHIP ID': 'customer_id'}, inplace=True)
        
    print(f"Results columns: {df_results.columns.tolist()}")
    print(f"Banking columns: {df_banking.columns.tolist()}")
    
    # Check Segments
    if 'segment' in df_results.columns:
        segments = df_results['segment'].unique()
        print(f"\nUnique Segments found: {segments}")
    else:
        print("No 'segment' column found in results.")
        return

    # Link Retailer and State to Plumbers (deduplicate banking data to get unique plumber-retailer links)
    # A plumber might be linked to multiple retailers. We need all unique links.
    if 'RETAILER CODE' in df_banking.columns and 'STATE' in df_banking.columns:
        linkage = df_banking[['customer_id', 'RETAILER CODE', 'STATE']].drop_duplicates()
    else:
        print("Required columns (RETAILER CODE, STATE) missing in banking data.")
        return

    # Merge results with linkage
    # specific plumber-retailer combinations
    merged = pd.merge(linkage, df_results, on='customer_id', how='left')
    
    # Filter out those without risk info (if any)
    merged = merged.dropna(subset=['segment'])

    # --- Data Cleaning for STATE ---
    # 1. Handle Nulls
    merged['STATE'] = merged['STATE'].fillna('Unknown')
    merged['STATE'] = merged['STATE'].astype(str) # Ensure all are strings for replacement
    
    # 2. Fix Uttar Pradesh variations
    # Replace 'UttarPradesh' (no space) with 'Uttar Pradesh' (standard)
    merged['STATE'] = merged['STATE'].replace({'UttarPradesh': 'Uttar Pradesh', 'nan': 'Unknown'})
    
    print(f"\nStates after cleaning: {merged['STATE'].unique()}")
    
    print(f"\nMerged data shape: {merged.shape}")

    # 1. Classify based on state
    print("\n--- Classification based on State ---")
    state_summary = merged.groupby(['STATE', 'segment'])['customer_id'].nunique().unstack(fill_value=0)

    print(state_summary)
    
    # 2. Flag retailers with > 5 plumbers linked for specific risks
    # User asked for "high risk, high risk high value customer"
    # match segments vaguely
    
    target_segments = []
    for seg in segments:
        seg_str = str(seg).upper()
        if 'HIGH RISK' in seg_str or 'AT RISK' in seg_str or 'HIGH_VALUE' in seg_str: # Broad match first
             target_segments.append(seg)
    
    # Refine target segments
    # We look for segments containing HIGH, RISK, VALUE as per user request
    chosen_segments = []
    for s in segments:
        s_str = str(s).upper()
        if 'HIGH' in s_str or 'RISK' in s_str: # Broader capture to check
            chosen_segments.append(s)
            
    print(f"\nPotential risk segments: {chosen_segments}")
    
    # Specific user request: "high risk, high risk high value customer"
    # Matches: "High Risk", "At Risk High Value" likely.
    target_segments = [s for s in chosen_segments if 'HIGH' in str(s).upper() or 'RISK' in str(s).upper()]
    # Actually, let's just take all segments that seem to imply risk or high value to be safe, then let user decide?
    # No, strict interpretation:
    # 1. High Risk
    # 2. High Risk High Value (likely AT_RISK_HIGH_VALUE)
    
    strict_segments = [s for s in segments if isinstance(s, str) and (
        s == 'AT_RISK_HIGH_VALUE' or 
        s == 'HIGH_RISK' or 
        s == 'High Risk' or
        s == 'CHURNED_OUT_RECENTLY' # Maybe?
        or ('RISK' in s.upper() and 'HIGH' in s.upper())
    )]
    
    print(f"Strictly selected segments: {strict_segments}")
    if not strict_segments:
        print("Warning: No strict segments found. Falling back to all 'Risk' segments.")
        strict_segments = [s for s in segments if isinstance(s, str) and 'RISK' in s.upper()]
    
    risk_plumbers = merged[merged['segment'].isin(strict_segments)]
    
    print(f"Number of risk plumbers found: {len(risk_plumbers)}")
    
    # Group by Retailer and count unique plumbers
    retailer_risk_counts = risk_plumbers.groupby(['RETAILER CODE', 'STATE'])['customer_id'].nunique().reset_index()
    retailer_risk_counts.columns = ['Retailer_Code', 'State', 'Risk_Plumber_Count']
    
    print("\nTop retailers by risk plumber count:")
    print(retailer_risk_counts.sort_values('Risk_Plumber_Count', ascending=False).head(10))
    
    # Filter > 5 (or 0 if none found > 5 just to show)
    flagged_retailers = retailer_risk_counts[retailer_risk_counts['Risk_Plumber_Count'] > 5].sort_values('Risk_Plumber_Count', ascending=False)
    
    if flagged_retailers.empty:
        print("\nNo retailers found with > 5 risk plumbers. Exporting all retailers with > 0 risk plumbers for review.")
        flagged_retailers = retailer_risk_counts[retailer_risk_counts['Risk_Plumber_Count'] > 0].sort_values('Risk_Plumber_Count', ascending=False)
    
    print(f"\nFinal Flagged Retailers count: {len(flagged_retailers)}")

    
    # Save outputs
    with pd.ExcelWriter(output_file) as writer:
        state_summary.to_excel(writer, sheet_name='State Classification')
        flagged_retailers.to_excel(writer, sheet_name='Flagged Retailers', index=False)
        merged.to_excel(writer, sheet_name='Full Data', index=False)
        
    print(f"\nAnalysis saved to {output_file}")

if __name__ == "__main__":
    analyze()
