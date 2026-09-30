-- ============================================================
-- Cross-Channel Marketing Funnel Leakage Intelligence
-- SQL Script 06: KPI Queries
-- All analytical KPI calculations
-- ============================================================

USE marketing_funnel_dw;

-- ============================================================
-- 1. Total Users
-- ============================================================
SELECT COUNT(DISTINCT User_ID) AS Total_Users
FROM Fact_FunnelEvent;

-- ============================================================
-- 2. Total Sessions
-- ============================================================
SELECT COUNT(DISTINCT Session_ID) AS Total_Sessions
FROM Fact_FunnelEvent;

-- ============================================================
-- 3. Total Events
-- ============================================================
SELECT COUNT(*) AS Total_Events
FROM Fact_FunnelEvent;

-- ============================================================
-- 4. Total Purchases
-- ============================================================
SELECT COUNT(*) AS Total_Purchases
FROM Fact_FunnelEvent
WHERE Funnel_Stage = 'PURCHASE';

-- ============================================================
-- 5. Total Revenue
-- ============================================================
SELECT ROUND(SUM(Revenue), 2) AS Total_Revenue
FROM Fact_FunnelEvent;

-- ============================================================
-- 6. Total Ad Spend
-- ============================================================
SELECT ROUND(SUM(Ad_Spend), 2) AS Total_Ad_Spend
FROM Fact_FunnelEvent;

-- ============================================================
-- 7. Funnel Stage Counts
-- ============================================================
SELECT
    Funnel_Stage,
    COUNT(*) AS Event_Count,
    COUNT(DISTINCT User_ID) AS Unique_Users,
    COUNT(DISTINCT Session_ID) AS Unique_Sessions
FROM Fact_FunnelEvent
GROUP BY Funnel_Stage
ORDER BY FIELD(Funnel_Stage,
    'IMPRESSION','CLICK','LANDING_PAGE','PRODUCT_VIEW','CART','CHECKOUT','PURCHASE');

-- ============================================================
-- 8. Stage Conversion Rate (stage-to-stage)
-- ============================================================
WITH stage_users AS (
    SELECT Funnel_Stage, COUNT(DISTINCT User_ID) AS Users
    FROM Fact_FunnelEvent
    GROUP BY Funnel_Stage
),
ordered AS (
    SELECT *, FIELD(Funnel_Stage,
        'IMPRESSION','CLICK','LANDING_PAGE','PRODUCT_VIEW','CART','CHECKOUT','PURCHASE') AS ord
    FROM stage_users
)
SELECT
    c.Funnel_Stage,
    c.Users AS Current_Stage_Users,
    p.Users AS Previous_Stage_Users,
    ROUND(c.Users * 100.0 / NULLIF(p.Users, 0), 2) AS Conversion_Rate_Pct,
    ROUND((p.Users - c.Users) * 100.0 / NULLIF(p.Users, 0), 2) AS Drop_Off_Rate_Pct
FROM ordered c
LEFT JOIN ordered p ON p.ord = c.ord - 1
ORDER BY c.ord;

-- ============================================================
-- 9. Funnel Drop-Off (absolute counts)
-- ============================================================
WITH stage_users AS (
    SELECT Funnel_Stage, COUNT(DISTINCT User_ID) AS Users
    FROM Fact_FunnelEvent
    GROUP BY Funnel_Stage
),
ordered AS (
    SELECT *, FIELD(Funnel_Stage,
        'IMPRESSION','CLICK','LANDING_PAGE','PRODUCT_VIEW','CART','CHECKOUT','PURCHASE') AS ord
    FROM stage_users
)
SELECT
    c.Funnel_Stage,
    c.Users,
    COALESCE(p.Users - c.Users, 0) AS Drop_Off_Count
FROM ordered c
LEFT JOIN ordered p ON p.ord = c.ord - 1
ORDER BY c.ord;

-- ============================================================
-- 10. Cart Abandonment Rate
-- ============================================================
SELECT
    ROUND(
        (cart.Users - COALESCE(checkout.Users, 0)) * 100.0 / NULLIF(cart.Users, 0), 2
    ) AS Cart_Abandonment_Rate_Pct
FROM
    (SELECT COUNT(DISTINCT User_ID) AS Users FROM Fact_FunnelEvent WHERE Funnel_Stage = 'CART') cart,
    (SELECT COUNT(DISTINCT User_ID) AS Users FROM Fact_FunnelEvent WHERE Funnel_Stage = 'CHECKOUT') checkout;

-- ============================================================
-- 11. Checkout Abandonment Rate
-- ============================================================
SELECT
    ROUND(
        (checkout.Users - COALESCE(purchase.Users, 0)) * 100.0 / NULLIF(checkout.Users, 0), 2
    ) AS Checkout_Abandonment_Rate_Pct
FROM
    (SELECT COUNT(DISTINCT User_ID) AS Users FROM Fact_FunnelEvent WHERE Funnel_Stage = 'CHECKOUT') checkout,
    (SELECT COUNT(DISTINCT User_ID) AS Users FROM Fact_FunnelEvent WHERE Funnel_Stage = 'PURCHASE') purchase;

-- ============================================================
-- 12. CPA (Cost Per Acquisition)
-- ============================================================
SELECT
    ROUND(
        SUM(Ad_Spend) / NULLIF(SUM(CASE WHEN Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END), 0), 2
    ) AS CPA
FROM Fact_FunnelEvent;

-- ============================================================
-- 13. ROAS (Return on Ad Spend)
-- ============================================================
SELECT
    ROUND(
        SUM(Revenue) / NULLIF(SUM(Ad_Spend), 0), 2
    ) AS ROAS
FROM Fact_FunnelEvent;

-- ============================================================
-- 14. Landing Page Conversion Rate
-- ============================================================
SELECT
    lp.Page_URL,
    COUNT(DISTINCT f.User_ID) AS Total_Users,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END) AS Purchasers,
    ROUND(
        SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END) * 100.0
        / NULLIF(COUNT(DISTINCT f.User_ID), 0), 2
    ) AS Conversion_Rate_Pct
FROM Fact_FunnelEvent f
JOIN Dim_LandingPage lp ON f.LandingPage_ID = lp.LandingPage_ID
GROUP BY lp.Page_URL
ORDER BY Conversion_Rate_Pct DESC;

-- ============================================================
-- 15. Device Conversion Rate
-- ============================================================
SELECT
    d.Device_Type,
    COUNT(DISTINCT f.User_ID) AS Total_Users,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END) AS Purchasers,
    ROUND(
        SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END) * 100.0
        / NULLIF(COUNT(DISTINCT f.User_ID), 0), 2
    ) AS Conversion_Rate_Pct
FROM Fact_FunnelEvent f
JOIN Dim_Device d ON f.Device_ID = d.Device_ID
GROUP BY d.Device_Type
ORDER BY Conversion_Rate_Pct DESC;

-- ============================================================
-- 16. Geography Conversion Rate
-- ============================================================
SELECT
    g.Country,
    COUNT(DISTINCT f.User_ID) AS Total_Users,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END) AS Purchasers,
    ROUND(
        SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END) * 100.0
        / NULLIF(COUNT(DISTINCT f.User_ID), 0), 2
    ) AS Conversion_Rate_Pct
FROM Fact_FunnelEvent f
JOIN Dim_Geography g ON f.Geography_ID = g.Geography_ID
GROUP BY g.Country
ORDER BY Conversion_Rate_Pct DESC;

-- ============================================================
-- 17. Channel Performance Summary
-- ============================================================
SELECT * FROM vw_channel_performance
ORDER BY Total_Revenue DESC;

-- ============================================================
-- 18. Campaign Performance Summary
-- ============================================================
SELECT * FROM vw_campaign_performance
ORDER BY Total_Revenue DESC;

-- ============================================================
-- 19. Daily Trend
-- ============================================================
SELECT * FROM vw_daily_trend
ORDER BY `Date`
LIMIT 30;

-- ============================================================
-- 20. Weekly Trend
-- ============================================================
SELECT
    dt.`Year`,
    dt.Week,
    COUNT(DISTINCT f.User_ID) AS Users,
    SUM(CASE WHEN f.Funnel_Stage = 'PURCHASE' THEN 1 ELSE 0 END) AS Purchases,
    ROUND(SUM(f.Revenue), 2) AS Revenue,
    ROUND(SUM(f.Ad_Spend), 2) AS Spend
FROM Fact_FunnelEvent f
JOIN Dim_Date dt ON f.Date_ID = dt.Date_ID
GROUP BY dt.`Year`, dt.Week
ORDER BY dt.`Year`, dt.Week;

-- ============================================================
-- 21. Monthly Trend
-- ============================================================
SELECT * FROM vw_monthly_trend;

-- ============================================================
-- 22. Overall Funnel Conversion Rate (top to bottom)
-- ============================================================
SELECT
    ROUND(
        (SELECT COUNT(DISTINCT User_ID) FROM Fact_FunnelEvent WHERE Funnel_Stage = 'PURCHASE')
        * 100.0 /
        NULLIF((SELECT COUNT(DISTINCT User_ID) FROM Fact_FunnelEvent WHERE Funnel_Stage = 'IMPRESSION'), 0)
    , 2) AS Overall_Funnel_Conversion_Rate_Pct;
