# Step-by-Step Power BI Desktop Setup Guide

---

## 1. Connecting Power BI to the Data Source

You can connect Power BI to either the **live MySQL Data Warehouse** or the **staged CSV files** located in `data/processed/`.

### Option A: Direct Connection to MySQL Database (Recommended)
1. Launch **Power BI Desktop**.
2. Click **Get Data** on the Home ribbon and select **MySQL database**.
3. In the connection dialog:
   * **Server**: `localhost:3306` (or `localhost`)
   * **Database**: `marketing_funnel_dw`
   * **Data Connectivity mode**: Select **Import** (recommended for best DAX calculation performance).
4. Enter MySQL credentials:
   * **User name**: `root`
   * **Password**: `your_mysql_password`
5. In the Navigator pane, check all core tables:
   * `Fact_FunnelEvent`
   * `Dim_Date`
   * `Dim_Channel`
   * `Dim_Campaign`
   * `Dim_LandingPage`
   * `Dim_Device`
   * `Dim_Geography`
6. Click **Load**.

### Option B: Fast Import via Staged CSV Files
If MySQL is not currently running or credentials are unavailable:
1. Open Power BI Desktop.
2. Select **Get Data** -> **Text/CSV**.
3. Navigate to `business-intelligence-funnel-leakage/data/processed/` and load:
   * `fact_funnel_event.csv`
   * `dim_date.csv`
   * `dim_channel.csv`
   * `dim_campaign.csv`
   * `dim_landing_page.csv`
   * `dim_device.csv`
   * `dim_geography.csv`

---

## 2. Configuring Model Relationships

Switch to the **Model View** (left navigation bar icon) and establish the following 1-to-Many relationships:

| From Table (Dimension) | From Column (PK) | To Table (Fact) | To Column (FK) | Cardinality | Cross Filter |
|:---|:---|:---|:---|:---:|:---:|
| `Dim_Date` | `Date_ID` | `Fact_FunnelEvent` | `Date_ID` | 1 to Many (`1:*`) | Single |
| `Dim_Channel` | `Channel_ID` | `Fact_FunnelEvent` | `Channel_ID` | 1 to Many (`1:*`) | Single |
| `Dim_Campaign` | `Campaign_ID` | `Fact_FunnelEvent` | `Campaign_ID` | 1 to Many (`1:*`) | Single |
| `Dim_LandingPage` | `LandingPage_ID`| `Fact_FunnelEvent` | `LandingPage_ID`| 1 to Many (`1:*`) | Single |
| `Dim_Device` | `Device_ID` | `Fact_FunnelEvent` | `Device_ID` | 1 to Many (`1:*`) | Single |
| `Dim_Geography` | `Geography_ID` | `Fact_FunnelEvent` | `Geography_ID` | 1 to Many (`1:*`) | Single |

---

## 3. Creating DAX Measures

1. In the **Report View**, click **New Measure** on the Home ribbon.
2. Copy and paste each measure from `powerbi/dax_measures.md`.
3. Format currency measures (`Total Revenue`, `Total Ad Spend`, `CPA`) as **Currency (\$ USD)**.
4. Format percentage measures (`Conversion Rate`, `ROAS`, `Cart Abandonment Rate`) as **Percentage (%)**.

---

## 4. Building the 4 Dashboard Pages

Refer to `powerbi/dashboard_specification.md` for exact visual choices, axis bindings, and layout structure for:
* Page 1: Executive Overview
* Page 2: Funnel Leakage & Drop-Off
* Page 3: Channel & Campaign Matrix
* Page 4: Customer & Segment Intelligence

Save the finished workbook as `CrossChannel_Funnel_Intelligence.pbix` inside the `powerbi/` directory.
