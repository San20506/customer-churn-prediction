
# Retailer Risk Analysis Summary (Updated)

**Date**: 2025-12-17
**Source Files**:
- `churn_analysis_results.xlsx`
- `Plumber banking data Apr 24- Dec 25.xlsx`

## Data Cleaning Updates
1. **Null States**: Entries with missing state information are now labeled as `Unknown`.
2. **State Normalization**: Corrected variations like `UttarPradesh` to the standard `Uttar Pradesh`.

## 1. Classification by State
A summary of customer segments broken down by state (including Unknown) is available in the `State Classification` sheet.

## 2. Retailer Flagging
We identified retailers with **more than 5** linked plumbers falling into High Risk categories.

**Risk Categories Included**:
- High Risk
- At Risk
- At Risk High Value
- Churned Out Recently

**Findings**:
- **49 Retailers** were flagged as having > 5 risk plumbers (increased from 32 after cleaning state data and potentially capturing more links).
- The top retailer (`RMA1903000798`) has **19** linked risk plumbers.

## Output
The detailed analysis is saved in:
`d:\Skipper\Customer_churn_out_prediction_model\retailer_risk_analysis.xlsx`
