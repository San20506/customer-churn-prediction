# API Reference

Complete reference for every class and public method in the churn prediction system.

## Quick Start

```python
from multi_level_churn import MultiLevelChurnSystem
import pandas as pd

# Load data
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# Run full analysis
system = MultiLevelChurnSystem(churn_threshold=183)
results = system.run(df)

# Get priority list
priority = system.get_priority_list()
```

---

## MultiLevelChurnSystem

Orchestrator that runs all analysis levels and merges results.

### Constructor

```python
MultiLevelChurnSystem(churn_threshold: int = 183)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `churn_threshold` | int | 183 | Days inactive before a customer is considered churned |

### Methods

#### `run(df) → dict`

Run the complete multi-level analysis pipeline.

**Parameters:**
- `df` (pd.DataFrame): Transaction data. Auto-detects columns by name pattern.

**Returns:** dict with keys:
- `'rfm'`: RFM analysis DataFrame
- `'drift'`: Drift detection DataFrame
- `'survival'`: Survival analysis results
- `'logistic'`: Logistic regression results
- `'churning_champions'`: At-risk high-value customers
- `'priority_list'`: Merged priority list

**Column auto-detection:** The system looks for columns containing these keywords:
- Date: `trxn_date`, `date`, `trxn`
- Customer ID: `membership`, `loyalty`, `id`, `customer`
- Points: `point_awarded`, `point`, `points`
- Quantity: `quantity`, `qty`
- State: `state`
- Retailer: `retailer`

#### `get_priority_list() → pd.DataFrame`

Get the merged priority list sorted by action_priority (1 = most urgent).

---

## RFMAnalyzer

Level 1: Recency, Frequency, Monetary analysis.

### Constructor

```python
RFMAnalyzer(churn_threshold: int = 183)
```

### Methods

#### `calculate_rfm(df, date_col=None, id_col=None, point_col=None, qty_col=None) → pd.DataFrame`

Calculate RFM scores for all customers.

**Returns:** DataFrame with columns:
- `customer_id`, `last_purchase`, `frequency`, `monetary`, `total_qty`
- `recency_days`, `avg_purchase_gap`
- `R_score`, `F_score`, `M_score`, `RFM_score`
- `is_churned`, `recently_churned`, `long_term_churned`
- `churn_timeline`, `segment`, `action_priority`

#### `get_at_risk_high_value() → pd.DataFrame`

Customers who were loyal (F≥4) but are now drifting (R≤2). Priority 1.

#### `get_at_risk() → pd.DataFrame`

All at-risk customers (AT_RISK_HIGH_VALUE + AT_RISK segments).

#### `get_recently_churned() → pd.DataFrame`

Customers churned 183-365 days ago. Win-back targets.

#### `get_churned_out() → pd.DataFrame`

All churned customers (183+ days inactive).

#### `get_churn_timeline_summary() → pd.DataFrame`

Summary of customer counts by churn timeline category.

---

## DriftDetector

Early warning system. Detects customers whose purchase gap is increasing.

### Constructor

```python
DriftDetector(threshold_std: float = 1.0)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `threshold_std` | float | 1.0 | Z-score threshold for drift flagging |

### Methods

#### `detect_drift(df, date_col=None, id_col=None) → pd.DataFrame`

**Returns:** DataFrame with columns:
- `customer_id`, `avg_purchase_gap`, `std_gap`, `current_gap`
- `z_score`, `is_drifting`, `drift_severity` (HIGH/MEDIUM/LOW)

**Requires:** At least 3 transactions per customer to detect drift.

---

## SurvivalPredictor

Level 3: Cox Proportional Hazards survival analysis.

### Constructor

```python
SurvivalPredictor()
```

### Methods

#### `fit(df, date_col=None, id_col=None, point_col=None, qty_col=None) → dict`

Fit the Cox model.

**Returns:** dict with keys:
- `'concordance'`: float (model quality, 0.5=random, 1.0=perfect)
- `'hazard_ratios'`: dict of feature → hazard ratio
- `'summary'`: lifelines summary DataFrame

#### `predict_survival_probability(customer_id=None) → pd.DataFrame`

Get survival probability curves. If `customer_id` is None, returns all customers.

#### `predict_median_survival_time() → pd.DataFrame`

Predict median days until churn for each customer.

---

## LogisticChurnModel

Interpretable churn prediction using logistic regression.

### Constructor

```python
LogisticChurnModel(churn_threshold: int = 183)
```

### Methods

#### `fit(df, date_col=None, id_col=None, point_col=None, qty_col=None) → dict`

Fit logistic regression model.

**Returns:** dict with keys:
- `'accuracy'`: float
- `'coefficients'`: dict of feature → coefficient (positive = increases churn)
- `'feature_importance'`: dict of feature → importance

#### `predict(df) → pd.DataFrame`

Predict churn probability for new data.

---

## ChurnPredictor (xgboost_churn.py)

XGBoost-based binary classifier.

### Constructor

```python
ChurnPredictor()
```

### Methods

#### `prepare_features(df, date_col, id_col, point_col=None, qty_col=None, analysis_date=None) → pd.DataFrame`

Extract per-customer features from transaction data.

**Returns:** DataFrame with columns: `customer_id`, `recency_days`, `frequency`, `total_points`, `total_qty`, `days_active`, `avg_points_per_txn`, `avg_qty_per_txn`, `txn_frequency`, `trend`, `months_since_start`

#### `create_labels(features_df, churn_threshold=60) → pd.DataFrame`

Add binary churn labels based on recency threshold.

#### `train(features_df, label_col='churned') → dict`

Train XGBoost classifier with train/test split and cross-validation.

**Returns:** dict with keys: `accuracy`, `roc_auc`, `cv_mean`, `cv_std`, `feature_importance`, `classification_report`

#### `predict(features_df) → pd.DataFrame`

Predict churn probability and risk level (LOW/MEDIUM/HIGH/CRITICAL).

#### `save_model(path)` / `load_model(path)`

Serialize/deserialize trained model to/from pickle file.

---

## PanelChurnModel (panel_churn_model.py)

Two-Way Fixed Effects panel data model (IIT Kanpur methodology).

### Constructor

```python
PanelChurnModel()
```

### Methods

#### `fit(df, date_col=None, id_col=None, point_col=None, qty_col=None) → dict`

Complete pipeline: build panel → select features (VIF) → fit model.

**Returns:** dict with keys: `coefficients`, `r_squared`, `customer_fe`, `time_fe`

#### `build_panel(df, date_col, id_col, point_col=None, qty_col=None) → pd.DataFrame`

Construct panel dataset (customer × month observations).

#### `select_features(panel_df) → list`

Remove features with VIF > 10 (multicollinearity).

#### `fit_two_way_fixed_effects(panel_df, features) → dict`

Fit entity + time fixed effects model using within-transformation + OLS.

#### `predict_churn_probability(customer_id, month_idx=None) → float`

Predict churn probability for one customer.

#### `predict_3month_forecast(analysis_date=None) → pd.DataFrame`

Generate 3-month churn forecast for all customers.

**Returns:** DataFrame with columns: `customer_id`, `current_recency`, `month_1_prob`, `month_2_prob`, `month_3_prob`, `avg_3month_prob`

---

## MultiFactorPredictionModel

Random Forest classifier with state/retailer/distributor pattern features.

### Constructor

```python
MultiFactorPredictionModel(churn_threshold: int = 183)
```

### Methods

#### `fit_and_predict(df) → dict`

Train models and generate predictions in one call.

**Returns:** dict with keys:
- `'predictions'`: DataFrame with `churn_prob`, `predicted_points`, `risk_level`
- `'feature_importance'`: DataFrame sorted by importance
- `'summary'`: dict with `total`, `high_risk`, `medium_risk`, `low_risk`, `accuracy`

---

## GeographicChannelAnalyzer

Identifies geographic and channel patterns in churn.

### Constructor

```python
GeographicChannelAnalyzer(churn_threshold: int = 183)
```

### Methods

#### `analyze(df) → dict`

**Returns:** dict with keys:
- `'state_analysis'`: DataFrame with churn rates by state
- `'channel_analysis'`: DataFrame with churn rates by channel
- `'insights'`: list of insight dicts with `type`, `severity`, `message`, `action`
- `'overall_churn_rate'`: float

---

## StateAdjustedChurnAnalyzer

Adapts churn threshold per state based on local buying patterns.

### Constructor

```python
StateAdjustedChurnAnalyzer(flat_threshold: int = 183, multiplier: float = 3.0)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `flat_threshold` | int | 183 | Global default threshold |
| `multiplier` | float | 3.0 | Multiplier on state median gap |

### Methods

#### `analyze(df) → dict`

**Returns:** dict with keys:
- `'customer_data'`: DataFrame with both flat and adjusted churn flags
- `'state_patterns'`: DataFrame with state-level thresholds
- `'comparison'`: DataFrame comparing flat vs adjusted rates
- `'summary'`: dict with counts and rates

---

## MultiFactorChurnAnalyzer

Combined analysis considering state, retailer, and customer-retailer relationship.

### Constructor

```python
MultiFactorChurnAnalyzer(flat_threshold: int = 183, multiplier: float = 3.0)
```

### Methods

#### `analyze(df) → dict`

**Returns:** dict with keys:
- `'customer_data'`: DataFrame with flat, state, retailer, and combined churn flags
- `'state_patterns'`: State-level thresholds
- `'retailer_patterns'`: Retailer-level thresholds
- `'summary'`: Churn counts by method

---

## Utility Functions (churn_utils.py)

### `fast_rfm_calculate(df, date_col, id_col, point_col=None, churn_threshold=183) → pd.DataFrame`

Vectorized RFM calculation. 10x faster than per-customer loops. Same output schema as `RFMAnalyzer.calculate_rfm()`.

### `fast_customer_features(df, date_col, id_col, point_col=None, analysis_date=None) → pd.DataFrame`

Extract ML features using vectorized operations. Returns: `customer_id`, `first_purchase`, `last_purchase`, `frequency`, `avg_gap`, `gap_std`, `max_gap`, `total_points`, `avg_points`, `points_std`, `recency`, `tenure`, `purchase_velocity`, `trend`.

### `calculate_churn_probabilities(features_df, churn_threshold=183) → pd.DataFrame`

Heuristic churn probabilities based on recency and behavior. Use when ML model is not available. Adds `base_prob`, `churn_prob`, `risk_level`.

### `get_seasonality_factors() → dict`

Cached seasonality index by month (1-12). Based on historical banking patterns.

---

## Data Format

Your Excel file should have these columns (column names are auto-detected):

| Required | Column Keywords | Example |
|----------|----------------|---------|
| Yes | `trxn_date`, `date` | 2024-01-15 |
| Yes | `membership`, `loyalty`, `id` | 8583996292 |
| Optional | `point_awarded`, `points` | 150 |
| Optional | `quantity`, `qty` | 10 |
| Optional | `state` | Tamil Nadu |
| Optional | `retailer` | Retailer A |
| Optional | `distributor` | Distributor X |

Multiple keyword matches are tried in order. First match wins.
