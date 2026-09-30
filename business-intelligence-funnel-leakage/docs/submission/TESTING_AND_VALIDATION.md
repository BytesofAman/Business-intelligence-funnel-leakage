# TESTING AND DATA VALIDATION AUDIT REPORT

**Course**: Business Intelligence (TAE 2 Winter 2026)  
**Execution Environment**: Python 3.13.0, pytest 8.3.4, MySQL Community Server 8.0.42  
**Date of Audit**: September 28, 2026

---

## 1. Summary of Verification Results

| Verification Category | Total Checks | Passed | Failed | Status |
|:---|---:|---:|---:|:---:|
| **Automated Unit Tests (pytest)** | 52 | 52 | 0 | ✅ 100% PASS |
| **ETL Validation Engine (`validate.py`)** | 34 | 34 | 0 | ✅ 100% PASS |
| **MySQL Table Row Count Verification** | 7 | 7 | 0 | ✅ 100% PASS |
| **MySQL Index & View Verification** | 2 | 2 | 0 | ✅ 100% PASS |
| **Pipeline Idempotent Rerun Test** | 1 | 1 | 0 | ✅ 100% PASS |

---

## 2. Table-by-Table Row Count Verification

| Table Name | Table Type | Expected Rows | Verified MySQL Rows | Discrepancy | Status |
|:---|:---|---:|---:|---:|:---:|
| `Dim_Date` | Dimension | 366 | 366 | 0 | ✅ PASS |
| `Dim_Channel` | Dimension | 5 | 5 | 0 | ✅ PASS |
| `Dim_Campaign` | Dimension | 7 | 7 | 0 | ✅ PASS |
| `Dim_LandingPage` | Dimension | 3 | 3 | 0 | ✅ PASS |
| `Dim_Device` | Dimension | 18 | 18 | 0 | ✅ PASS |
| `Dim_Geography` | Dimension | 500 | 500 | 0 | ✅ PASS |
| `Fact_FunnelEvent`| Fact | 57,083 | 57,083 | 0 | ✅ PASS |
| **Total Warehouse Records** | - | **57,982** | **57,982** | **0** | ✅ PASS |

---

## 3. Automated Unit Testing Breakdown (`pytest tests/ -v`)

### 3.1 `test_transform.py` (25 Tests)
- `test_all_ga4_events_mapped`: Confirms every raw event maps to an approved canonical stage.
- `test_purchase_maps_correctly`, `test_view_item_maps_to_product_view`, `test_add_to_cart_maps_to_cart`, `test_begin_checkout_maps_to_checkout`: Verifies exact event routing.
- `test_unmapped_event_removed`: Prunes garbage events without raising unhandled exceptions.
- `test_funnel_order_correct`: Confirms correct chronological order of the 7 stages.
- `test_channel_normalization`: Tests cpc → Paid Search, organic → Organic Search, email → Email, null → Direct.
- `test_duplicate_handling`: Tests deduplication, preservation of first occurrence, and duplicate counting.
- `test_revenue_handling`: Guarantees revenue is \$0.00 on non-purchase events and non-negative.
- `test_missing_values`: Verifies fallback handling for null device, geography, and landing page attributes.
- `test_timestamp_normalization`: Confirms Unix microsecond conversion to UTC datetime objects.

### 3.2 `test_validation.py` (13 Tests)
- `test_valid_fact_passes`, `test_null_event_id_fails`, `test_duplicate_event_id_fails`: Fact primary key checks.
- `test_invalid_funnel_stage_fails`: Asserts failure upon arbitrary or corrupt stage strings.
- `test_negative_revenue_fails`: Verifies validation rejection on negative numbers.
- `test_valid_dimension_passes`, `test_duplicate_pk_fails`, `test_empty_dimension_warns`: Dimension constraints.
- `test_valid_fks_pass`, `test_orphan_fk_fails`: Foreign key referential integrity checks.

### 3.3 `test_kpis.py` (14 Tests)
- Verifies accuracy of Users, Sessions, Purchases, Revenue, Spend, CPA, ROAS, Cart Abandonment Rate, and Funnel Drop-off.
- Verifies safe division handling (zero spend, zero purchases, null values return `None`/`BLANK` without divide-by-zero crashes).

---

## 4. ETL Validation Engine Results (`validate.py`)

34 discrete assertions are executed during Phase 3 of the ETL pipeline:
1. `Fact: Required columns` (All 8 present)
2. `Fact: Row count` (57,083 records)
3. `Fact: Null Event_ID` (0 nulls)
4. `Fact: Duplicate Event_ID` (0 duplicates)
5. `Fact: Funnel stages` (Distribution: IMPRESSION: 17,992, CLICK: 10,495, LANDING_PAGE: 15,000, PRODUCT_VIEW: 6,853, CART: 3,284, CHECKOUT: 2,098, PURCHASE: 1,361)
6. `Fact: Null User_ID` (0 nulls, 6,803 unique)
7. `Fact: Negative revenue` (0 negative rows, Total: \$355,403.85)
8. `Fact: Negative spend` (0 negative rows, Total: \$243,209.53)
9. `Fact: Revenue allocation` (Revenue only on PURCHASE events)
10. `Fact: Timestamps` (Range: 2023-12-31 18:38:00 to 2024-12-31 17:58:25)
11–22. `Dim_* Row count, Null PK, Duplicate PK` (All 6 dimensions verified)
23–28. `FK: Channel_ID, Campaign_ID, LandingPage_ID, Device_ID, Geography_ID, Date_ID` (100% referential integrity, 0 orphan foreign keys).

---

## 5. Rerun & Idempotence Verification

* **Test Execution**: The complete ETL pipeline was executed repeatedly using `python -m etl.run_pipeline`.
* **Behavior**: `truncate_tables()` cleanly resets existing rows while respecting foreign key checks (`SET FOREIGN_KEY_CHECKS=0`), followed by controlled dimension-first ingestion.
* **Result**: Zero duplicate primary keys created; warehouse rows remain strictly identical across repeated runs.
