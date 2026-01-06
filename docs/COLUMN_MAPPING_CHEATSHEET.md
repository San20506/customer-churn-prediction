# Column Mapping Reference

**Skipper Churn Prediction System**

---

## Required Columns

| System Column | Your Column Must Contain | Status |
|---------------|--------------------------|--------|
| Transaction Date | `TRXN_DATE` or any column with "date" | **Required** |
| Customer ID | `MEMBERSHIP ID` or any column with "id" | **Required** |

---

## Optional Columns

| System Column | Your Column Name | Purpose |
|---------------|------------------|---------|
| Points | `POINT_AWARDED` | Monetary scoring |
| Quantity | `QUANTITY` | Volume analysis |
| State | `STATE` | Geographic analysis |
| Retailer | `RETAILER CODE` | Channel analysis |
| Distributor | `DISTRIBUTOR CODE` | Channel analysis |

---

## Data Template

| TRXN_DATE | MEMBERSHIP ID | STATE | RETAILER CODE | DISTRIBUTOR CODE | QUANTITY | POINT_AWARDED |
|-----------|---------------|-------|---------------|------------------|----------|---------------|
| 2024-01-15 | 8583996292 | West Bengal | RET001 | 101 | 5 | 150 |

---

## Output Priorities

| Priority | Segment | Action Required |
|----------|---------|-----------------|
| 1 | AT_RISK_HIGH_VALUE | Immediate contact |
| 2 | AT_RISK | Contact within 48h |
| 3 | CHURNED_RECENTLY | Win-back campaign |
| 9 | LOYAL_ACTIVE | Maintain relationship |

---

**Full documentation:** See `DATA_PREPARATION_GUIDE.md`
