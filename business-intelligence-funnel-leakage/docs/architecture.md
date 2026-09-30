# System Architecture Documentation

## 1. High-Level Architecture

The system is architected as a modular, decoupled Business Intelligence and Decision Support pipeline designed to process granular digital marketing events into an analytical Star Schema data warehouse, exposing optimized views and DAX metrics for Power BI Desktop.

```mermaid
flowchart TD
    subgraph Ingestion ["1. Data Ingestion & Sources"]
        S1["GA4 Web Events (Google Merchandise Store)"]
        S2["Campaign Reference Metadata"]
        S3["Daily Ad Spend by Channel"]
        S4["Google Ads API (Adapter Ready)"]
        S5["Meta Marketing API (Adapter Ready)"]
        S6["HubSpot CRM (Adapter Ready)"]
        S7["Email Platform (Adapter Ready)"]
    end

    subgraph Pipeline ["2. Automated ETL Pipeline (Python)"]
        E["extract.py - Source Extractors"]
        T["transform.py - 15-Stage Star Schema Transformation"]
        V["validate.py - 34 Automated Quality Checks"]
        L["load.py - Dimension-First Database Loader"]
    end

    subgraph DW ["3. MySQL Data Warehouse (Star Schema)"]
        F["Fact_FunnelEvent (Grain: 1 Event/Session)"]
        D1["Dim_Date"]
        D2["Dim_Channel"]
        D3["Dim_Campaign"]
        D4["Dim_LandingPage"]
        D5["Dim_Device"]
        D6["Dim_Geography"]
        VW["Analytical Views (vw_funnel_summary, etc.)"]
    end

    subgraph BI ["4. Analytical & Presentation Layer"]
        P1["Page 1: Executive Overview"]
        P2["Page 2: Funnel Leakage & Abandonment"]
        P3["Page 3: Channel & Campaign Performance"]
        P4["Page 4: Customer Segmentation & Geography"]
    end

    S1 & S2 & S3 & S4 & S5 & S6 & S7 --> E
    E --> T
    T --> V
    V --> L
    L --> F
    D1 & D2 & D3 & D4 & D5 & D6 --> F
    F --> VW
    VW --> BI
    F --> BI
```

## 2. Ingestion Tier
* **Primary Digital Event Source**: Google Analytics 4 (GA4) export capturing granular user actions (`session_start`, `page_view`, `view_item`, `add_to_cart`, `begin_checkout`, `purchase`).
* **Campaign & Channel Metadata**: Campaign mapping tables standardizing campaign identifiers, objectives, and channel groupings.
* **Ad Spend Integration**: Daily expenditure datasets per campaign allowing accurate calculation of CPA and ROAS.
* **External API Adapters**: Pre-built adapter interfaces for Google Ads, Meta Marketing API, HubSpot CRM, and Email platforms configured to gracefully handle unauthenticated environments without fabricated live calls.

## 3. Transformation & Normalization Tier
* **Event Deduplication**: Filters identical `event_id` occurrences preserving data integrity.
* **Funnel Mapping**: Maps heterogeneous platform events into a canonical 7-stage funnel model:
  1. `IMPRESSION`
  2. `CLICK`
  3. `LANDING_PAGE`
  4. `PRODUCT_VIEW`
  5. `CART`
  6. `CHECKOUT`
  7. `PURCHASE`
* **Spend Attribution**: Allocates daily spend across top-of-funnel impression records avoiding downstream multi-touch double-counting.
* **Dimension Normalization**: Extracts unique entities and assigns deterministic surrogate primary keys.

## 4. Star Schema Storage Tier
* **Fact Table**: `Fact_FunnelEvent` enforces referential integrity via strict foreign keys to all six dimension tables.
* **Indexing Strategy**: B-Tree composite indexes on `(Funnel_Stage, Date_ID)`, `(Channel_ID, Funnel_Stage)`, and `(Campaign_ID, Funnel_Stage)` guarantee sub-second analytical query responses.
* **Pre-Aggregated Views**: 8 specialized views (`vw_funnel_summary`, `vw_channel_performance`, `vw_device_performance`, etc.) serve as optimized data sources for BI tools.
