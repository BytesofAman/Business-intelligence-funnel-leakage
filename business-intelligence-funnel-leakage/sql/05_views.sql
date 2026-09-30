-- ============================================================
-- Cross-Channel Marketing Funnel Leakage Intelligence
-- SQL Script 05: Create Analytical Views
-- Pre-built views for Power BI and reporting
-- ============================================================

USE marketing_funnel_dw;

-- ============================================================
-- VIEW: vw_funnel_summary
-- Funnel stage counts and conversion rates
-- ============================================================
CREATE OR REPLACE VIEW vw_funnel_summary AS
SELECT
    f.Funnel_Stage,
    COUNT(*)                                            AS Event_Count,
    COUNT(DISTINCT f.User_ID)                           AS Unique_Users,
    COUNT(DISTINCT f.Session_ID)                        AS Unique_Sessions
FROM Fact_FunnelEvent f
GROUP BY f.Funnel_Stage
ORDER BY FIELD(f.Funnel_Stage,
    'IMPRESSION','CLICK','LANDING_PAGE','PRODUCT_VIEW','CART','CHECKOUT','PURCHASE');

-- ============================================================
-- VIEW: vw_funnel_conversion
-- Stage-to-stage conversion and drop-off rates
-- ============================================================
CREATE OR REPLACE VIEW vw_funnel_conversion AS
WITH stage_users AS (
    SELECT
        Funnel_Stage,
        COUNT(DISTINCT User_ID) AS Users
    FROM Fact_FunnelEvent
    GROUP BY Funnel_Stage
),
ordered_stages AS (
    SELECT
        Funnel_Stage,
        Users,
        FIELD(Funnel_Stage,
            'IMPRESSION','CLICK','LANDING_PAGE','PRODUCT_VIEW','CART','CHECKOUT','PURCHASE') AS stage_order
    FROM stage_users
)
SELECT
    curr.Funnel_Stage,
    curr.Users                                                              AS Stage_Users,
    prev.Users                                                              AS Previous_Stage_Users,
    ROUND(curr.Users * 100.0 / NULLIF(prev.Users, 0), 2)                   AS Conversion_Rate_Pct,
    ROUND((prev.Users - curr.Users) * 100.0 / NULLIF(prev.Users, 0), 2)    AS Drop_Off_Rate_Pct
FROM ordered_stages curr
LEFT JOIN ordered_stages prev ON prev.stage_order = curr.stage_order - 1
ORDER BY curr.stage_order;

-- ============================================================
-- VIEW: vw_channel_performance
-- Revenue, spend, ROAS, CPA by channel
-- ============================================================
CREATE OR REPLACE VIEW vw_channel_performance AS
SELECT
    ch.Channel_Name,
    ch.Platform,
    COUNT(DISTINCT f.User_ID)                                               AS Users,
    COUNT(DISTINCT f.Session_ID)                                            AS Sessions,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)           AS Purchases,
    ROUND(SUM(f.Revenue), 2)                                                AS Total_Revenue,
    ROUND(SUM(f.Ad_Spend), 2)                                               AS Total_Spend,
    ROUND(SUM(f.Revenue) / NULLIF(SUM(f.Ad_Spend), 0), 2)                  AS ROAS,
    ROUND(SUM(f.Ad_Spend) / NULLIF(SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE'
          THEN 1 ELSE 0 END), 0), 2)                                        AS CPA,
    ROUND(SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)
          * 100.0 / NULLIF(COUNT(DISTINCT f.User_ID), 0), 2)               AS Conversion_Rate_Pct
FROM Fact_FunnelEvent f
JOIN Dim_Channel ch ON f.Channel_ID = ch.Channel_ID
GROUP BY ch.Channel_Name, ch.Platform;

-- ============================================================
-- VIEW: vw_campaign_performance
-- Campaign-level metrics
-- ============================================================
CREATE OR REPLACE VIEW vw_campaign_performance AS
SELECT
    c.Campaign_ID,
    c.Campaign_Name,
    c.Objective,
    ch.Channel_Name,
    COUNT(DISTINCT f.User_ID)                                               AS Users,
    COUNT(DISTINCT f.Session_ID)                                            AS Sessions,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)           AS Purchases,
    ROUND(SUM(f.Revenue), 2)                                                AS Total_Revenue,
    ROUND(SUM(f.Ad_Spend), 2)                                               AS Total_Spend,
    ROUND(SUM(f.Revenue) / NULLIF(SUM(f.Ad_Spend), 0), 2)                  AS ROAS,
    ROUND(SUM(f.Ad_Spend) / NULLIF(SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE'
          THEN 1 ELSE 0 END), 0), 2)                                        AS CPA
FROM Fact_FunnelEvent f
JOIN Dim_Campaign c ON f.Campaign_ID = c.Campaign_ID
LEFT JOIN Dim_Channel ch ON f.Channel_ID = ch.Channel_ID
GROUP BY c.Campaign_ID, c.Campaign_Name, c.Objective, ch.Channel_Name;

-- ============================================================
-- VIEW: vw_device_performance
-- Device-level conversion analysis
-- ============================================================
CREATE OR REPLACE VIEW vw_device_performance AS
SELECT
    d.Device_Type,
    d.OS,
    d.Browser,
    COUNT(DISTINCT f.User_ID)                                               AS Users,
    COUNT(DISTINCT f.Session_ID)                                            AS Sessions,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)           AS Purchases,
    ROUND(SUM(f.Revenue), 2)                                                AS Total_Revenue,
    ROUND(SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)
          * 100.0 / NULLIF(COUNT(DISTINCT f.User_ID), 0), 2)               AS Conversion_Rate_Pct
FROM Fact_FunnelEvent f
JOIN Dim_Device d ON f.Device_ID = d.Device_ID
GROUP BY d.Device_Type, d.OS, d.Browser;

-- ============================================================
-- VIEW: vw_geography_performance
-- Geography-level conversion analysis
-- ============================================================
CREATE OR REPLACE VIEW vw_geography_performance AS
SELECT
    g.Country,
    g.Region,
    g.City,
    COUNT(DISTINCT f.User_ID)                                               AS Users,
    COUNT(DISTINCT f.Session_ID)                                            AS Sessions,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)           AS Purchases,
    ROUND(SUM(f.Revenue), 2)                                                AS Total_Revenue,
    ROUND(SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)
          * 100.0 / NULLIF(COUNT(DISTINCT f.User_ID), 0), 2)               AS Conversion_Rate_Pct
FROM Fact_FunnelEvent f
JOIN Dim_Geography g ON f.Geography_ID = g.Geography_ID
GROUP BY g.Country, g.Region, g.City;

-- ============================================================
-- VIEW: vw_landingpage_performance
-- Landing page conversion analysis
-- ============================================================
CREATE OR REPLACE VIEW vw_landingpage_performance AS
SELECT
    lp.Page_URL,
    lp.Page_Category,
    COUNT(DISTINCT f.User_ID)                                               AS Users,
    COUNT(DISTINCT f.Session_ID)                                            AS Sessions,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)           AS Purchases,
    ROUND(SUM(f.Revenue), 2)                                                AS Total_Revenue,
    ROUND(SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)
          * 100.0 / NULLIF(COUNT(DISTINCT f.User_ID), 0), 2)               AS Conversion_Rate_Pct
FROM Fact_FunnelEvent f
JOIN Dim_LandingPage lp ON f.LandingPage_ID = lp.LandingPage_ID
GROUP BY lp.Page_URL, lp.Page_Category;

-- ============================================================
-- VIEW: vw_daily_trend
-- Daily revenue and conversion trends
-- ============================================================
CREATE OR REPLACE VIEW vw_daily_trend AS
SELECT
    dt.`Date`,
    dt.Day_of_Week,
    dt.Is_Weekend,
    COUNT(DISTINCT f.User_ID)                                               AS Users,
    COUNT(DISTINCT f.Session_ID)                                            AS Sessions,
    COUNT(*)                                                                AS Events,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)           AS Purchases,
    ROUND(SUM(f.Revenue), 2)                                                AS Revenue,
    ROUND(SUM(f.Ad_Spend), 2)                                               AS Spend
FROM Fact_FunnelEvent f
JOIN Dim_Date dt ON f.Date_ID = dt.Date_ID
GROUP BY dt.`Date`, dt.Day_of_Week, dt.Is_Weekend
ORDER BY dt.`Date`;

-- ============================================================
-- VIEW: vw_monthly_trend
-- Monthly aggregated trends
-- ============================================================
CREATE OR REPLACE VIEW vw_monthly_trend AS
SELECT
    dt.`Year`,
    dt.`Month`,
    dt.Month_Name,
    COUNT(DISTINCT f.User_ID)                                               AS Users,
    COUNT(DISTINCT f.Session_ID)                                            AS Sessions,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END)           AS Purchases,
    ROUND(SUM(f.Revenue), 2)                                                AS Revenue,
    ROUND(SUM(f.Ad_Spend), 2)                                               AS Spend,
    ROUND(SUM(f.Revenue) / NULLIF(SUM(f.Ad_Spend), 0), 2)                  AS ROAS
FROM Fact_FunnelEvent f
JOIN Dim_Date dt ON f.Date_ID = dt.Date_ID
GROUP BY dt.`Year`, dt.`Month`, dt.Month_Name
ORDER BY dt.`Year`, dt.`Month`;

SELECT 'All views created successfully' AS status;
