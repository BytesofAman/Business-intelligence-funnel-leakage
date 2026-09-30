# DATA DICTIONARY: MARKETING FUNNEL WAREHOUSE

**Database**: `marketing_funnel_dw`  
**RDBMS**: MySQL Community Server 8.0.42

---

## 1. Fact Table: `Fact_FunnelEvent`

**Table Description**: Central fact table storing standardized customer journey interactions across marketing channels.  
**Table Grain**: One record = One standardized customer journey event for a user/session at a specific funnel stage.

| Column Name | SQL Type | Nullable | Key Type | Business Meaning & Format |
|:---|:---|:---:|:---:|:---|
| `Event_ID` | `VARCHAR(36)` | No | PK | Globally unique UUID assigned to each journey interaction. |
| `User_ID` | `VARCHAR(100)` | No | - | Pseudonymized customer identifier (`user_pseudo_id`). |
| `Session_ID` | `VARCHAR(100)` | No | - | Session grouping token (`ga_session_id`). |
| `Campaign_ID` | `VARCHAR(10)` | Yes | FK | References `Dim_Campaign(Campaign_ID)`. e.g., 'C001'. |
| `Channel_ID` | `INT` | Yes | FK | References `Dim_Channel(Channel_ID)`. |
| `LandingPage_ID` | `INT` | Yes | FK | References `Dim_LandingPage(LandingPage_ID)`. |
| `Device_ID` | `INT` | Yes | FK | References `Dim_Device(Device_ID)`. |
| `Geography_ID` | `INT` | Yes | FK | References `Dim_Geography(Geography_ID)`. |
| `Date_ID` | `INT` | Yes | FK | References `Dim_Date(Date_ID)`. Format: YYYYMMDD. |
| `Funnel_Stage` | `VARCHAR(20)` | No | - | One of: IMPRESSION, CLICK, LANDING_PAGE, PRODUCT_VIEW, CART, CHECKOUT, PURCHASE. |
| `Event_Timestamp`| `DATETIME` | No | - | Event timestamp normalized to UTC. |
| `Source_Platform`| `VARCHAR(100)` | Yes | - | Origin traffic source (e.g., google, facebook, direct, email). |
| `Ad_Spend` | `DECIMAL(12,4)`| No | Measure | Allocated ad spend in USD (attributed strictly to IMPRESSION events). |
| `Revenue` | `DECIMAL(12,4)`| No | Measure | Purchase monetary value in USD (strictly non-zero on PURCHASE events). |
| `Conversion_Flag`| `TINYINT(1)` | No | Measure | Binary indicator: 1 if `Funnel_Stage = 'PURCHASE'`, else 0. |

---

## 2. Dimension Tables

### 2.1 `Dim_Date`
| Column Name | SQL Type | Nullable | Key Type | Description & Example |
|:---|:---|:---:|:---:|:---|
| `Date_ID` | `INT` | No | PK | Surrogate key in `YYYYMMDD` integer format (e.g., 20240101). |
| `Date` | `DATE` | No | Unique | Calendar date (`2024-01-01`). |
| `Day_of_Week` | `VARCHAR(10)` | No | - | Day name (Monday, Tuesday, etc.). |
| `Day_of_Month`| `INT` | No | - | Day index within month (1–31). |
| `Week` | `INT` | No | - | ISO week number (1–53). |
| `Month` | `INT` | No | - | Calendar month integer (1–12). |
| `Month_Name` | `VARCHAR(10)` | No | - | Month name (January, February, etc.). |
| `Quarter` | `INT` | No | - | Calendar quarter (1–4). |
| `Year` | `INT` | No | - | 4-digit calendar year (e.g., 2024). |
| `Is_Weekend` | `TINYINT(1)` | No | - | 1 if Saturday or Sunday, 0 if weekday. |

### 2.2 `Dim_Channel`
| Column Name | SQL Type | Nullable | Key Type | Description & Example |
|:---|:---|:---:|:---:|:---|
| `Channel_ID` | `INT AUTO_INCREMENT` | No | PK | Surrogate primary key. |
| `Channel_Name` | `VARCHAR(100)` | No | Unique | Standard marketing channel: Paid Search, Organic Search, Social, Email, Direct. |
| `Platform` | `VARCHAR(100)` | Yes | - | Underlying platform: Google, Meta, Email Platform, Direct. |
| `Campaign_Type`| `VARCHAR(100)` | Yes | - | Classification: Brand, Traffic, Retargeting, Engagement. |

### 2.3 `Dim_Campaign`
| Column Name | SQL Type | Nullable | Key Type | Description & Example |
|:---|:---|:---:|:---:|:---|
| `Campaign_ID` | `VARCHAR(10)` | No | PK | Business key (e.g., C001, C002). |
| `Campaign_Name` | `VARCHAR(200)` | No | Unique | Descriptive campaign name (e.g., `google_cpc_brand`). |
| `Objective` | `VARCHAR(100)` | Yes | - | Goal: Conversions, Traffic, Awareness, Engagement. |
| `Budget` | `DECIMAL(12,2)` | Yes | - | Monthly budget allocation in USD. |

### 2.4 `Dim_LandingPage`
| Column Name | SQL Type | Nullable | Key Type | Description & Example |
|:---|:---|:---:|:---:|:---|
| `LandingPage_ID` | `INT AUTO_INCREMENT` | No | PK | Surrogate primary key. |
| `Page_URL` | `VARCHAR(500)` | No | Unique | Entry site path (e.g., `/home`, `/products/apparel`, `/products/bags`). |
| `Page_Category` | `VARCHAR(100)` | Yes | - | Catalog grouping: Home, Apparel, Bags. |

### 2.5 `Dim_Device`
| Column Name | SQL Type | Nullable | Key Type | Description & Example |
|:---|:---|:---:|:---:|:---|
| `Device_ID` | `INT AUTO_INCREMENT` | No | PK | Surrogate primary key. |
| `Device_Type` | `VARCHAR(50)` | No | Composite UK | Form factor: mobile, desktop, tablet. |
| `OS` | `VARCHAR(100)` | Yes | Composite UK | Operating system: iOS, Android, Windows, Macintosh, Linux. |
| `Browser` | `VARCHAR(100)` | Yes | Composite UK | Browser client: Chrome, Safari, Firefox, Edge, Samsung Internet. |

### 2.6 `Dim_Geography`
| Column Name | SQL Type | Nullable | Key Type | Description & Example |
|:---|:---|:---:|:---:|:---|
| `Geography_ID` | `INT AUTO_INCREMENT` | No | PK | Surrogate primary key. |
| `Country` | `VARCHAR(100)` | No | Composite UK | Country code: US, India, UK, Canada, France, Australia, Germany, Japan, Brazil, Mexico. |
| `Region` | `VARCHAR(200)` | Yes | Composite UK | State or province division (e.g., Region_1 to Region_50). |
| `City` | `VARCHAR(200)` | Yes | Composite UK | Municipality / City name (e.g., City_1 to City_100). |
