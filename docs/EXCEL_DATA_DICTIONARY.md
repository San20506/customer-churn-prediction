# Excel Export Data Dictionary

## 📊 Complete Guide to All Excel Sheets and Parameters

This document explains every parameter in the exported Excel file, what it means, and why it's important for your business.

---

## 📋 Sheet 1: Priority_List

**Purpose**: Master list of all customers sorted by action priority

### Columns

| Column | Description | Why It's Important | Example |
|--------|-------------|-------------------|---------|
| **customer_id** | Unique customer identifier (Loyalty ID) | Track individual customers | 8583996292 |
| **segment** | Customer category based on behavior | Determines action strategy | AT_RISK_HIGH_VALUE |
| **action_priority** | Urgency ranking (1=highest) | Who to contact first | 1 |
| **recency_days** | Days since last purchase | Shows engagement level | 248 |
| **frequency** | Total number of orders | Indicates loyalty | 16 |
| **RFM_score** | Combined score (3-15 scale) | Overall customer value | 9 |
| **is_drifting** | Purchase gap increasing? | Early warning sign | True |

### Segment Meanings

| Segment | Status | Days | Priority | Action Required |
|---------|--------|------|----------|-----------------|
| **AT_RISK_HIGH_VALUE** | Active | 0-182 | 🔴 1 | **CALL IMMEDIATELY** - Was loyal, now drifting |
| **AT_RISK** | Active | 0-182 | 🟡 2 | Proactive outreach within 48 hours |
| **CHURNED_OUT_RECENTLY** | Churned | 183-365 | 🟠 3 | Win-back campaign (30-40% success) |
| **DORMANT** | Active | 0-182 | ⚫ 4 | Re-engagement email campaign |
| **MODERATE** | Active | 0-182 | ⚪ 5 | Standard retention program |
| **ACTIVE** | Active | 0-182 | 🟢 6 | Maintain current relationship |
| **NEW_OR_OCCASIONAL** | Active | 0-182 | 🔵 7 | Nurture into regular customer |
| **CHURNED_OUT_LONG_TERM** | Churned | 365+ | ⚫ 8 | Low priority (< 10% recovery) |
| **LOYAL_ACTIVE** | Active | 0-182 | 🌟 9 | Already excellent - maintain |

### How to Use This Sheet

1. **Sort by action_priority** (already done)
2. **Filter segment = 'AT_RISK_HIGH_VALUE'** → Call these customers TODAY
3. **Check is_drifting = True** → Purchase gap is increasing
4. **High frequency + High recency_days** = Urgent intervention needed

---

## 📋 Sheet 2: Recently_Churned_183-365

**Purpose**: Customers who churned 183-365 days ago - WIN-BACK TARGETS

### Columns

| Column | Description | Why It's Important | Typical Value |
|--------|-------------|-------------------|---------------|
| **customer_id** | Loyalty ID | Track win-back success | 8583996292 |
| **recency_days** | Days since last purchase | Time in churn window | 248 |
| **frequency** | Historical order count | Shows past loyalty | 16 |
| **R_score** | Recency score (1-5, 1=worst) | How long they've been gone | 1 |
| **F_score** | Frequency score (1-5, 5=best) | How loyal they were | 4 |
| **M_score** | Monetary score (1-5, 5=best) | How valuable they were | 4 |
| **segment** | Always 'CHURNED_OUT_RECENTLY' | Confirms churn status | CHURNED_OUT_RECENTLY |
| **churn_timeline** | Same as segment | Timeline category | CHURNED_OUT_RECENTLY |
| **last_purchase** | Date of last order | When they stopped | 2024-04-10 |
| **total_points** | Lifetime points earned | Total value | 15,000 |
| **total_qty** | Lifetime quantity purchased | Purchase volume | 250 |
| **avg_purchase_gap** | Average days between orders | Normal buying pattern | 21.5 |

### Win-Back Strategy by Recency

| Days Since Last Purchase | Phase | Discount | Expected Recovery |
|-------------------------|-------|----------|-------------------|
| 183-240 | Phase 1 | 25-30% | 40% |
| 241-300 | Phase 2 | 35-40% | 30% |
| 301-365 | Phase 3 | 40-50% | 20% |

### How to Use This Sheet

1. **Sort by F_score (descending)** → Target high-frequency customers first
2. **Filter recency_days 183-240** → Phase 1 win-back (best chance)
3. **Check avg_purchase_gap** → Personalize "We miss you" message
4. **Use total_points** → Offer bonus points incentive

**ROI**: ₹500-1,000 campaign cost × 30-40% recovery × ₹50,000 LTV = **15-30× ROI**

---

## 📋 Sheet 3: RFM_Analysis

**Purpose**: Complete RFM scoring for all customers

### Columns

| Column | Description | Formula | Why It's Important |
|--------|-------------|---------|-------------------|
| **customer_id** | Loyalty ID | - | Unique identifier |
| **last_purchase** | Date of last order | MAX(transaction_date) | Recency calculation |
| **frequency** | Total orders | COUNT(transactions) | Loyalty indicator |
| **monetary** | Total points earned | SUM(points) | Customer value |
| **total_qty** | Total items purchased | SUM(quantity) | Purchase volume |
| **recency_days** | Days since last purchase | TODAY - last_purchase | Engagement metric |
| **avg_purchase_gap** | Average days between orders | AVG(days between orders) | Buying pattern |
| **R_score** | Recency score (1-5) | Quintile ranking | 5=most recent, 1=oldest |
| **F_score** | Frequency score (1-5) | Quintile ranking | 5=most frequent, 1=least |
| **M_score** | Monetary score (1-5) | Quintile ranking | 5=highest value, 1=lowest |
| **RFM_score** | Combined score (3-15) | R + F + M | Overall customer value |
| **segment** | Behavioral category | RFM + recency logic | Action strategy |
| **action_priority** | Urgency ranking (1-9) | Based on segment | Contact order |
| **is_churned** | Churned flag (True/False) | recency_days >= 183 | Churn status |
| **recently_churned** | Recently churned flag | 183 <= days <= 365 | Win-back target |
| **long_term_churned** | Long-term churned flag | days > 365 | Low priority |
| **churn_timeline** | Timeline category | Based on recency_days | ACTIVE/CHURNED_OUT_RECENTLY/CHURNED_OUT_LONG_TERM |

### RFM Score Interpretation

| RFM Score | Customer Type | Action |
|-----------|---------------|--------|
| 13-15 | **Champions** | Reward, upsell, cross-sell |
| 10-12 | **Loyal** | Maintain, appreciate |
| 7-9 | **Potential** | Engage, educate |
| 4-6 | **At Risk** | Re-engage, special offers |
| 3 | **Lost** | Win-back or ignore |

### How to Use This Sheet

1. **Pivot by segment** → See distribution
2. **Filter RFM_score >= 10** → High-value customers
3. **Sort by recency_days (descending)** → Find drifting customers
4. **Compare avg_purchase_gap to recency_days** → Detect anomalies

---

## 📋 Sheet 4: Drift_Detection

**Purpose**: Customers whose purchase gap is increasing (early warning)

### Columns

| Column | Description | Formula | Why It's Important |
|--------|-------------|---------|-------------------|
| **customer_id** | Loyalty ID | - | Track drifting customers |
| **avg_purchase_gap** | Normal days between orders | AVG(historical gaps) | Baseline pattern |
| **std_gap** | Standard deviation of gaps | STDEV(historical gaps) | Pattern variability |
| **current_gap** | Days since last purchase | TODAY - last_purchase | Current status |
| **z_score** | Statistical drift measure | (current - avg) / std | Drift severity |
| **is_drifting** | Drifting flag | z_score > 1.0 | Action trigger |
| **drift_severity** | Severity level | Based on z_score | HIGH/MEDIUM/LOW |

### Z-Score Interpretation

| Z-Score | Meaning | Action |
|---------|---------|--------|
| > 2.0 | **HIGH** - 2+ std deviations | Call within 24 hours |
| 1.0-2.0 | **MEDIUM** - 1-2 std deviations | Email within 48 hours |
| < 1.0 | **LOW** - Within normal range | Monitor |

### Example

```
Customer: 8583996292
avg_purchase_gap: 21 days (normally buys every 3 weeks)
current_gap: 63 days (hasn't bought in 9 weeks)
z_score: 2.8 (HIGH severity)
→ ACTION: Call immediately - something changed!
```

### How to Use This Sheet

1. **Sort by z_score (descending)** → Highest drift first
2. **Filter drift_severity = 'HIGH'** → Urgent cases
3. **Compare current_gap to avg_purchase_gap** → See deviation
4. **Cross-reference with RFM** → Prioritize high-value drifters

**Why This Matters**: Drift detection catches problems BEFORE customers churn. A customer who normally buys every 20 days but hasn't bought in 60 days is likely switching to a competitor.

---

## 📋 Sheet 5: At_Risk_High_Value

**Purpose**: Your most important at-risk customers (Priority 1)

### Columns

Same as RFM_Analysis sheet, but filtered to show only:
- **segment = 'AT_RISK_HIGH_VALUE'**
- **F_score >= 4** (high frequency - was loyal)
- **R_score <= 2** (low recency - now drifting)
- **recency_days < 183** (still active, not yet churned)

### Why These Customers Are Critical

1. **High Historical Value**: F_score >= 4 means they bought frequently
2. **Recent Drift**: R_score <= 2 means they're pulling away
3. **Still Recoverable**: < 183 days means not yet churned
4. **High ROI**: Saving an existing customer costs 5-7× less than acquiring new

### Recommended Actions

| Recency Days | Action | Timeline |
|--------------|--------|----------|
| 60-90 | Personal call from account manager | Within 24 hours |
| 91-120 | Email + 20% discount offer | Within 48 hours |
| 121-182 | Urgent intervention + 30% discount | Immediate |

### How to Use This Sheet

1. **This is your TOP PRIORITY list**
2. **Assign each customer to a sales rep**
3. **Track call outcomes** (add columns for notes)
4. **Follow up within 1 week**
5. **Measure recovery rate**

**Expected Outcome**: 60-70% of these customers can be saved with timely intervention.

---

## 🎯 Quick Reference Guide

### Most Important Metrics

| Metric | What It Tells You | Action Threshold |
|--------|-------------------|------------------|
| **recency_days** | How long since last purchase | > 60 days = concern |
| **frequency** | How loyal they are | < 5 orders = new/occasional |
| **RFM_score** | Overall value | < 7 = at risk |
| **is_drifting** | Purchase gap increasing | True = investigate |
| **z_score** | Drift severity | > 2.0 = urgent |
| **segment** | Behavioral category | AT_RISK_HIGH_VALUE = priority 1 |

### Daily Workflow

**Morning (9:00 AM)**:
1. Open Priority_List sheet
2. Filter action_priority = 1
3. Assign to sales team
4. Make calls

**Afternoon (2:00 PM)**:
1. Check Drift_Detection sheet
2. Filter drift_severity = 'HIGH'
3. Send intervention emails

**Weekly**:
1. Review Recently_Churned_183-365
2. Launch win-back campaigns
3. Track recovery rate

### Color Coding Recommendation

Apply conditional formatting in Excel:
- **Red**: recency_days > 120
- **Orange**: recency_days 60-120
- **Yellow**: is_drifting = True
- **Green**: RFM_score >= 10

---

## 📞 Support & Questions

**Column Missing?** Check if analysis completed successfully.

**Strange Values?** Verify data quality in source Excel.

**Need Custom Report?** Modify export in `churn_app_v3.py`.

---

**Last Updated**: 2025-12-15  
**Version**: 3.0  
**Status**: Production Ready
