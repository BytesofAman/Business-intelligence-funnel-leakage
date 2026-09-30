# Cross-Channel Marketing Funnel Leakage Intelligence

### A Business Intelligence Approach for Customer Journey Optimization

---

## 1. Project Overview & Business Domain

Digital performance marketing involves acquiring prospects across paid search, organic, social, display, and email channels. Marketing managers receive impressions, clicks, conversions, and ad spend metrics in isolated silos across multiple platforms. Consequently, marketing leadership cannot reliably reconstruct end-to-end customer journeys or pinpoint where prospects drop out of the conversion funnel.

This project delivers an enterprise-grade **Business Intelligence solution** providing:
* Centralized data integration via an automated Python ETL pipeline.
* A dimensional **Star Schema** data warehouse hosted on MySQL.
* Systematic **Funnel Leakage Intelligence** tracking drop-offs across all 7 stages.
* Comprehensive **Cross-Channel Marketing Attribution & ROI Optimization**.
* Analytical views and DAX specifications for executive and operational Power BI reporting.

---

## 2. The 7-Stage Conversion Funnel

```
[ IMPRESSION ]  --> Top of Funnel (Brand Awareness, Ad Impressions)
       ↓
[ CLICK ]       --> Traffic Acquisition (Ad Clicks, External Links)
       ↓
[ LANDING PAGE]--> Site Arrival & First Session Touchpoint
       ↓
[ PRODUCT VIEW]--> Engagement & Consideration (Catalog/Product Interaction)
       ↓
[ CART ]        --> Purchase Intent (Item Added to Shopping Bag)
       ↓
[ CHECKOUT ]    --> High-Intent Action (Initiation of Payment/Address Flow)
       ↓
[ PURCHASE ]    --> Conversion & Revenue Realization
```

---

## 3. Architecture & Data Pipeline

```
Raw Sources (GA4 Export, Ad Spend, Campaign Metadata, API Adapters)
                               ↓
                 [EXTRACT] - etl/extract.py
                               ↓
               [TRANSFORM] - etl/transform.py
         (Normalization, Funnel Mapping, Deduplication)
                               ↓
                [VALIDATE] - etl/validate.py
            (34 Data Quality & Integrity Checks)
                               ↓
                   [LOAD] - etl/load.py
       (Dimension-First Ingestion, Transactions, Indexes)
                               ↓
          MySQL Analytical Warehouse (Star Schema)
       (Fact_FunnelEvent + 6 Dimensions + 8 Views)
                               ↓
         Power BI Desktop Interactive Dashboards
```

---

## 4. Star Schema Warehouse Design

### Central Fact Table: `Fact_FunnelEvent`
* **Grain**: One record = One standardized funnel event for a user/session.
* **Measures**: `Ad_Spend`, `Revenue`, `Conversion_Flag`.
* **Surrogate Keys**: `Channel_ID`, `Campaign_ID`, `LandingPage_ID`, `Device_ID`, `Geography_ID`, `Date_ID`.

### Dimension Tables:
1. **`Dim_Date`**: Full calendar breakdown (Year, Quarter, Month, Week, Day of Week, Is_Weekend).
2. **`Dim_Channel`**: Marketing channels (Organic Search, Paid Search, Social, Display, Email, Direct).
3. **`Dim_Campaign`**: Campaign metadata (Objective, Monthly Budget).
4. **`Dim_LandingPage`**: Entry URL classification (Home, Category, Product, Checkout).
5. **`Dim_Device`**: Hardware & software environment (Device Type, Operating System, Browser).
6. **`Dim_Geography`**: Geographic attribution (Country, Region, City).

---

## 5. Directory Structure

```
business-intelligence-funnel-leakage/
│
├── README.md                      # Complete Project Documentation
├── PROJECT_STATUS.md              # Environment & Execution Status
├── requirements.txt               # Exact Python Dependencies
├── .gitignore                     # Git Exclusions (venv, env, pycache)
├── .env.example                   # Environment Configuration Template
│
├── data/
│   ├── raw/
│   │   ├── ga4/                   # GA4 Event Export, Campaign, Ad Spend
│   │   ├── google_ads/            # Google Ads Adapter Directory
│   │   ├── meta/                  # Meta Marketing Adapter Directory
│   │   ├── hubspot/               # HubSpot CRM Adapter Directory
│   │   └── email/                 # Email Campaign Adapter Directory
│   ├── processed/                 # Warehouse Staging CSVs
│   └── validation/                # Data Quality Audit Reports
│
├── etl/
│   ├── __init__.py
│   ├── config.py                  # Pipeline Configuration & Paths
│   ├── extract.py                 # Multi-Source Extraction Handlers
│   ├── transform.py               # Star Schema Normalization Logic
│   ├── validate.py                # 34-Check Automated Validation Engine
│   ├── load.py                    # MySQL Warehouse Ingestion Engine
│   └── run_pipeline.py            # CLI Orchestrator
│
├── sql/
│   ├── 01_create_database.sql     # Database Initialization
│   ├── 02_create_dimensions.sql   # Star Schema Dimension Tables
│   ├── 03_create_fact.sql         # Fact Table with FK Constraints
│   ├── 04_indexes.sql             # Performance Optimization Indexes
│   ├── 05_views.sql               # Pre-Built Analytical Views
│   ├── 06_kpi_queries.sql         # 22 Analytical & Funnel KPI Queries
│   └── 07_validation_queries.sql  # Integrity & Reconciliation Queries
│
├── docs/
│   ├── architecture.md            # System Architecture & Flow
│   ├── data_dictionary.md         # Schema & Column Level Dictionary
│   ├── source_mapping.md          # Raw-to-Canonical Field Mapping
│   ├── etl_documentation.md       # ETL Process & Transformation Spec
│   ├── warehouse_documentation.md # Star Schema Physical Model
│   ├── validation_report.md       # Data Quality & Profiling Report
│   ├── business_insights.md       # Empirical Findings & Recommendations
│   └── TAE2_REQUIREMENT_MAPPING.md# Academic Assessment Criteria Mapping
│
├── powerbi/
│   ├── README.md                  # Power BI Overview
│   ├── POWERBI_SETUP_GUIDE.md     # Step-by-Step Connection & Build Guide
│   ├── dashboard_specification.md # 4-Page Dashboard Layout & Visual Guide
│   └── dax_measures.md            # Production DAX Formulas
│
├── tests/
│   ├── test_transform.py          # Transformation Unit Tests
│   ├── test_validation.py         # Data Quality Validation Tests
│   └── test_kpis.py               # KPI Calculation Unit Tests
│
└── presentation/
    ├── presentation_outline.md    # 19-Slide Evaluator Slide Outline
    └── demo_script.md             # Turn-by-Turn Live Demo Walkthrough
```

---

## 6. Installation & Execution Guide

### Prerequisites
* Python 3.10+ (Verified on Python 3.13.0)
* MySQL 8.0+
* Microsoft Power BI Desktop

### 1. Clone & Configure
```bash
git clone <repo_url>
cd business-intelligence-funnel-leakage
cp .env.example .env
```
Edit `.env` with your MySQL credentials:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_NAME=marketing_funnel_dw
DB_USER=root
DB_PASSWORD=your_mysql_password
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
pytest tests/ -v
```
*(All 52 unit tests validate funnel mapping, schema constraints, and KPI logic).*

### 4. Execute the ETL Pipeline
To run the full pipeline including warehouse load:
```bash
python -m etl.run_pipeline
```
To run in CSV staging mode without connecting to a live database:
```bash
python -m etl.run_pipeline --no-db
```

### 5. Connect Power BI
Follow instructions in `powerbi/POWERBI_SETUP_GUIDE.md` to import warehouse tables, apply DAX measures from `powerbi/dax_measures.md`, and build the 4-page dashboard report.
