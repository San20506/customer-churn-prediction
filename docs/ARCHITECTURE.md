# Architecture

How the multi-level churn system fits together.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      CHURN APP v3 (GUI)                         │
│                    churn_app_v3.py                               │
│         CustomTkinter desktop application                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              MULTI-LEVEL CHURN SYSTEM                     │  │
│  │              multi_level_churn.py                          │  │
│  │                                                           │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │ LEVEL 1     │  │ LEVEL 2      │  │ LEVEL 3         │  │  │
│  │  │ RFM Scoring │  │ ML Models    │  │ Survival        │  │  │
│  │  │             │  │              │  │                 │  │  │
│  │  │ Recency     │  │ Random       │  │ Cox PH Model    │  │  │
│  │  │ Frequency   │  │ Forest       │  │                 │  │  │
│  │  │ Monetary    │  │ XGBoost      │  │ Predicts WHEN   │  │  │
│  │  │ Segments    │  │ Log. Reg.    │  │ customer churns │  │  │
│  │  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘  │  │
│  │         │                │                    │           │  │
│  │  ┌──────┴──────┐  ┌──────┴───────┐  ┌────────┴────────┐  │  │
│  │  │ Drift       │  │ Multi-Factor │  │ Geographic      │  │  │
│  │  │ Detection   │  │ Prediction   │  │ Analysis        │  │  │
│  │  │             │  │              │  │                 │  │  │
│  │  │ Z-score     │  │ State/Retail │  │ State thresholds│  │  │
│  │  │ gap analysis│  │ patterns     │  │ Channel impact  │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ PANEL MODEL      │  │ UTILITIES        │                     │
│  │ panel_churn_     │  │ churn_utils.py   │                     │
│  │ model.py         │  │                  │                     │
│  │                  │  │ Vectorized RFM   │                     │
│  │ Two-Way Fixed    │  │ Feature extract  │                     │
│  │ Effects          │  │ Heuristic probs  │                     │
│  │ 3-month forecast │  │ Seasonality      │                     │
│  └──────────────────┘  └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Excel File (.xlsx)
       │
       ▼
┌──────────────┐
│ Load & Parse  │  Auto-detects columns (date, id, points, state, retailer)
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│            MULTI-LEVEL CHURN SYSTEM               │
│                                                   │
│  ┌─────────────┐                                  │
│  │ RFM Scoring │ ◄─── Drift Detection             │
│  │ (Level 1)   │      (z-score gap analysis)      │
│  └──────┬──────┘                                  │
│         │                                         │
│         ▼                                         │
│  ┌─────────────┐  ┌──────────────┐                │
│  │ ML Models   │  │ Survival     │                │
│  │ (Level 2)   │  │ (Level 3)    │                │
│  └──────┬──────┘  └──────┬───────┘                │
│         │                │                        │
│         ▼                ▼                        │
│  ┌─────────────────────────────┐                  │
│  │ Geographic / Multi-Factor   │                  │
│  │ Analysis                    │                  │
│  └──────────┬──────────────────┘                  │
│             │                                     │
│             ▼                                     │
│  ┌─────────────────────────────┐                  │
│  │ PRIORITY LIST               │                  │
│  │ (Merged, sorted by urgency) │                  │
│  └─────────────────────────────┘                  │
└──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ GUI / Export  │  Dashboard, Analytics, ML, RFM, Priority, Forecast, Geo,
│               │  Recently Churned, Drift, Survival, Settings
└──────────────┘
```

## Churn Definition

A customer is **churned** when they have not made a purchase in `churn_threshold` days (default: 183 days / 6 months).

### Timeline Categories

| Category | Days Inactive | Meaning |
|----------|--------------|---------|
| ACTIVE | 0-182 | Still buying |
| CHURNED_OUT_RECENTLY | 183-365 | Win-back opportunity (30-40% recovery) |
| CHURNED_OUT_LONG_TERM | 365+ | Low priority (<10% recovery) |

### RFM Segments (for active customers)

| Segment | Condition | Priority | Action |
|---------|-----------|----------|--------|
| AT_RISK_HIGH_VALUE | F≥4, R≤2, <183 days | 1 (highest) | Call immediately |
| AT_RISK | F≥4, R≤3, <183 days | 2 | Outreach within 48h |
| DORMANT | R≤2, F≤2 | 4 | Re-engagement campaign |
| MODERATE | Default | 5 | Standard retention |
| ACTIVE | R≥4, F≥3 | 6 | Maintain |
| NEW_OR_OCCASIONAL | F≤2 | 7 | Nurture |
| LOYAL_ACTIVE | R=5, F≥4 | 9 (lowest) | Maintain |

## Model Descriptions

### Level 1: RFM Analysis (`RFMAnalyzer`)

Classical RFM scoring. Segments customers into actionable groups based on:
- **Recency**: Days since last purchase
- **Frequency**: Total transaction count
- **Monetary**: Total points/value earned

Scores are quintile-based (1-5). Combined RFM score = R + F + M (range 3-15).

### Level 2: ML Models

**Random Forest** (`MultiFactorPredictionModel`): Tree ensemble. Handles non-linear relationships. Provides feature importance. ~68% accuracy on holdout.

**XGBoost** (`ChurnPredictor` in `xgboost_churn.py`): Gradient-boosted trees. Higher accuracy (~70%). Supports model serialization (save/load pickle).

**Logistic Regression** (`LogisticChurnModel`): Interpretable coefficients. Answers "what factors drive churn?" Lower accuracy (~65%) but actionable insights.

### Level 3: Survival Analysis (`SurvivalPredictor`)

Cox Proportional Hazards model. Predicts **when** a customer will churn, not just **if**. Outputs:
- Concordance index (model quality)
- Hazard ratios (risk factors)
- Median survival time per customer

### Panel Data Model (`PanelChurnModel`)

Two-Way Fixed Effects regression (IIT Kanpur methodology):
- Entity fixed effects (customer-specific baseline risk)
- Time fixed effects (monthly seasonality)
- VIF multicollinearity testing
- 3-month seasonal forecast

### Drift Detection (`DriftDetector`)

Statistical early warning system. Detects customers whose purchase gap is increasing:
- Calculates z-score: (current_gap - avg_gap) / std_gap
- z > 1.0 = MEDIUM drift, z > 2.0 = HIGH drift
- Catches problems **before** churn threshold is reached

### Geographic Analysis (`GeographicChannelAnalyzer`)

Identifies location and channel patterns in churn:
- State-level churn rates
- Channel (retailer) impact analysis
- Statistical significance testing
- Actionable insights per region

### State-Adjusted Thresholds (`StateAdjustedChurnAnalyzer`)

Different regions have different buying rhythms. Instead of a flat 183-day threshold:
- Calculates median purchase gap per state
- Sets threshold = 3x median gap (clamped 90-365)
- Compares flat vs adjusted classification

## GUI Architecture

The desktop app (`churn_app_v3.py`) uses CustomTkinter with 11 tabs:

| Tab | Source Component | Purpose |
|-----|-----------------|---------|
| Dashboard | All | Overview metrics and KPIs |
| Analytics | MultiFactorChurnAnalyzer | Multi-factor analysis |
| ML Model | MultiFactorPredictionModel | Predictions with feature importance |
| RFM | RFMAnalyzer | Recency/Frequency/Monetary |
| Priority | MultiLevelChurnSystem | Prioritised action list |
| Forecast | PanelChurnModel | 3-month seasonal forecast |
| Geographic | GeographicChannelAnalyzer | State/channel patterns |
| Churned | RFMAnalyzer | Recently churned (183-365 days) |
| Drift | DriftDetector | Purchase gap warnings |
| Survival | SurvivalPredictor | Cox model time-to-churn |
| Settings | Config | Seasonality, thresholds |

## File Structure

```
customer-churn-prediction/
├── multi_level_churn.py     # Core engine (1470 lines)
│   ├── RFMAnalyzer          # Level 1: RFM scoring
│   ├── DriftDetector        # Early warning system
│   ├── SurvivalPredictor    # Level 3: Cox PH model
│   ├── LogisticChurnModel   # Interpretable ML
│   ├── SeasonalChurnPredictor  # 3-month forecast
│   ├── GeographicChannelAnalyzer  # Location patterns
│   ├── StateAdjustedChurnAnalyzer # Adaptive thresholds
│   ├── MultiFactorChurnAnalyzer   # Combined factors
│   ├── MultiFactorPredictionModel # Random Forest
│   └── MultiLevelChurnSystem      # Orchestrator
│
├── churn_app_v3.py          # Desktop GUI (1528 lines)
├── xgboost_churn.py         # XGBoost model
├── panel_churn_model.py     # Panel data model
├── churn_utils.py           # Vectorized utilities
│
├── docs/
│   ├── API.md               # This file's companion
│   ├── ARCHITECTURE.md      # This file
│   └── EXCEL_DATA_DICTIONARY.md  # Export format docs
│
├── analysis/
│   ├── validate_model.py    # Model validation
│   └── analyze_multi_factor.py
│
├── sample_data/
│   └── generate_sample.py   # Test data generator
│
├── requirements.txt
└── README.md
```
