# Power BI Production DAX Measure Library

All measures below have been tested and verified to reconcile identically against SQL analytical queries in `sql/06_kpi_queries.sql`.

---

## 1. Core Volume Measures

```dax
// Total Unique Users
Total Users = 
DISTINCTCOUNT(Fact_FunnelEvent[User_ID])
```

```dax
// Total Sessions
Total Sessions = 
DISTINCTCOUNT(Fact_FunnelEvent[Session_ID])
```

```dax
// Total Standardized Events
Total Events = 
COUNTROWS(Fact_FunnelEvent)
```

```dax
// Total Purchases Completed
Total Purchases = 
CALCULATE(
    COUNTROWS(Fact_FunnelEvent),
    Fact_FunnelEvent[Funnel_Stage] = "PURCHASE"
)
```

---

## 2. Financial & Efficiency Measures

```dax
// Total Attributed Revenue ($ USD)
Total Revenue = 
SUM(Fact_FunnelEvent[Revenue])
```

```dax
// Total Attributed Ad Spend ($ USD)
Total Ad Spend = 
SUM(Fact_FunnelEvent[Ad_Spend])
```

```dax
// Return On Ad Spend (ROAS)
ROAS = 
DIVIDE(
    [Total Revenue],
    [Total Ad Spend],
    BLANK()
)
```

```dax
// Cost Per Acquisition (CPA)
CPA = 
DIVIDE(
    [Total Ad Spend],
    [Total Purchases],
    BLANK()
)
```

```dax
// Overall End-to-End Funnel Conversion Rate
Conversion Rate = 
DIVIDE(
    [Total Purchases],
    [Total Users],
    0
)
```

---

## 3. Funnel Stage Counts

```dax
Stage Users - Impression = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "IMPRESSION")

Stage Users - Click = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "CLICK")

Stage Users - Landing Page = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "LANDING_PAGE")

Stage Users - Product View = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "PRODUCT_VIEW")

Stage Users - Cart = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "CART")

Stage Users - Checkout = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "CHECKOUT")

Stage Users - Purchase = 
CALCULATE(DISTINCTCOUNT(Fact_FunnelEvent[User_ID]), Fact_FunnelEvent[Funnel_Stage] = "PURCHASE")
```

---

## 4. Abandonment & Leakage Metrics

```dax
// Cart Abandonment Rate (% of cart users who do not proceed to checkout)
Cart Abandonment Rate = 
VAR CartUsers = [Stage Users - Cart]
VAR CheckoutUsers = [Stage Users - Checkout]
RETURN
DIVIDE(CartUsers - CheckoutUsers, CartUsers, 0)
```

```dax
// Checkout Abandonment Rate (% of checkout users who do not complete purchase)
Checkout Abandonment Rate = 
VAR CheckoutUsers = [Stage Users - Checkout]
VAR PurchaseUsers = [Stage Users - Purchase]
RETURN
DIVIDE(CheckoutUsers - PurchaseUsers, CheckoutUsers, 0)
```

```dax
// Product Page Drop-off Rate (% arriving on landing page who never view a product)
Catalog Browse Dropoff Rate = 
VAR LandingUsers = [Stage Users - Landing Page]
VAR ProductUsers = [Stage Users - Product View]
RETURN
DIVIDE(LandingUsers - ProductUsers, LandingUsers, 0)
```
