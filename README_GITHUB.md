# Customer Churn Prediction

Multi-level customer churn prediction system using RFM analysis, machine learning, and survival analysis.

## 🎯 Overview

A comprehensive churn analysis system that predicts which customers are at risk of churning and forecasts their behavior for the next 3 months.

**Key Features:**
- RFM Analysis (Recency, Frequency, Monetary scoring)
- Machine Learning models (Random Forest, XGBoost, Logistic Regression)
- Survival Analysis (Cox Proportional Hazards)
- Geographic/Channel impact analysis
- Interactive desktop application

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MULTI-LEVEL CHURN SYSTEM                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LEVEL 1: RFM Analysis                                      │
│  ├── Recency, Frequency, Monetary scoring                   │
│  └── Customer segmentation (9 segments)                     │
│                                                             │
│  LEVEL 2: Machine Learning                                  │
│  ├── Random Forest Classifier (churn prediction)           │
│  ├── XGBoost (high-performance prediction)                 │
│  └── Logistic Regression (interpretable coefficients)      │
│                                                             │
│  LEVEL 3: Survival Analysis                                 │
│  ├── Cox Proportional Hazards Model                        │
│  └── Predicts WHEN customer will churn                     │
│                                                             │
│  LEVEL 4: Multi-Factor Analysis                             │
│  ├── Geographic patterns                                    │
│  ├── Channel patterns                                       │
│  └── Statistical significance testing                       │
│                                                             │
│  OUTPUT: 3-Month Forecast + Priority List + Risk Scores     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/San20506/customer-churn-prediction.git
cd customer-churn-prediction

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python churn_app_v3.py
```

1. Click "📂 Load Excel" and select your data file
2. Choose the appropriate sheet
3. Click "🚀 Run Analysis"
4. Explore the analysis tabs and export results

### Using the Core Library

```python
from multi_level_churn import MultiLevelChurnSystem
import pandas as pd

# Load your data
df = pd.read_excel('your_data.xlsx')

# Run analysis
system = MultiLevelChurnSystem(churn_threshold=90)
results = system.run(df)

# Get priority list
priority = system.get_priority_list()
print(priority.head(20))
```

## 📁 Project Structure

```
customer-churn-prediction/
│
├── churn_app_v3.py          # Main GUI application
├── multi_level_churn.py     # Core analysis engine
├── churn_utils.py           # Vectorized utilities (fast)
├── xgboost_churn.py         # XGBoost model
├── panel_churn_model.py     # Panel data model
│
├── analysis/                # Analysis scripts
│   ├── validate_model.py    # Model validation
│   └── analyze_multi_factor.py
│
├── docs/                    # Documentation
│   ├── EXCEL_DATA_DICTIONARY.md
│   └── CHURN_LOGIC_FIX.md
│
├── sample_data/             # Sample data generator
│   └── generate_sample.py
│
└── requirements.txt
```

## 📈 Data Format

Your Excel file should have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Customer ID | Unique identifier | 12345 |
| Transaction Date | Date of purchase | 2024-01-15 |
| Points/Amount | Transaction value | 150 |
| State (optional) | Geographic region | California |
| Channel (optional) | Sales channel | Retail |

## 🎯 Churn Definition

A customer is considered **churned** if they have not made a purchase in **90+ days** (configurable).

**Risk Levels:**
- **CRITICAL**: 70%+ churn probability
- **HIGH**: 50-70% probability
- **MEDIUM**: 30-50% probability
- **LOW**: <30% probability

## 📱 Application Tabs

| Tab | Purpose |
|-----|---------|
| 📊 Dashboard | Overview metrics and KPIs |
| 🔬 Analytics | Multi-factor analysis |
| 🤖 ML Model | ML predictions with feature importance |
| 🎯 RFM | Recency/Frequency/Monetary analysis |
| 🚨 Priority | Prioritized action list |
| 📅 Forecast | 3-month seasonal forecast |

## 🔬 Model Performance

| Model | Accuracy | Use Case |
|-------|----------|----------|
| Random Forest | ~68% | General prediction |
| XGBoost | ~70% | High-performance |
| Logistic Regression | ~65% | Interpretability |
| Survival Analysis | N/A | Time-to-churn prediction |

## 📦 Dependencies

- pandas >= 1.5.0
- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- xgboost >= 1.7.0
- lifelines >= 0.27.0
- customtkinter >= 5.0.0
- openpyxl >= 3.0.0

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**San20506** - [GitHub Profile](https://github.com/San20506)
