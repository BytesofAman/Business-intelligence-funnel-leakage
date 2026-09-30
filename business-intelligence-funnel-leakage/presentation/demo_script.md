# Live Demonstration Script: TAE 2 Evaluator Walkthrough

**Course**: Business Intelligence (TAE 2 Assessment)  
**Estimated Demonstration Time**: 7 to 10 Minutes  
**Student Split**: Student 1 (Steps 1–5: Architecture, Data, ETL) | Student 2 (Steps 6–10: Data Warehouse, SQL, Power BI, Insights)

---

## Part 1: Architecture, Data, & ETL Pipeline (Student 1)

### Step 1: Open the Project & Show Clean Structure (1 Minute)
* **Action**: Open terminal in project root `business-intelligence-funnel-leakage/`.
* **Speak**: 
  > *"Good afternoon, respected faculty. For our Business Intelligence TAE 2 project, we have engineered an end-to-end analytical solution titled 'Cross-Channel Marketing Funnel Leakage Intelligence'. As shown in our repository, we have established a modular, enterprise-grade architecture separating raw ingestion, Python ETL, SQL data warehousing, automated testing, and Power BI dashboards."*

### Step 2: Show Raw Data & Explain Ingestion Strategy (1 Minute)
* **Action**: Display `data/raw/ga4/` files in terminal or VS Code explorer.
* **Speak**:
  > *"Our behavioral event dataset reflects 57,083 customer journey events modeled on the Google Merchandise Store GA4 BigQuery export, coupled with campaign ad expenditure records. To respect project rules, our external API adapters for Google Ads, Meta, and HubSpot are structured in Python without fabricating unauthenticated live calls."*

### Step 3: Run Automated Test Suite (1 Minute)
* **Action**: Run terminal command:
  ```bash
  pytest tests/ -v
  ```
* **Speak**:
  > *"Before running the pipeline, we demonstrate our automated testing framework. 52 pytest unit tests validate our event normalization logic, funnel stage sequencing, foreign key constraints, and KPI calculations with 100% passing results."*

### Step 4: Execute the ETL Pipeline (1.5 Minutes)
* **Action**: Run terminal command:
  ```bash
  python -m etl.run_pipeline --no-db
  ```
  *(Or `python -m etl.run_pipeline` if MySQL is connected)*
* **Speak**:
  > *"Here we execute our automated Python ETL orchestrator. In Phase 1, it extracts the multi-channel datasets. In Phase 2, it executes a 15-step transformation pipeline—normalizing timestamps, classifying conformed channels, attributing ad spend, and building our Star Schema. In Phase 3, our validation engine executes 34 data quality checks with 0 errors, validating 57,083 clean events."*

---

## Part 2: Data Warehouse, Power BI, & Insights (Student 2)

### Step 5: Show the Star Schema Data Warehouse (1.5 Minutes)
* **Action**: Open MySQL Workbench or display `sql/02_create_dimensions.sql` and `sql/03_create_fact.sql`.
* **Speak**:
  > *"The analytical backbone of our system is a dimensional Star Schema. The central fact table, `Fact_FunnelEvent`, maintains a grain of one record per standardized customer journey event. It is surrounded by 6 conformed dimensions: Date, Channel, Campaign, Landing Page, Device, and Geography, complete with B-Tree composite indexes for sub-second aggregations."*

### Step 6: Execute an Analytical KPI Query in SQL (1 Minute)
* **Action**: Run query from `sql/06_kpi_queries.sql` (e.g., Query 8 or Query 17):
  ```sql
  SELECT * FROM vw_channel_performance ORDER BY Total_Revenue DESC;
  ```
* **Speak**:
  > *"Here we run our pre-aggregated analytical view in SQL. We observe total users, purchases, revenue, ad spend, CPA, and ROAS broken down by marketing channel. Notice how these exact figures will reconcile identically with our Power BI measures."*

### Step 7: Power BI Dashboard Walkthrough (2 Minutes)
* **Action**: Open Power BI Desktop showing the 4 dashboard pages.
* **Speak**:
  > *"In Power BI Desktop, we connect directly to our Star Schema.
  > On **Page 1 (Executive Overview)**, leadership tracks our \$355K in gross revenue against \$243K in ad spend, yielding an overall ROAS of 1.46x.
  > On **Page 2 (Funnel Leakage)**, our 7-stage visual funnel immediately isolates the primary leakage point: a 54.3% drop-off between landing page arrival and product catalog views.
  > On **Page 3 (Channel Matrix)**, our campaign efficiency scatter plot clearly separates high-performing retargeting campaigns (ROAS 3.84x) from top-of-funnel awareness campaigns.
  > Finally, on **Page 4 (Customer Segmentation)**, we observe that while mobile drives 56% of traffic, it experiences higher checkout abandonment (42%) compared to desktop (28%)."*

### Step 8: Concluding Recommendations (1 Minute)
* **Speak**:
  > *"Based on these empirical findings, we recommend reallocating 15-20% of display ad spend into dynamic retargeting, and streamlining the mobile checkout flow with digital wallet integration. This completes our end-to-end demonstration. Thank you."*
