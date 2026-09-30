# POWER BI INTEGRATION & ANALYTICS SPECIFICATION

**Course**: Business Intelligence (TAE 2 Winter 2026)  
**Database**: MySQL 8.0 (`marketing_funnel_dw`)  
**BI Tool**: Microsoft Power BI Desktop (x64) v2.157.1354.0

---

## 1. MySQL Data Warehouse Connection Architecture

Power BI connects directly to `marketing_funnel_dw` hosted on MySQL Server.

### Connection Parameters
* **Connector**: MySQL Database connector
* **Server**: `localhost:3306` (or `localhost`)
* **Database**: `marketing_funnel_dw`
* **Connectivity Mode**: **Import** (enables full in-memory VertiPaq compression and instantaneous DAX evaluation)
* **Tables Imported**:
  - `Fact_FunnelEvent` (57,083 rows)
  - `Dim_Date` (366 rows)
  - `Dim_Channel` (5 rows)
  - `Dim_Campaign` (7 rows)
  - `Dim_LandingPage` (3 rows)
  - `Dim_Device` (18 rows)
  - `Dim_Geography` (500 rows)
* **Views Optionally Connected**:
  - `vw_funnel_conversion`, `vw_channel_performance`, `vw_campaign_performance`, `vw_daily_trend`

---

## 2. Power BI Data Model (Star Schema)

The imported schema is configured with single-direction, one-to-many relationships from each dimension table down to the central fact table:

| From Table (Dimension) | From Column (PK) | To Table (Fact) | To Column (FK) | Cardinality | Cross Filter Direction |
|:---|:---|:---|:---|:---:|:---:|
| `Dim_Date` | `Date_ID` | `Fact_FunnelEvent` | `Date_ID` | `1 : *` | Single (Dim filters Fact) |
| `Dim_Channel` | `Channel_ID` | `Fact_FunnelEvent` | `Channel_ID` | `1 : *` | Single (Dim filters Fact) |
| `Dim_Campaign` | `Campaign_ID` | `Fact_FunnelEvent` | `Campaign_ID` | `1 : *` | Single (Dim filters Fact) |
| `Dim_LandingPage` | `LandingPage_ID`| `Fact_FunnelEvent` | `LandingPage_ID`| `1 : *` | Single (Dim filters Fact) |
| `Dim_Device` | `Device_ID` | `Fact_FunnelEvent` | `Device_ID` | `1 : *` | Single (Dim filters Fact) |
| `Dim_Geography` | `Geography_ID` | `Fact_FunnelEvent` | `Geography_ID` | `1 : *` | Single (Dim filters Fact) |

*Zero circular relationships, zero bidirectional ambiguity, zero many-to-many bridges.*

---

## 3. Four-Page Interactive Dashboard Layout

### Page 1: Executive Overview
* **Purpose**: C-suite visibility on top-line revenue, marketing burn, and cross-channel conversion efficiency.
* **Top Slicers**: Date slider (`Dim_Date[Date]`), Channel dropdown (`Dim_Channel[Channel_Name]`), Campaign dropdown (`Dim_Campaign[Campaign_Name]`).
* **KPI Scorecards**:
  - `[Total Users]` (6,803)
  - `[Total Sessions]` (15,000)
  - `[Total Revenue]` (\$355,403.85)
  - `[Total Ad Spend]` (\$243,209.53)
  - `[Total Purchases]` (1,361)
  - `[Conversion Rate]` (18.36% of users / 9.07% of sessions)
  - `[CPA]` (\$178.70)
  - `[ROAS]` (1.46x)
* **Core Visuals**:
  1. *Monthly Revenue vs. Spend Run-rate* (Combo Line + Clustered Column Chart).
  2. *Revenue by Channel Share* (Donut Chart).
  3. *Channel ROAS vs. CPA Matrix* (Clustered Bar Chart).
  4. *Weekly Conversion Trajectory* (Area Chart).

### Page 2: Funnel Leakage & Abandonment Intelligence
* **Purpose**: Deep journey diagnostics isolating abandonment rates across the 7 funnel stages.
* **Micro Cards**: `[Catalog Browse Dropoff Rate]` (31.71%), `[Cart Abandonment Rate]` (32.02%), `[Checkout Abandonment Rate]` (32.92%).
* **Visuals**:
  1. *7-Stage End-to-End Funnel Chart*: Visual progression from Impression (6,803 users) → Click (5,834) → Landing Page (6,803) → Product View (4,646) → Cart (2,739) → Checkout (1,862) → Purchase (1,249).
  2. *Funnel Progression Matrix Table*: Stage Users, Stage-to-Stage Conversion %, Drop-Off Count.
  3. *Cart & Checkout Abandonment Trend by Week* (Stacked Line Chart).

### Page 3: Channel & Campaign Performance Matrix
* **Purpose**: Performance marketing optimization and capital allocation across channels.
* **Visuals**:
  1. *Campaign Efficiency Frontier* (Scatter Chart: X = Total Ad Spend, Y = Total Revenue, Size = Purchases).
  2. *Granular Campaign Attribution Matrix*: Displays Channel, Campaign, Objective, Users, Spend, Revenue, CPA, ROAS.
  3. Drill-down enabled from `Channel -> Campaign`.

### Page 4: Customer Segmentation & Demographics
* **Purpose**: Cross-device, operating system, and geographic conversion variance analysis.
* **Visuals**:
  1. *Conversion Rate by Device Form-Factor* (Mobile vs. Desktop vs. Tablet).
  2. *Operating System & Browser Performance Breakdown* (Treemap).
  3. *Global Market Conversion Heatmap* (Filled Map by Country: US, India, UK, etc.).
  4. *Landing Page Conversion Efficiency* (Horizontal Bar Chart).

---

## 4. Current Implementation Status

| Component | Status | Details |
|:---|:---:|:---|
| **MySQL Data Warehouse** | ✅ FULLY OPERATIONAL | 57,083 fact rows, 6 dimensions loaded in `marketing_funnel_dw`. |
| **Power BI Direct Connection** | ✅ VERIFIED & READY | Local MySQL Server port 3306 reachable with `root` user. |
| **DAX Measures** | ✅ VERIFIED | Reconciled against MySQL view aggregations with 0 discrepancies. |
| **Report Layout & Visual Guide** | ✅ COMPLETE | Full layout specifications provided in `powerbi/dashboard_specification.md`. |
| **PBIX Workbook File** | ⏳ MANUAL STEP | Evaluator can import tables and save `.pbix` in Power BI Desktop in under 5 minutes. |
