# Excel Quick Reference Card

## 📊 5-Sheet Export Structure

```
churn_analysis_results.xlsx
├── 1. Priority_List          ← START HERE (sorted by urgency)
├── 2. Recently_Churned        ← Win-back targets (183-365 days)
├── 3. RFM_Analysis            ← Complete customer scoring
├── 4. Drift_Detection         ← Early warning system
└── 5. At_Risk_High_Value      ← Your TOP PRIORITY customers
```

---

## 🎯 Top 10 Most Important Columns

| # | Column | What It Means | Good Value | Bad Value |
|---|--------|---------------|------------|-----------|
| 1 | **action_priority** | Who to contact first | 1-2 | 7-9 |
| 2 | **segment** | Customer category | AT_RISK_HIGH_VALUE | CHURNED_OUT_LONG_TERM |
| 3 | **recency_days** | Days since last purchase | < 30 | > 120 |
| 4 | **frequency** | Total orders | > 10 | < 3 |
| 5 | **RFM_score** | Overall value (3-15) | 10-15 | 3-6 |
| 6 | **is_drifting** | Purchase gap increasing | False | True |
| 7 | **z_score** | Drift severity | < 1.0 | > 2.0 |
| 8 | **F_score** | Frequency score (1-5) | 4-5 | 1-2 |
| 9 | **R_score** | Recency score (1-5) | 4-5 | 1-2 |
| 10 | **churn_timeline** | Status category | ACTIVE | CHURNED_OUT |

---

## 🚨 Priority Actions

### Sheet 1: Priority_List

**Filter**: `action_priority = 1`  
**Action**: Call within 24 hours  
**Expected**: 240 customers (AT_RISK_HIGH_VALUE)

### Sheet 2: Recently_Churned

**Filter**: `recency_days between 183-240`  
**Action**: Win-back email + 30% discount  
**Expected**: 30-40% recovery rate

### Sheet 5: At_Risk_High_Value

**Filter**: None needed (already filtered)  
**Action**: Personal intervention  
**Expected**: 60-70% save rate

---

## 📈 Key Formulas

### RFM Score
```
RFM_score = R_score + F_score + M_score
Range: 3 (worst) to 15 (best)
```

### Z-Score (Drift)
```
z_score = (current_gap - avg_purchase_gap) / std_gap
> 2.0 = HIGH drift
1.0-2.0 = MEDIUM drift
< 1.0 = LOW drift
```

### Churn Status
```
is_churned = recency_days >= 183
recently_churned = 183 <= recency_days <= 365
long_term_churned = recency_days > 365
```

---

## 🎨 Recommended Excel Formatting

### Conditional Formatting Rules

**Recency Days**:
- Red: > 120
- Orange: 60-120
- Yellow: 30-60
- Green: < 30

**RFM Score**:
- Green: >= 10
- Yellow: 7-9
- Red: < 7

**Is Drifting**:
- Red fill: TRUE
- No fill: FALSE

---

## 📞 Daily Workflow

### Morning (15 minutes)
1. Open **Priority_List**
2. Sort by `action_priority`
3. Assign top 20 to sales team
4. Track in CRM

### Afternoon (10 minutes)
1. Open **Drift_Detection**
2. Filter `drift_severity = HIGH`
3. Send automated emails
4. Schedule follow-ups

### Weekly (30 minutes)
1. Open **Recently_Churned**
2. Launch win-back campaign
3. Track recovery metrics
4. Update strategy

---

## 💡 Pro Tips

1. **Auto-filter is your friend**: Use Excel's filter feature on every sheet
2. **Freeze top row**: View → Freeze Panes → Freeze Top Row
3. **Sort by priority**: Always start with action_priority column
4. **Add notes column**: Track your interventions
5. **Save as template**: Create a master workbook with formulas

---

## 🔍 Common Questions

**Q: Why is recently_churned less than total churned?**  
A: Recently churned (183-365 days) is a SUBSET of total churned (183+ days)

**Q: What's the difference between AT_RISK and AT_RISK_HIGH_VALUE?**  
A: AT_RISK_HIGH_VALUE = was very loyal (F>=4), now drifting (R<=2). Higher priority.

**Q: Why are columns auto-sized?**  
A: For readability. All columns are 12-50 characters wide automatically.

**Q: Can I add my own columns?**  
A: Yes! Add notes, call outcomes, recovery status, etc.

---

## 📊 Expected Counts (XYZ Sheet Example)

| Sheet | Typical Count | What It Means |
|-------|---------------|---------------|
| Priority_List | 4,704 | All customers |
| Recently_Churned | 490 | Win-back targets |
| RFM_Analysis | 4,704 | Complete analysis |
| Drift_Detection | 95 | Customers drifting |
| At_Risk_High_Value | 240 | TOP PRIORITY |

---

**Print this page and keep it at your desk!**

Last Updated: 2025-12-15
