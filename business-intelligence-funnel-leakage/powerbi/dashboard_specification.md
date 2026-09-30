# Power BI 4-Page Dashboard Specification

This specification outlines the visual architecture, coordinate layouts, measures, and interaction schemes for building an executive-grade 4-page dashboard report.

---

## Page 1: Executive Overview

**Target Audience**: CMO, VP of Marketing, Digital Performance Directors  
**Primary Objective**: Deliver an immediate pulse on top-line revenue, marketing expenditure, blended CPA, and cross-channel conversion performance.

### 1. Global Slicers (Top Banner)
* **Date Range Slicer**: Between slider bound to `Dim_Date[Date]`.
* **Channel Dropdown**: Multi-select dropdown bound to `Dim_Channel[Channel_Name]`.
* **Campaign Dropdown**: Multi-select dropdown bound to `Dim_Campaign[Campaign_Name]`.

### 2. High-Impact KPI Scorecards (Row 1)
* **Card 1**: Total Users (`[Total Users]`)
* **Card 2**: Total Sessions (`[Total Sessions]`)
* **Card 3**: Total Revenue (`[Total Revenue]`, formatted as Currency)
* **Card 4**: Total Ad Spend (`[Total Ad Spend]`, formatted as Currency)
* **Card 5**: Total Purchases (`[Total Purchases]`)
* **Card 6**: Blended Conversion Rate (`[Conversion Rate]`, formatted as %)
* **Card 7**: Blended CPA (`[CPA]`, formatted as Currency)
* **Card 8**: Return On Ad Spend (`[ROAS]`, formatted as Decimal `X.XXx`)

### 3. Core Visuals (Body)
* **Chart 1 (Left 60% Width)**: *Monthly Revenue vs. Ad Spend Run-Rate*
  * **Visual Type**: Line and Clustered Column Chart
  * **Shared X-Axis**: `Dim_Date[Month_Name]` (Sorted chronologically)
  * **Column Values**: `[Total Revenue]`
  * **Line Values**: `[Total Ad Spend]`
* **Chart 2 (Right 40% Width)**: *Revenue by Channel Distribution*
  * **Visual Type**: Donut Chart
  * **Legend**: `Dim_Channel[Channel_Name]`
  * **Values**: `[Total Revenue]`
* **Chart 3 (Bottom Left)**: *ROAS & CPA by Channel Matrix*
  * **Visual Type**: Clustered Bar Chart
  * **Y-Axis**: `Dim_Channel[Channel_Name]`
  * **X-Axis**: `[ROAS]` and `[CPA]`
* **Chart 4 (Bottom Right)**: *Weekly Conversion Rate Trajectory*
  * **Visual Type**: Area Chart
  * **X-Axis**: `Dim_Date[Week]`
  * **Y-Axis**: `[Conversion Rate]`

---

## Page 2: Funnel Leakage & Abandonment Intelligence

**Target Audience**: Growth Hackers, UX/CRO Specialists, Product Managers  
**Primary Objective**: Isolate the exact point of journey abandonment across the 7 funnel stages.

### 1. Slicers
* Date Slicer, Channel Slicer, Device Type Slicer.

### 2. Micro KPI Callout Cards
* **Card 1**: Catalog Browse Drop-Off (`[Catalog Browse Dropoff Rate]`)
* **Card 2**: Cart Abandonment Rate (`[Cart Abandonment Rate]`)
* **Card 3**: Checkout Abandonment Rate (`[Checkout Abandonment Rate]`)

### 3. Primary Visuals
* **Visual 1 (Centerpiece Funnel)**: *End-to-End Customer Conversion Funnel*
  * **Visual Type**: Funnel Chart
  * **Category**: `Fact_FunnelEvent[Funnel_Stage]` (Custom sorted: Impression -> Click -> Landing Page -> Product View -> Cart -> Checkout -> Purchase)
  * **Values**: `[Total Users]`
* **Visual 2 (Right Matrix)**: *Funnel Progression & Leakage Audit Table*
  * **Columns**: `Stage Name`, `Stage Users`, `Previous Stage Users`, `Stage Conversion %`, `Absolute Drop-Off Count`.
* **Visual 3 (Bottom Left)**: *Cart & Checkout Abandonment Trend by Week*
  * **Visual Type**: Stacked Line Chart
  * **X-Axis**: `Dim_Date[Week]`
  * **Lines**: `[Cart Abandonment Rate]`, `[Checkout Abandonment Rate]`

---

## Page 3: Channel & Campaign Performance Matrix

**Target Audience**: Media Buyers, Search & Social Campaign Managers  
**Primary Objective**: Granular ROI optimization and capital reallocation across campaigns.

### 1. Slicers
* Channel, Campaign Objective, Date Range.

### 2. Core Visuals
* **Visual 1 (Top Scatter)**: *Campaign Efficiency Frontier (Spend vs. Revenue)*
  * **Visual Type**: Scatter Chart
  * **X-Axis**: `[Total Ad Spend]`
  * **Y-Axis**: `[Total Revenue]`
  * **Size**: `[Total Purchases]`
  * **Legend / Details**: `Dim_Campaign[Campaign_Name]`
* **Visual 2 (Bottom Granular Table)**: *Detailed Campaign Attribution Table*
  * **Matrix/Table Fields**:
    * `Dim_Channel[Channel_Name]`
    * `Dim_Campaign[Campaign_Name]`
    * `Dim_Campaign[Objective]`
    * `[Total Users]`
    * `[Total Sessions]`
    * `[Total Ad Spend]`
    * `[Total Revenue]`
    * `[ROAS]`
    * `[CPA]`
    * `[Conversion Rate]`

---

## Page 4: Customer Segmentation & Demographics

**Target Audience**: Customer Insights Analysts, International Growth Leads  
**Primary Objective**: Uncover conversion variances across hardware platforms, operating systems, and geographies.

### 1. Core Visuals
* **Visual 1 (Top Left)**: *Conversion Rate by Device Form-Factor*
  * **Visual Type**: Clustered Column Chart
  * **X-Axis**: `Dim_Device[Device_Type]` (Mobile vs. Desktop vs. Tablet)
  * **Y-Axis**: `[Conversion Rate]` and `[Checkout Abandonment Rate]`
* **Visual 2 (Top Right)**: *Operating System & Browser Performance Breakdown*
  * **Visual Type**: Treemap
  * **Group**: `Dim_Device[OS]`
  * **Details**: `Dim_Device[Browser]`
  * **Values**: `[Total Purchases]`
* **Visual 3 (Bottom Left)**: *Geographic Market Conversion Heatmap*
  * **Visual Type**: Map / Filled Map
  * **Location**: `Dim_Geography[Country]`
  * **Bubble Size**: `[Total Revenue]`
  * **Tooltips**: `[Conversion Rate]`, `[Total Users]`
* **Visual 4 (Bottom Right)**: *Landing Page Efficiency Comparison*
  * **Visual Type**: Horizontal Bar Chart
  * **Y-Axis**: `Dim_LandingPage[Page_Category]`
  * **X-Axis**: `[Conversion Rate]`
