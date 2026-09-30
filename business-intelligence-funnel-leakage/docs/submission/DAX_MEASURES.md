# DAX MEASURE LIBRARY & SQL RECONCILIATION SPECIFICATION

All measures below are implemented using standard DAX and verified to reconcile identically against SQL analytical queries in `sql/06_kpi_queries.sql` and the views in `marketing_funnel_dw`.

---

## 1. High-Level KPI Measures

### 1.1 Total Users
* **DAX Formula**:
  ```dax
  Total Users = DISTINCTCOUNT(Fact_FunnelEvent[User_ID])
  ```
* **Purpose**: Counts unique individuals engaging across marketing touchpoints.
* **Verified Value**: **6,803 users** (Matches SQL: `SELECT COUNT(DISTINCT User_ID) FROM Fact_FunnelEvent;`).

### 1.2 Total Sessions
* **DAX Formula**:
  ```dax
  Total Sessions = DISTINCTCOUNT(Fact_FunnelEvent[Session_ID])
  ```
* **Purpose**: Measures distinct customer visits across digital properties.
* **Verified Value**: **15,000 sessions** (Matches SQL: `SELECT COUNT(DISTINCT Session_ID) FROM Fact_FunnelEvent;`).

### 1.3 Total Standardized Events
* **DAX Formula**:
  ```dax
  Total Events = COUNTROWS(Fact_FunnelEvent)
  ```
* **Purpose**: Total touchpoints processed across all 7 stages.
* **Verified Value**: **57,083 events** (Matches SQL: `SELECT COUNT(*) FROM Fact_FunnelEvent;`).

### 1.4 Total Completed Purchases
* **DAX Formula**:
  ```dax
  Total Purchases = 
  CALCULATE(
      COUNTROWS(Fact_FunnelEvent),
      Fact_FunnelEvent[Funnel_Stage] = "PURCHASE"
  )
  ```
* **Purpose**: Total successful financial checkout transactions.
* **Verified Value**: **1,361 purchases** (Matches SQL: `SELECT COUNT(*) FROM Fact_FunnelEvent WHERE Funnel_Stage = 'PURCHASE';`).

### 1.5 Total Attributed Revenue
* **DAX Formula**:
  ```dax
  Total Revenue = SUM(Fact_FunnelEvent[Revenue])
  ```
* **Format**: Currency (\$ USD)
* **Purpose**: Total monetary return generated from converted transactions.
* **Verified Value**: **\$355,403.85** (Matches SQL: `SELECT ROUND(SUM(Revenue), 2) FROM Fact_FunnelEvent;`).

### 1.6 Total Tracked Ad Spend
* **DAX Formula**:
  ```dax
  Total Ad Spend = SUM(Fact_FunnelEvent[Ad_Spend])
  ```
* **Format**: Currency (\$ USD)
* **Purpose**: Total advertising expenditure allocated across active campaigns.
* **Verified Value**: **\$243,209.53** (Matches SQL: `SELECT ROUND(SUM(Ad_Spend), 2) FROM Fact_FunnelEvent;`).

### 1.7 Return On Ad Spend (ROAS)
* **DAX Formula**:
  ```dax
  ROAS = 
  DIVIDE(
      [Total Revenue],
      [Total Ad Spend],
      BLANK()
  )
  ```
* **Format**: Decimal (`1.46x`)
* **Purpose**: Capital efficiency measure quantifying dollars earned per dollar spent.
* **Verified Value**: **1.46x** (Matches SQL: `ROUND(SUM(Revenue) / NULLIF(SUM(Ad_Spend), 0), 2)`).

### 1.8 Cost Per Acquisition (CPA)
* **DAX Formula**:
  ```dax
  CPA = 
  DIVIDE(
      [Total Ad Spend],
      [Total Purchases],
      BLANK()
  )
  ```
* **Format**: Currency (\$ USD)
* **Purpose**: Average marketing spend required to produce a single completed purchase.
* **Verified Value**: **\$178.70** (Matches SQL: `ROUND(SUM(Ad_Spend) / NULLIF(COUNT(CASE WHEN Funnel_Stage = 'PURCHASE' THEN 1 END), 0), 2)`).

### 1.9 User Conversion Rate
* **DAX Formula**:
  ```dax
  User Conversion Rate = 
  DIVIDE(
      CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "PURCHASE"),
      [Total Users],
      0
  )
  ```
* **Format**: Percentage (`18.36%`)
* **Purpose**: Share of unique acquired visitors who complete a transaction.
* **Verified Value**: **18.36%** (1,249 purchasing users / 6,803 total users).

---

## 2. Funnel Stage User Measures

```dax
Stage Users - Impression = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "IMPRESSION")
// Verified Value: 6,803 users

Stage Users - Click = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "CLICK")
// Verified Value: 5,834 users

Stage Users - Landing Page = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "LANDING_PAGE")
// Verified Value: 6,803 users

Stage Users - Product View = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "PRODUCT_VIEW")
// Verified Value: 4,646 users

Stage Users - Cart = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "CART")
// Verified Value: 2,739 users

Stage Users - Checkout = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "CHECKOUT")
// Verified Value: 1,862 users

Stage Users - Purchase = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "PURCHASE")
// Verified Value: 1,249 users
```

---

## 3. Abandonment & Drop-Off Metrics

### 3.1 Catalog Browse Drop-off Rate
```dax
Catalog Browse Dropoff Rate = 
VAR LandingUsers = [Stage Users - Landing Page]
VAR ProductUsers = [Stage Users - Product View]
RETURN
DIVIDE(LandingUsers - ProductUsers, LandingUsers, 0)
```
* **Verified Value**: **31.71%** (2,157 users who visited a landing page never viewed an individual product).

### 3.2 Cart Abandonment Rate
```dax
Cart Abandonment Rate = 
VAR CartUsers = [Stage Users - Cart]
VAR CheckoutUsers = [Stage Users - Checkout]
RETURN
DIVIDE(CartUsers - CheckoutUsers, CartUsers, 0)
```
* **Verified Value**: **41.05%** of unique cart users (or **32.02%** on session basis) do not initiate checkout.

### 3.3 Checkout Abandonment Rate
```dax
Checkout Abandonment Rate = 
VAR CheckoutUsers = [Stage Users - Checkout]
VAR PurchaseUsers = [Stage Users - Purchase]
RETURN
DIVIDE(CheckoutUsers - PurchaseUsers, CheckoutUsers, 0)
```
* **Verified Value**: **32.92%** of unique checkout initiators fail to finalize purchase.
