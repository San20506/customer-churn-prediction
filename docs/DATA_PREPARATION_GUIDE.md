# Skipper Churn Prediction System
## Data Preparation Guide


---

## 1. Overview

This document provides instructions for preparing transaction data for the Skipper Customer Churn Prediction System. Proper data formatting ensures accurate analysis and actionable insights.

---

## 2. Data Requirements

### 2.1 File Format

| Requirement | Specification |
|-------------|---------------|
| File Type | Microsoft Excel (.xlsx) |
| Sheet Selection | Select the sheet containing transaction data when prompted |
| Encoding | UTF-8 (default Excel encoding) |

### 2.2 Required Columns

The following columns are **mandatory** for the system to function:

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `TRXN_DATE` | Date | Transaction date | 2024-01-15 |
| `MEMBERSHIP ID` | Integer | Unique customer identifier | 8583996292 |

### 2.3 Recommended Columns

The following columns enable full analysis capabilities:

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `POINT_AWARDED` | Integer | Transaction value (points/amount) | 150 |
| `QUANTITY` | Integer | Items purchased | 5 |
| `STATE` | Text | Customer state/region | West Bengal |
| `RETAILER CODE` | Text | Retailer identifier | RET001 |
| `DISTRIBUTOR CODE` | Integer | Distributor identifier | 101 |

---

## 3. Data Format Specifications

### 3.1 Date Format

| Accepted Formats | Example |
|------------------|---------|
| YYYY-MM-DD | 2024-01-15 |
| DD/MM/YYYY | 15/01/2024 |
| DD-MMM-YYYY | 15-Jan-2024 |

> **Note:** Ensure consistent date formatting across all records.

### 3.2 Customer ID

- Must be unique per customer
- No blank or null values permitted
- Numeric format recommended

### 3.3 Numeric Fields

- No currency symbols (₹, $)
- No thousand separators
- Decimal values acceptable for monetary fields

---

## 4. Sample Data Template

```
| TRXN_DATE  | MEMBERSHIP ID | STATE       | RETAILER CODE | DISTRIBUTOR CODE | QUANTITY | POINT_AWARDED |
|------------|---------------|-------------|---------------|------------------|----------|---------------|
| 2024-01-15 | 8583996292    | West Bengal | RET001        | 101              | 5        | 150           |
| 2024-01-20 | 8583996292    | West Bengal | RET001        | 101              | 3        | 90            |
| 2024-02-01 | 7425836190    | Assam       | RET002        | 102              | 10       | 300           |
```

---

## 5. Operating Procedure

### Step 1: Data Validation

Before uploading, verify:
- [ ] All required columns are present
- [ ] Date column contains valid dates only
- [ ] Customer ID column has no blank values
- [ ] Minimum 6 months of transaction history included

### Step 2: Launch Application

```
python churn_app_v3.py
```

### Step 3: Load Data

1. Click **Load Excel**
2. Select the prepared data file
3. Choose the appropriate sheet from the dropdown

### Step 4: Execute Analysis

1. Click **Run Analysis**
2. Wait for processing to complete (1-3 minutes)
3. Review results in the application tabs

### Step 5: Configure Settings (Optional)

Navigate to the **Settings** tab to customize:

| Setting | Description | Default |
|---------|-------------|---------|
| Seasonality Index | Monthly weights affecting 3-month forecast | Pre-calibrated values |
| Drift Z-Score | Sensitivity for drift detection | 1.0 |

**Seasonality Values:**
- Values > 1.0 = High season (lower churn expected)
- Values < 1.0 = Low season (higher churn expected)

You can **Load from CSV**, **Save to CSV**, or **Reset to Defaults**.

### Step 6: Export Results

1. Click **Export Results**
2. Select destination folder
3. Results are saved as an Excel workbook

---

## 6. Output Reference

### 6.1 Priority Classification

| Priority | Segment | Definition | Recommended Action |
|----------|---------|------------|-------------------|
| 1 | AT_RISK_HIGH_VALUE | Previously active customer showing disengagement | Immediate outreach |
| 2 | AT_RISK | Customer exhibiting early warning signs | Contact within 48 hours |
| 3 | CHURNED_RECENTLY | No activity for 6-12 months | Win-back campaign |
| 4-7 | Various | Standard engagement levels | Routine follow-up |
| 8 | CHURNED_LONG_TERM | No activity for 12+ months | Low priority |
| 9 | LOYAL_ACTIVE | Consistently engaged customer | Retention focus |

### 6.2 Export Sheets

| Sheet Name | Purpose |
|------------|---------|
| Priority_List | Action list sorted by urgency |
| Recently_Churned | Customers for win-back campaigns |
| RFM_Analysis | Complete customer scoring |
| Drift_Detection | Early warning indicators |

---

## 7. Troubleshooting

| Error Message | Cause | Resolution |
|---------------|-------|------------|
| "Could not find required columns" | Column naming mismatch | Rename columns per Section 2.2 |
| "Date parsing error" | Invalid date format | Standardize dates per Section 3.1 |
| "No transactions found" | Empty dataset or wrong sheet | Verify sheet selection |

---

## 8. Support

For technical assistance, contact the Business Intelligence team.

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | January 2026 | BI Team | Initial release |
