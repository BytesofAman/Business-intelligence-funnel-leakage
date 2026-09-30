# TAE 2 Academic Assessment Requirement Mapping

**Course**: Business Intelligence (TAE 2 — Winter 2026)  
**Program**: B.Tech Computer Science & Engineering (Data Science)  
**Institution**: G H Raisoni College of Engineering and Management

---

## 1. Compliance Matrix

| TAE 2 Assessment Component | Prescribed Requirement | Delivered Artifact / Implementation Evidence | Verification Method |
|:---|:---|:---|:---|
| **Data Ingestion & Integration** | Ingest fragmented multi-channel marketing & journey data without fabricated calls. | `etl/extract.py`, `data/raw/ga4/` (57,083 GA4 events, 1,830 ad spend records, 7 campaigns), structured API stubs for Google Ads, Meta, HubSpot, Email. | Inspect `extract.py` and run extraction step. |
| **Data Warehouse & Schema** | Centralized SQL DW with dimensional Star Schema modeling. | `sql/01_create_database.sql`, `sql/02_create_dimensions.sql`, `sql/03_create_fact.sql`, `sql/04_indexes.sql`. | Review SQL scripts & table definitions in MySQL. |
| **ETL Pipeline** | Automated Python ETL performing Extract, Clean, Transform, Validate, and Load. | Modular Python modules: `etl/extract.py`, `etl/transform.py`, `etl/validate.py`, `etl/load.py`, `etl/run_pipeline.py`. | Run `python -m etl.run_pipeline`. |
| **Data Quality & Audit** | Explicit validation checks, rejected data logging, zero-silent-drop policy. | `etl/validate.py` executing 34 automated checks; outputs `data/validation/validation_report.csv` and terminal report. | Run `pytest tests/test_validation.py`. |
| **Funnel Leakage Intelligence**| Measure continuous progression across the 7 approved funnel stages. | Canonical mapping in `etl/transform.py`, SQL view `vw_funnel_conversion`, and Page 2 Power BI specification. | Execute query 8 in `sql/06_kpi_queries.sql`. |
| **Attribution & Marketing KPIs**| Calculate Users, Sessions, Purchases, Revenue, Ad Spend, CPA, ROAS, Drop-Off. | Implemented in SQL (`sql/06_kpi_queries.sql`), Python (`etl/transform.py`), DAX (`powerbi/dax_measures.md`), and unit tests (`tests/test_kpis.py`). | Run `pytest tests/test_kpis.py`. |
| **Power BI Dashboards** | Interactive multi-page dashboard model with clean business style. | `powerbi/dashboard_specification.md`, `powerbi/POWERBI_SETUP_GUIDE.md`, and 4 distinct page architectures. | Follow setup guide in Power BI Desktop. |
| **Empirical Insights** | Data-driven findings following Observation-Evidence-Implication framework. | `docs/business_insights.md` with quantified funnel bottleneck and attribution discoveries. | Review insights document. |
| **Testing & CI/CD Quality** | Automated unit tests covering ETL, normalization, and KPIs. | `tests/test_transform.py`, `tests/test_validation.py`, `tests/test_kpis.py` (52 automated pytest tests passing). | Run `pytest tests/ -v`. |
| **Evaluation Demonstration** | Documented presentation slides and executable demonstration script. | `presentation/presentation_outline.md` (19 slides) and `presentation/demo_script.md` (step-by-step live demo). | Conduct live walkthrough. |
| **GitHub Reproducibility** | Ready for version control with no hardcoded credentials. | Clean root repository, `.gitignore`, `.env.example`, and clean `git status`. | Check `git status` and commit history. |
