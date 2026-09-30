# Data Dictionary: Marketing Funnel Star Schema

---

## 1. Central Fact Table: `Fact_FunnelEvent`

**Table Description**: Stores individual standardized marketing funnel events generated during user sessions.  
**Table Grain**: One record per standardized customer journey event.

| Column Name | Data Type | Nullable | Key Type | Description / Example |
|:---|:---|:---|:---|:---|
| `Event_ID` | `VARCHAR(36)` | No | PK | Unique UUID identifying the specific event occurrence. |
| `User_ID` | `VARCHAR(100)` | No | - | Pseudonymized unique identifier for the customer/user. |
| `Session_ID` | `VARCHAR(100)` | No | - | Session token grouping interactions within a continuous visit. |
| `Campaign_ID` | `VARCHAR(10)` | Yes | FK | References `Dim_Campaign(Campaign_ID)`. e.g., 'C001'. |
| `Channel_ID` | `INT` | Yes | FK | References `Dim_Channel(Channel_ID)`. |
| `LandingPage_ID` | `INT` | Yes | FK | References `Dim_LandingPage(LandingPage_ID)`. |
| `Device_ID` | `INT` | Yes | FK | References `Dim_Device(Device_ID)`. |
| `Geography_ID` | `INT` | Yes | FK | References `Dim_Geography(Geography_ID)`. |
| `Date_ID` | `INT` | Yes | FK | References `Dim_Date(Date_ID)`. Format: YYYYMMDD. |
| `Funnel_Stage` | `VARCHAR(20)` | No | - | One of: IMPRESSION, CLICK, LANDING_PAGE, PRODUCT_VIEW, CART, CHECKOUT, PURCHASE. |
| `Event_Timestamp` | `DATETIME` | No | - | Exact timestamp of event occurrence. |
| `Source_Platform` | `VARCHAR(100)` | Yes | - | Origin platform (e.g., google, facebook, direct, email). |
| `Ad_Spend` | `DECIMAL(12,4)` | No | Measure | Allocated advertising expenditure in USD (allocated to top-of-funnel events). |
| `Revenue` | `DECIMAL(12,4)` | No | Measure | Monies generated in USD (populated only on PURCHASE events). |
| `Conversion_Flag` | `TINYINT(1)` | No | Flag | Binary indicator (1 for PURCHASE events, 0 otherwise). |

---

## 2. Dimension Tables

### `Dim_Date`
**Description**: Calendar dimension supporting temporal analysis, quarter rollups, and day-of-week trends.

| Column Name | Data Type | Nullable | Key Type | Description / Example |
|:---|:---|:---|:---|:---|
| `Date_ID` | `INT` | No | PK | Integer key in `YYYYMMDD` format (e.g., 20240315). |
| `Date` | `DATE` | No | Unique | Full calendar date (e.g., 2024-03-15). |
| `Day_of_Week` | `VARCHAR(10)` | No | - | Day name: Monday, Tuesday, etc. |
| `Day_of_Month` | `INT` | No | - | Numeric day: 1 to 31. |
| `Week` | `INT` | No | - | ISO calendar week number (1 to 53). |
| `Month` | `INT` | No | - | Numeric month: 1 to 12. |
| `Month_Name` | `VARCHAR(10)` | No | - | Month name: January, February, etc. |
| `Quarter` | `INT` | No | - | Calendar quarter: 1 to 4. |
| `Year` | `INT` | No | - | Calendar year (e.g., 2024). |
| `Is_Weekend` | `TINYINT(1)` | No | - | 1 for Saturday/Sunday, 0 for weekdays. |

---

### `Dim_Channel`
**Description**: Standardized marketing acquisition channels and traffic groupings.

| Column Name | Data Type | Nullable | Key Type | Description / Example |
|:---|:---|:---|:---|:---|
| `Channel_ID` | `INT AUTO_INCREMENT`| No | PK | Surrogate primary key. |
| `Channel_Name` | `VARCHAR(100)` | No | Unique | Standardized name (e.g., Paid Search, Organic Search, Social, Display, Email, Direct). |
| `Platform` | `VARCHAR(100)` | Yes | - | Associated primary platform (e.g., Google, Meta, Email Provider). |
| `Campaign_Type` | `VARCHAR(100)` | Yes | - | Typical campaign classification (e.g., Brand, Retargeting, Awareness). |

---

### `Dim_Campaign`
**Description**: Individual marketing campaign attributes and budget limits.

| Column Name | Data Type | Nullable | Key Type | Description / Example |
|:---|:---|:---|:---|:---|
| `Campaign_ID` | `VARCHAR(10)` | No | PK | Business key (e.g., C001, C002). |
| `Campaign_Name` | `VARCHAR(200)` | No | Unique | Descriptive name (e.g., google_cpc_brand, facebook_retarget). |
| `Objective` | `VARCHAR(100)` | Yes | - | Goal: Traffic, Conversions, Awareness, Revenue. |
| `Budget` | `DECIMAL(12,2)` | Yes | - | Planned monthly budget allocation in USD. |

---

### `Dim_LandingPage`
**Description**: Catalog entry points and page classifications.

| Column Name | Data Type | Nullable | Key Type | Description / Example |
|:---|:---|:---|:---|:---|
| `LandingPage_ID` | `INT AUTO_INCREMENT`| No | PK | Surrogate primary key. |
| `Page_URL` | `VARCHAR(500)` | No | Unique | Relative site path (e.g., /products/apparel, /home). |
| `Page_Category` | `VARCHAR(100)` | Yes | - | Page group: Apparel, Bags, Electronics, Drinkware, Cart, Checkout. |

---

### `Dim_Device`
**Description**: Technical client environment including device form factor, OS, and browser.

| Column Name | Data Type | Nullable | Key Type | Description / Example |
|:---|:---|:---|:---|:---|
| `Device_ID` | `INT AUTO_INCREMENT`| No | PK | Surrogate primary key. |
| `Device_Type` | `VARCHAR(50)` | No | - | Device category: mobile, desktop, tablet. |
| `OS` | `VARCHAR(100)` | Yes | - | Operating system: Windows, Macintosh, iOS, Android, Linux. |
| `Browser` | `VARCHAR(100)` | Yes | - | Browser client: Chrome, Safari, Firefox, Edge. |

---

### `Dim_Geography`
**Description**: Regional location coordinates for geographic segmentation.

| Column Name | Data Type | Nullable | Key Type | Description / Example |
|:---|:---|:---|:---|:---|
| `Geography_ID` | `INT AUTO_INCREMENT`| No | PK | Surrogate primary key. |
| `Country` | `VARCHAR(100)` | No | - | Country code / name (e.g., US, India, UK, Germany). |
| `Region` | `VARCHAR(200)` | Yes | - | State or province division. |
| `City` | `VARCHAR(200)` | Yes | - | Municipality / City name. |
