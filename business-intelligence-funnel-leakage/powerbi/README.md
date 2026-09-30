# Power BI Integration & Model Overview

This directory contains the complete specifications, data model architecture, DAX formulas, and execution guides required to build and deploy the interactive **Cross-Channel Marketing Funnel Leakage Intelligence** dashboard in Microsoft Power BI Desktop.

---

## 1. Directory Contents

* **`POWERBI_SETUP_GUIDE.md`**: Step-by-step instructions for connecting Power BI Desktop to MySQL / CSV files, configuring relationships, and importing tables.
* **`dashboard_specification.md`**: Visual layout, card dimensions, chart definitions, and slicing hierarchies for all 4 report pages.
* **`dax_measures.md`**: Verified, production-grade DAX formulas reconciling identically with SQL analytical queries.

---

## 2. Power BI Star Schema Model

```
       +-----------------+             +------------------+
       |   Dim_Channel   |             |   Dim_Campaign   |
       +-----------------+             +------------------+
               | 1                             | 1
               |                               |
               | *                             | *
               +-------->              +------->
                        |              |
               +--------------------------------+
               |        Fact_FunnelEvent        |
               +--------------------------------+
                        |              |
               +--------+              +--------+
               | *                             | *
               |                               |
               | 1                             | 1
       +-----------------+             +------------------+
       | Dim_LandingPage |             |    Dim_Device    |
       +-----------------+             +------------------+
               |                                |
               +-------------+    +-------------+
                           * |    | *
                             v    v
                    +--------------------+
                    |   Dim_Geography    |
                    +--------------------+
                             ^ 1
                             |
                             | *
                    +--------------------+
                    |      Dim_Date      |
                    +--------------------+
```

* **Relationship Card**: Single-direction (1 to Many, `1:*`), from dimension tables down to `Fact_FunnelEvent`.
* **Cross-filter direction**: Single (Dimension filters Fact).

---

## 3. The 4 Dashboard Pages

1. **Page 1: Executive Overview**: High-level financial KPIs, revenue and spend run-rate, conversion rates, and channel ROI distribution.
2. **Page 2: Funnel Leakage & Abandonment**: Comprehensive 7-stage visual funnel, stage-to-stage conversion %, drop-off volume, and cart/checkout abandonment metrics.
3. **Page 3: Channel & Campaign Performance**: Granular acquisition matrix, campaign ROI tables, CPA vs. ROAS cross-plot, and drill-down hierarchy (`Channel -> Campaign`).
4. **Page 4: Customer Segmentation & Demographics**: Device form-factor conversion, operating system breakdowns, geographic conversion map, and landing page performance.
