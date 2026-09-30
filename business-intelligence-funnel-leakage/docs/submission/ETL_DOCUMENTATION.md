# ETL PIPELINE SPECIFICATION & DOCUMENTATION

**Course**: Business Intelligence (TAE 2 Winter 2026)  
**Pipeline Orchestrator**: `python -m etl.run_pipeline`  
**Execution Environment**: Python 3.13.0, pandas 2.3.0, mysql-connector-python 8.0.33  
**Verified Execution Time**: ~56.6 seconds (Full Extraction → Transformation → Validation → MySQL Ingestion)

---

## 1. Pipeline Execution Flow

```
[Phase 1: EXTRACTION]
  ├─ load_ga4_events()     --> data/raw/ga4/ga4_events.csv    (57,083 rows)
  ├─ load_campaign_data()  --> data/raw/ga4/campaign_data.csv (7 rows)
  ├─ load_ad_spend_data()  --> data/raw/ga4/ad_spend.csv      (1,830 rows)
  └─ API Adapters (Google Ads, Meta, HubSpot, Email) -> Graceful unauthenticated status

[Phase 2: TRANSFORMATION]
  ├─ Step 1: Standardize column names (snake_case)
  ├─ Step 2: Normalize timestamps (Unix microseconds -> UTC datetime)
  ├─ Step 3: Canonical funnel stage mapping (7 standard stages)
  ├─ Step 4: Channel normalization (Paid Search, Organic, Social, Email, Direct)
  ├─ Step 5: Campaign normalization & reference lookup
  ├─ Step 6: Device classification (mobile, desktop, tablet + OS + Browser)
  ├─ Step 7: Geography normalization (Country, Region, City)
  ├─ Step 8: Landing page categorization (Home, Apparel, Bags)
  ├─ Step 9: Revenue isolation (strictly on PURCHASE stage)
  ├─ Step 10: Conversion flag derivation
  ├─ Step 11: Date_ID surrogate key generation (YYYYMMDD)
  ├─ Step 12: Event deduplication (Event_ID uniqueness check)
  ├─ Step 13: Ad spend proportional allocation (allocated to IMPRESSION events)
  ├─ Step 14: Dimension table extraction & surrogate key generation (6 dimensions)
  ├─ Step 15: Fact table assembly (surrogate key resolution)
  └─ Persist processed CSV staging files in data/processed/

[Phase 3: VALIDATION]
  └─ 34 automated quality checks (Required columns, PK uniqueness, FK referential integrity, 
     financial non-negativity, funnel stage validity) -> 100% PASS (34/34)

[Phase 4: LOADING (MySQL)]
  ├─ Database creation (marketing_funnel_dw)
  ├─ Schema DDL parsing (comment-safe SQL splitter)
  ├─ Dimension-first table creation & truncation for clean idempotence
  ├─ Batch insertion with comprehensive type sanitization:
  │   - Dim_Date: 366 rows
  │   - Dim_Channel: 5 rows
  │   - Dim_Campaign: 7 rows
  │   - Dim_LandingPage: 3 rows
  │   - Dim_Device: 18 rows
  │   - Dim_Geography: 500 rows
  │   - Fact_FunnelEvent: 57,083 rows
  ├─ Performance index creation (18 B-Tree indexes)
  ├─ Analytical view creation (9 views)
  └─ Direct SQL verification query to guarantee actual row counts in MySQL
```

---

## 2. Transformation Engineering Details

### 2.1 Funnel Stage Mapping Matrix
| Raw GA4 `event_name` | Canonical `Funnel_Stage` | Order | Stage Objective |
|:---|:---|:---:|:---|
| `session_start`, `first_visit` | `IMPRESSION` | 1 | Traffic entry and brand awareness |
| `click` | `CLICK` | 2 | Promotional or link engagement |
| `page_view` | `LANDING_PAGE` | 3 | Initial catalog page render |
| `view_item` | `PRODUCT_VIEW` | 4 | In-depth product exploration |
| `add_to_cart` | `CART` | 5 | Commercial purchase intent |
| `begin_checkout` | `CHECKOUT` | 6 | Payment & address entry flow |
| `purchase` | `PURCHASE` | 7 | Order confirmation and revenue |

### 2.2 Ad Spend Allocation Methodology
To prevent downstream double-counting across multi-stage sessions, total daily campaign marketing spend is allocated proportionally strictly to `IMPRESSION` events:
$$\text{Spend per Impression} = \frac{\text{Daily Campaign Spend}}{\text{Total Campaign Impressions on Date}}$$
- Total allocated spend across all impressions: **\$243,209.53**
- Total recorded spend in raw ad spend log: **\$244,491.69** (99.5% attributed to active session dates; unallocated remainder belongs to days with zero recorded sessions).

---

## 3. Database Loading & Type Conversion Fix

### The Problem
During initial MySQL batch loading, `mysql-connector-python` fails when encountering pandas-specific data types (such as `pd.Timestamp`, `pd.NaT`, `pd.NA`, or `numpy.int64`), raising:
`Failed processing format-parameters; Python 'timestamp' cannot be converted to a MySQL type`

### The Solution (`etl/load.py`)
Implemented `convert_value_for_mysql(val)` which explicitly transforms every scalar before insertion:
* `pd.isna(val) or val is pd.NaT or val is pd.NA` → `None` (SQL `NULL`)
* `isinstance(val, pd.Timestamp)` → `val.to_pydatetime()` (native Python `datetime.datetime`)
* `isinstance(val, (datetime.datetime, datetime.date))` → preserved
* `hasattr(val, 'item')` → `val.item()` (native Python `int`, `float`, `bool`)

### SQL Parser Fix
Replaced simple string splitting on `;` with `parse_sql_statements(sql_text)` that removes block comments `/* ... */` and strips `--` line comments before identifying executable statements. This eliminated the previous schema failure where `USE` or comment lines caused `CREATE TABLE` statements to be skipped.

---

## 4. Final Verified Database Row Counts

| Target Table | Expected Rows | Verified MySQL Rows | Load Status |
|:---|---:|---:|:---:|
| `Dim_Date` | 366 | 366 | ✅ PASS |
| `Dim_Channel` | 5 | 5 | ✅ PASS |
| `Dim_Campaign` | 7 | 7 | ✅ PASS |
| `Dim_LandingPage` | 3 | 3 | ✅ PASS |
| `Dim_Device` | 18 | 18 | ✅ PASS |
| `Dim_Geography` | 500 | 500 | ✅ PASS |
| `Fact_FunnelEvent` | 57,083 | 57,083 | ✅ PASS |
| **Total Rows** | **57,982** | **57,982** | ✅ PASS |
