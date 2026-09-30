# Source-to-Canonical Field Mapping Specification

This document details how heterogeneous raw data sources are mapped, standardized, and harmonized into the canonical data warehouse Star Schema.

---

## 1. Funnel Event Normalization

| Raw GA4 `event_name` | Canonical `Funnel_Stage` | Stage Order | Business Meaning & Funnel Context |
|:---|:---|:---:|:---|
| `session_start` | `IMPRESSION` | 1 | Entry point and session initialization. |
| `first_visit` | `IMPRESSION` | 1 | New visitor acquisition event. |
| `click` | `CLICK` | 2 | Ad engagement or external/promotional click. |
| `page_view` | `LANDING_PAGE` | 3 | Visitor rendered entry landing page. |
| `view_item` | `PRODUCT_VIEW` | 4 | Consideration stage: viewing detailed product page. |
| `add_to_cart` | `CART` | 5 | Intent stage: adding item to shopping basket. |
| `begin_checkout` | `CHECKOUT` | 6 | High-intent stage: navigating to checkout process. |
| `purchase` | `PURCHASE` | 7 | Conversion stage: completing financial transaction. |

---

## 2. Marketing Medium to Channel Mapping

| Raw `traffic_source_medium` | Canonical `Channel_Name` | Default Platform |
|:---|:---|:---|
| `cpc` | `Paid Search` | Google / Bing |
| `organic` | `Organic Search` | Search Engines (Google, Bing, Yahoo) |
| `social` | `Social` | Meta / Instagram / YouTube |
| `email` | `Email` | CRM / Email Platform |
| `display` | `Display` | Google Display Network |
| `referral` | `Referral` | External Affiliate Sites |
| `direct`, `(none)`, `NULL` | `Direct` | Direct URL Entry |

---

## 3. Fact Table Field Mapping

| Canonical Field | Raw GA4 / Source Field | Transformation Rule |
|:---|:---|:---|
| `Event_ID` | `event_id` | Deduplicated UUID string. |
| `User_ID` | `user_pseudo_id` | Hashed/pseudonymized customer identifier. |
| `Session_ID` | `ga_session_id` | Unique session token cast to string. |
| `Campaign_ID` | `traffic_source_name` | Cross-referenced against `campaign_data.csv` lookup. |
| `Channel_ID` | `traffic_source_medium` | Surrogate key resolved from `Dim_Channel`. |
| `LandingPage_ID` | `landing_page` | Normalized path resolved from `Dim_LandingPage`. |
| `Device_ID` | `device_category` + OS + Browser | Surrogate key resolved from `Dim_Device`. |
| `Geography_ID` | `geo_country` + Region + City | Surrogate key resolved from `Dim_Geography`. |
| `Date_ID` | `event_date` / `event_timestamp` | Integer `YYYYMMDD` surrogate key resolved from `Dim_Date`. |
| `Funnel_Stage` | `event_name` | Mapped via `GA4_EVENT_MAPPING` dictionary. |
| `Event_Timestamp`| `event_timestamp` | Unix microseconds converted to UTC `DATETIME`. |
| `Source_Platform`| `traffic_source_source` | Platform string (e.g., google, meta, direct). |
| `Ad_Spend` | `ad_spend.csv` (`daily_spend`) | Proportional allocation strictly to `IMPRESSION` stage. |
| `Revenue` | `ecommerce_purchase_revenue` | Populated strictly when `Funnel_Stage = 'PURCHASE'`, else `0.0`. |
| `Conversion_Flag`| Derived | Binary condition: `1` if `Funnel_Stage = 'PURCHASE'` else `0`. |

---

## 4. API Integration Adapter Specification (Future Scope)

| Source API | Authentication Required | Target Canonical Entities | Status |
|:---|:---|:---|:---|
| **Google Ads API** | OAuth 2.0 Client ID, Developer Token | `Ad_Spend`, `Dim_Campaign`, `IMPRESSION`, `CLICK` | 🔒 Adapter Ready |
| **Meta Marketing API** | User/Page Access Token, Ad Account ID | `Ad_Spend`, `Dim_Campaign`, `IMPRESSION`, `CLICK` | 🔒 Adapter Ready |
| **HubSpot CRM API** | Private App Token / OAuth | Lead status, Deal size, Lifetime revenue | 🔒 Adapter Ready |
| **Email Campaign API** | Platform API Key (SendGrid / Mailchimp) | Newsletter campaigns, Open/Click events | 🔒 Adapter Ready |
