# Data Warehouse Documentation: Star Schema Specification

---

## 1. Schema Architecture

The data warehouse adheres strictly to a dimensional **Star Schema** centered around the `Fact_FunnelEvent` table, surrounded by 6 conformed dimension tables.

```
       +-----------------+             +------------------+
       |   Dim_Channel   |             |   Dim_Campaign   |
       +-----------------+             +------------------+
               |                                |
               | 1                            1 |
               |                                |
               +--------+              +--------+
                        |              |
                        v              v
               +--------------------------------+
               |        Fact_FunnelEvent        |
               +--------------------------------+
                        ^              ^
                        |              |
               +--------+              +--------+
               |                                |
               | 1                            1 |
               |                                |
       +-----------------+             +------------------+
       | Dim_LandingPage |             |    Dim_Device    |
       +-----------------+             +------------------+
               |                                |
               +-------------+    +-------------+
                             |    |
                             v    v
                    +--------------------+
                    |   Dim_Geography    |
                    +--------------------+
                             ^
                             | 1
                    +--------------------+
                    |      Dim_Date      |
                    +--------------------+
```

---

## 2. Table Specifications & Cardinality

### Dimensions
| Table Name | Primary Key | Estimated Rows | Purpose |
|:---|:---|:---:|:---|
| `Dim_Date` | `Date_ID` (INT) | 366 | Temporal analysis across days, weeks, months, and quarters. |
| `Dim_Channel` | `Channel_ID` (INT) | 5-10 | Digital acquisition channels (Organic, Paid Search, Social, etc.). |
| `Dim_Campaign` | `Campaign_ID` (VARCHAR) | 7-30 | Marketing campaign tracking, goals, and budgets. |
| `Dim_LandingPage` | `LandingPage_ID` (INT) | 3-50 | Entry URLs and catalog categories. |
| `Dim_Device` | `Device_ID` (INT) | 18-50 | Cross-device attributes (Mobile/Desktop/Tablet, OS, Browser). |
| `Dim_Geography` | `Geography_ID` (INT) | 500+ | Regional market segmentation (Country, Region, City). |

### Fact Table
| Table Name | Primary Key | Foreign Keys | Estimated Rows |
|:---|:---|:---|:---:|
| `Fact_FunnelEvent` | `Event_ID` (UUID) | 6 Dimension FKs | 57,000+ |

---

## 3. Storage Optimization & Indexing

The schema implements optimized composite and single-column B-Tree indexes:
1. `idx_fact_funnel_stage`: Speeds up funnel progression counts.
2. `idx_fact_stage_date`: Enables high-speed slicing by time periods and stages.
3. `idx_fact_channel_stage`: Optimizes channel-specific conversion and drop-off queries.
4. `idx_fact_campaign_stage`: Enables rapid campaign ROI and funnel leakage calculations.
