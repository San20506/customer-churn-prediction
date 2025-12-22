# Skipper Multi-Level Churn Prediction System
## Complete Project Report

**Project**: Customer Churn Prediction & Banking Forecast  
**Client**: Skipper Loyalty Program  
**Date**: December 16, 2025  
**Version**: 4.0

---

## Executive Summary

This report documents the complete development of a **multi-level customer churn prediction system** for the Skipper B2B plumber loyalty program. The system analyzes 6,546 plumbers across 169,111 transactions to predict churn risk and forecast banking points.

### Key Achievements

| Metric | Value |
|--------|-------|
| Customers Analyzed | 6,546 |
| Active Customers | 4,197 (64.1%) |
| Churned Customers | 2,349 (35.9%) |
| ML Model Accuracy | **68%** (validated) |
| Hypothesis Factors Confirmed | 4/4 (State, Retailer, Distributor, History) |

---

## 1. Project Overview

### 1.1 Business Problem

Skipper, a B2B plumbing parts distributor, operates a loyalty program where plumbers earn points for purchases. The business needed to:

1. **Identify at-risk customers** before they churn
2. **Understand what factors** drive churn (State, Retailer, Distributor, behavior)
3. **Predict future behavior** (churn and banking points) for the next 3 months
4. **Prioritize interventions** for sales team action

### 1.2 Data Source

| Attribute | Value |
|-----------|-------|
| File | `Plumber banking data Apr 24- Dec 25.xlsx` |
| Sheet | `XYZ` |
| Transactions | 169,111 |
| Customers | 6,546 |
| Date Range | April 1, 2024 - November 30, 2025 |

### 1.3 Churn Definition

A customer is considered **CHURNED** if they have not made a purchase in **183 days (6 months)**.

**Rationale**:
- B2B plumbers typically order supplies monthly or quarterly
- 6 months without purchase indicates likely switch to competitor
- Industry standard for distributor relationships

---

## 2. System Architecture

### 2.1 Multi-Level Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    MULTI-LEVEL CHURN SYSTEM                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LEVEL 1: RFM Analysis                                       │
│  ├── Recency scoring (1-5)                                   │
│  ├── Frequency scoring (1-5)                                 │
│  ├── Monetary scoring (1-5)                                  │
│  └── 9 customer segments                                     │
│                                                              │
│  LEVEL 2: Machine Learning                                   │
│  ├── Random Forest Classifier (churn)                        │
│  ├── Random Forest Regressor (banking points)               │
│  └── Accuracy: 68% (time-validated)                          │
│                                                              │
│  LEVEL 3: Survival Analysis                                  │
│  ├── Cox Proportional Hazards Model                          │
│  ├── Concordance Index: 0.918                                │
│  └── Predicts WHEN customer will churn                       │
│                                                              │
│  LEVEL 4: Multi-Factor Analysis                              │
│  ├── State patterns (p=0.000003)                             │
│  ├── Retailer patterns (p<0.000001)                          │
│  ├── Distributor patterns (p<0.001)                          │
│  └── Historical behavior (p=0.003)                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Application Tabs

| Tab | Purpose |
|-----|---------|
| 📊 Dashboard | Overview metrics and segment distribution |
| 🔬 Analytics | Multi-factor comparison (4 methods) |
| 🤖 ML Model | ML-based predictions with feature importance |
| 🎯 RFM | Recency/Frequency/Monetary analysis |
| 🚨 Priority | Prioritized action list |
| 📅 Forecast | 3-month seasonal forecast |
| 🌍 Geographic | State/Retailer/Distributor analysis |
| ⏰ Churned | Recently churned (win-back targets) |
| 📈 Drift | Behavior drift detection |
| ⏱️ Survival | Survival analysis |

---

## 3. Feature Engineering

### 3.1 Basic Features

| Feature | Calculation | Purpose |
|---------|-------------|---------|
| `recency` | Days since last purchase | How recently they bought |
| `frequency` | Count of transactions | How often they buy |
| `monetary` | Sum of points awarded | How much they spend |
| `tenure` | Days from first to last purchase | Relationship length |
| `avg_purchase_gap` | tenure / (frequency - 1) | Normal buying rhythm |

### 3.2 RFM Scoring

Each customer receives a score from **1 to 5** for each dimension:

| Score | Recency (Days) | Frequency (Orders) | Monetary (Points) |
|-------|----------------|--------------------| ------------------|
| 5 | 0-20 (Most recent) | 20+ orders | Top 20% |
| 4 | 21-50 | 10-19 orders | 60-80% |
| 3 | 51-100 | 5-9 orders | 40-60% |
| 2 | 101-150 | 2-4 orders | 20-40% |
| 1 | 151+ (Oldest) | 1 order | Bottom 20% |

**Combined RFM Score**: `R_score + F_score + M_score` (Range: 3-15)

### 3.3 Advanced Features

| Feature | Calculation | Purpose |
|---------|-------------|---------|
| `monthly_avg_points` | Sum(points last 6 months) / 6 | Average monthly banking |
| `trend` | (recent_3mo - prev_3mo) / prev_3mo | Banking trend direction |
| `state_churn_rate` | Churn rate of customer's state | State-level pattern |
| `retailer_churn_rate` | Churn rate of customer's retailer | Retailer-level pattern |
| `dist_churn_rate` | Churn rate of customer's distributor | Distributor pattern |
| `retailer_loyalty` | Primary retailer txns / total txns | Loyalty to primary retailer |

---

## 4. Multi-Factor Hypothesis Testing

### 4.1 Hypothesis

> **Hypothesis**: State, Retailer, Distributor, and Historical Behavior affect customer churn.

### 4.2 Statistical Tests Performed

#### State Factor

| Metric | Value |
|--------|-------|
| Test | Chi-Square |
| χ² Statistic | 35.71 |
| P-Value | 0.000003 |
| Degrees of Freedom | 6 |
| Cramér's V | 0.106 |
| Effect Size | Small but significant |
| **Result** | ✅ **SIGNIFICANT** |

#### Retailer Factor (Top 10)

| Metric | Value |
|--------|-------|
| Test | Chi-Square |
| P-Value | < 0.000001 |
| **Result** | ✅ **SIGNIFICANT** |

#### Distributor Factor

| Metric | Value |
|--------|-------|
| Test | Chi-Square |
| P-Value | < 0.001 |
| **Result** | ✅ **SIGNIFICANT** |

#### Historical Behavior

| Metric | Value |
|--------|-------|
| Test | T-test (purchase gap) |
| P-Value | 0.003 |
| **Result** | ✅ **SIGNIFICANT** |

### 4.3 Hypothesis Conclusion

**ALL 4 FACTORS ARE STATISTICALLY SIGNIFICANT**

| Factor | P-Value | Significant? | Importance |
|--------|---------|--------------|------------|
| State | 0.000003 | ✅ YES | ~2% |
| Retailer | <0.000001 | ✅ YES | ~10% |
| Distributor | <0.001 | ✅ YES | ~2% |
| Historical | 0.003 | ✅ YES | ~86% |

**Key Finding**: Historical behavior (86%) is the strongest predictor, but Retailer effects (10%) are also meaningful.

---

## 5. Machine Learning Models

### 5.1 Model Configuration

| Parameter | Value |
|-----------|-------|
| Algorithm | Random Forest |
| Trees | 100 |
| Max Depth | 10 |
| Random State | 42 |

### 5.2 Features Used

**Historical Features**:
- frequency, tenure, avg_gap, recency
- total_points, avg_points, points_std
- monthly_points, trend

**External Factors**:
- state_churn_rate, state_avg_points
- retailer_churn_rate, retailer_avg_points
- dist_churn_rate, dist_avg_points

### 5.3 Model Accuracy

#### ⚠️ Data Leakage Issue Discovered & Fixed

**Original Model**: 99.7% accuracy

**Problem**: The model used `recency` as a feature while `is_churned = recency >= 183` was the target. This is **circular logic**, not prediction.

**Corrected Model**: 68% accuracy (time-validated)

| Validation | Accuracy |
|------------|----------|
| Original (with leakage) | 99.7% ❌ |
| Fair (no recency feature) | 67.7% ✅ |
| Proper (time-based holdout) | ~68% ✅ |
| Industry Typical | 65-80% |

### 5.4 Feature Importance (Corrected Model)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | monthly_avg_points | 55.9% |
| 2 | trend | 25.1% |
| 3 | retailer_churn_rate | 10.0% |
| 4 | tenure | 3.2% |
| 5 | frequency | 1.8% |

---

## 6. State-Adjusted Thresholds

### 6.1 The Problem with Flat Thresholds

Different states have different buying patterns:

| State | Customers | Median Gap | Implied Threshold |
|-------|-----------|------------|-------------------|
| West Bengal | 2,965 | 6.8 days | 90 days |
| Assam | 220 | Higher | 90 days |
| Jharkhand | 9 | 120 days | 360 days |

**Issue**: Using 183-day flat threshold for West Bengal waits **27x** their normal gap!

### 6.2 State-Adjusted Threshold Formula

```python
state_threshold = median_purchase_gap * 3
# Clamped to 90-365 days
```

### 6.3 Combined Threshold (State + Retailer + Loyalty)

```python
combined_threshold = (retailer_loyalty × retailer_threshold) 
                   + ((1 - retailer_loyalty) × state_threshold)
```

Where:
- `retailer_loyalty` = transactions with primary retailer / total transactions
- High loyalty → uses retailer threshold more
- Low loyalty → uses state threshold more

---

## 7. Customer Segments

### 7.1 Segment Definitions

| Segment | Status | Criteria | Priority |
|---------|--------|----------|----------|
| AT_RISK_HIGH_VALUE | Active | F≥4, R≤2 (was loyal, now drifting) | 🔴 1 |
| AT_RISK | Active | F≥4, R≤3 (showing risk signs) | 🟡 2 |
| CHURNED_OUT_RECENTLY | Churned | 183-365 days | 🟠 3 |
| DORMANT | Active | R≤2, F≤2 (low engagement) | ⚫ 4 |
| MODERATE | Active | Average metrics | ⚪ 5 |
| ACTIVE | Active | R≥4, F≥3 (healthy) | 🟢 6 |
| NEW_OR_OCCASIONAL | Active | F≤2 (new customer) | 🔵 7 |
| CHURNED_OUT_LONG_TERM | Churned | 365+ days | ⚫ 8 |
| LOYAL_ACTIVE | Active | R=5, F≥4 (best customers) | 🌟 9 |

### 7.2 Current Distribution

| Segment | Count | Percentage |
|---------|-------|------------|
| Active (all) | 4,197 | 64.1% |
| Churned (all) | 2,349 | 35.9% |
| High Risk | 2,353 | 35.9% |
| Medium Risk | 1 | 0.0% |
| Low Risk | 4,192 | 64.0% |

---

## 8. 3-Month Forecast

### 8.1 Seasonality Indices

| Month | Index | Interpretation |
|-------|-------|----------------|
| January | 0.58 | Low season |
| February | 0.57 | Low season |
| March | 0.98 | Normal |
| April | 0.83 | Below average |
| May | 1.02 | Normal |
| June | 1.03 | Normal |
| July | 1.19 | High season |
| August | 1.34 | High season |
| September | 1.29 | High season |
| **October** | **1.64** | **PEAK** |
| November | 1.02 | Normal |
| **December** | **0.50** | **Low** |

### 8.2 Forecast Algorithm

```python
for each_month in next_3_months:
    base_prob = calculate_from_rfm_and_recency(customer)
    
    if seasonality_index > 1.0:  # Peak season
        adjusted_prob = base_prob / seasonality_index
    else:  # Low season
        adjusted_prob = base_prob
    
    adjusted_prob *= (1 + days_into_future / 365)
```

### 8.3 Predicted Output

- **High Risk Customers**: 2,353
- **Predicted Banking (3 months)**: 6,835,351 points

---

## 9. Drift Detection

### 9.1 What is Drift?

**Drift** occurs when a customer's purchase gap is **significantly longer** than their historical average.

### 9.2 Detection Method

```python
z_score = (current_gap - avg_purchase_gap) / std_deviation
is_drifting = z_score > 1.0
```

### 9.3 Severity Levels

| Z-Score | Severity | Action |
|---------|----------|--------|
| > 2.0 | HIGH | Call within 24 hours |
| 1.0-2.0 | MEDIUM | Email within 48 hours |
| < 1.0 | LOW | Monitor |

---

## 10. Win-Back Strategy

### 10.1 Recovery Phases

| Phase | Days | Discount | Channel | Recovery Rate |
|-------|------|----------|---------|---------------|
| 1 | 183-240 | 25-30% | Call + Email | 40% |
| 2 | 241-300 | 35-40% | Email + SMS | 30% |
| 3 | 301-365 | 40-50% | Final offer | 20% |
| 4 | 365+ | - | Low priority | <10% |

### 10.2 ROI Calculation

```
Campaign cost: ₹500-1,000 per customer
Recovery rate: 30-40%
Average LTV: ₹50,000

ROI = (0.35 × ₹50,000) / ₹750 = 23x return
```

---

## 11. Technical Implementation

### 11.1 File Structure

```
Customer_churn_out_prediction_model/
│
├── 📊 CORE APPLICATION
│   ├── churn_app_v3.py          # Main GUI (1,265 lines)
│   ├── multi_level_churn.py     # Core engine (1,430 lines)
│   ├── panel_churn_model.py     # Panel model
│   └── xgboost_churn.py         # XGBoost model
│
├── 📝 DOCUMENTATION
│   ├── README.md                
│   ├── COMPLETE_SYSTEM_DOCUMENTATION.md
│   └── docs/ (8 files)
│
├── 🔬 ANALYSIS
│   └── analysis/ (9 files)
│
└── 📤 OUTPUT
    └── output/ (11 files)
```

### 11.2 Dependencies

```
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.0.0
lifelines>=0.27.0
customtkinter>=5.0
openpyxl>=3.0
scipy>=1.9.0
```

### 11.3 Key Classes

| Class | Purpose |
|-------|---------|
| `MultiLevelChurnSystem` | Orchestrates all analysis |
| `RFMAnalyzer` | RFM scoring and segmentation |
| `DriftDetector` | Behavior drift detection |
| `SurvivalPredictor` | Cox survival analysis |
| `SeasonalChurnPredictor` | 3-month forecast |
| `GeographicChannelAnalyzer` | State/Retailer/Distributor analysis |
| `MultiFactorPredictionModel` | ML-based predictions |

---

## 12. Changes Made During Development

### 12.1 Feature Additions

| Date | Feature | Description |
|------|---------|-------------|
| - | RFM Analysis | Basic RFM scoring |
| - | ML Models | Logistic Regression + XGBoost |
| - | Survival Analysis | Cox PH Model |
| - | 3-Month Forecast | Seasonal predictions |
| - | Geographic Tab | State/Retailer/Distributor analysis |
| - | Multi-Factor Analysis | Hypothesis testing |
| - | ML Prediction Tab | Feature importance, risk distribution |
| - | Table Size Control | UI slider for readability |

### 12.2 Bug Fixes

| Issue | Fix |
|-------|-----|
| Syntax error in `predict_3months` | Added missing closing parenthesis |
| Excel export file dialog error | Changed `initialname` to `initialfile` |
| Null check errors in export | Added proper null checks |
| Data leakage in ML model | Removed recency from features, added time-based validation |

### 12.3 Model Accuracy Correction

| Before | After |
|--------|-------|
| 99.7% (fake) | 68% (validated) |

**Root Cause**: Using `recency` as a feature when it defines the target (`is_churned = recency >= 183`).

**Solution**: 
1. Removed recency from features
2. Used time-based validation (train on old, test on new)
3. Reported realistic accuracy

---

## 13. Conclusions

### 13.1 Key Findings

1. **All 4 hypothesized factors affect churn** (State, Retailer, Distributor, History)
2. **Historical behavior is the strongest predictor** (86% importance)
3. **Retailer effects matter** (10% importance)
4. **State-adjusted thresholds improve accuracy** for regional variations
5. **Realistic model accuracy is ~68%** (not 99.7%)

### 13.2 Business Recommendations

1. **Prioritize AT_RISK_HIGH_VALUE customers** for immediate intervention
2. **Use win-back campaigns** for recently churned (183-365 days)
3. **Consider state-specific thresholds** for more accurate predictions
4. **Monitor retailer churn rates** to identify problematic channels
5. **Expect 68% accuracy** when planning interventions

### 13.3 Next Steps

1. Integrate with CRM for automated alerts
2. A/B test intervention strategies
3. Track win-back campaign effectiveness
4. Refine thresholds based on actual outcomes

---

## Appendix: Export Files Generated

| File | Contents |
|------|----------|
| `multi_factor_predictions.xlsx` | All customer predictions |
| `state_hypothesis_test_results.xlsx` | State hypothesis test results |
| `geographic_channel_analysis.xlsx` | Geographic analysis |
| `multi_factor_churn_analysis.xlsx` | Multi-factor analysis |

---

**Report Generated**: December 16, 2025  
**System Version**: 4.0  
**Model Accuracy**: 68% (validated)
