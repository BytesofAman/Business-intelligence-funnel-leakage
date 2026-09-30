-- ============================================================
-- Cross-Channel Marketing Funnel Leakage Intelligence
-- SQL Script 07: Validation Queries
-- Data quality and integrity checks
-- ============================================================

USE marketing_funnel_dw;

-- ============================================================
-- 1. Row Counts
-- ============================================================
SELECT 'Fact_FunnelEvent' AS TableName, COUNT(*) AS RowCount FROM Fact_FunnelEvent
UNION ALL
SELECT 'Dim_Date', COUNT(*) FROM Dim_Date
UNION ALL
SELECT 'Dim_Channel', COUNT(*) FROM Dim_Channel
UNION ALL
SELECT 'Dim_Campaign', COUNT(*) FROM Dim_Campaign
UNION ALL
SELECT 'Dim_LandingPage', COUNT(*) FROM Dim_LandingPage
UNION ALL
SELECT 'Dim_Device', COUNT(*) FROM Dim_Device
UNION ALL
SELECT 'Dim_Geography', COUNT(*) FROM Dim_Geography;

-- ============================================================
-- 2. Null Primary Keys
-- ============================================================
SELECT 'Null Event_ID in Fact' AS Issue, COUNT(*) AS Count
FROM Fact_FunnelEvent WHERE Event_ID IS NULL
UNION ALL
SELECT 'Null Date_ID in Dim_Date', COUNT(*)
FROM Dim_Date WHERE Date_ID IS NULL
UNION ALL
SELECT 'Null Channel_ID in Dim_Channel', COUNT(*)
FROM Dim_Channel WHERE Channel_ID IS NULL;

-- ============================================================
-- 3. Duplicate Primary Keys
-- ============================================================
SELECT 'Duplicate Event_IDs' AS Issue, COUNT(*) AS Count
FROM (
    SELECT Event_ID FROM Fact_FunnelEvent
    GROUP BY Event_ID HAVING COUNT(*) > 1
) dup;

-- ============================================================
-- 4. Orphan Foreign Keys
-- ============================================================
SELECT 'Orphan Campaign_ID' AS Issue, COUNT(*) AS Count
FROM Fact_FunnelEvent f
LEFT JOIN Dim_Campaign c ON f.Campaign_ID = c.Campaign_ID
WHERE f.Campaign_ID IS NOT NULL AND c.Campaign_ID IS NULL
UNION ALL
SELECT 'Orphan Channel_ID', COUNT(*)
FROM Fact_FunnelEvent f
LEFT JOIN Dim_Channel ch ON f.Channel_ID = ch.Channel_ID
WHERE f.Channel_ID IS NOT NULL AND ch.Channel_ID IS NULL
UNION ALL
SELECT 'Orphan Device_ID', COUNT(*)
FROM Fact_FunnelEvent f
LEFT JOIN Dim_Device d ON f.Device_ID = d.Device_ID
WHERE f.Device_ID IS NOT NULL AND d.Device_ID IS NULL
UNION ALL
SELECT 'Orphan Geography_ID', COUNT(*)
FROM Fact_FunnelEvent f
LEFT JOIN Dim_Geography g ON f.Geography_ID = g.Geography_ID
WHERE f.Geography_ID IS NOT NULL AND g.Geography_ID IS NULL
UNION ALL
SELECT 'Orphan LandingPage_ID', COUNT(*)
FROM Fact_FunnelEvent f
LEFT JOIN Dim_LandingPage lp ON f.LandingPage_ID = lp.LandingPage_ID
WHERE f.LandingPage_ID IS NOT NULL AND lp.LandingPage_ID IS NULL
UNION ALL
SELECT 'Orphan Date_ID', COUNT(*)
FROM Fact_FunnelEvent f
LEFT JOIN Dim_Date dt ON f.Date_ID = dt.Date_ID
WHERE f.Date_ID IS NOT NULL AND dt.Date_ID IS NULL;

-- ============================================================
-- 5. Invalid Funnel Stages
-- ============================================================
SELECT 'Invalid Funnel Stages' AS Issue, COUNT(*) AS Count
FROM Fact_FunnelEvent
WHERE Funnel_Stage NOT IN ('IMPRESSION','CLICK','LANDING_PAGE','PRODUCT_VIEW','CART','CHECKOUT','PURCHASE');

-- ============================================================
-- 6. Revenue Totals by Stage
-- ============================================================
SELECT
    Funnel_Stage,
    ROUND(SUM(Revenue), 2) AS Total_Revenue,
    COUNT(CASE WHEN Revenue > 0 THEN 1 END) AS Records_With_Revenue
FROM Fact_FunnelEvent
GROUP BY Funnel_Stage
ORDER BY FIELD(Funnel_Stage,
    'IMPRESSION','CLICK','LANDING_PAGE','PRODUCT_VIEW','CART','CHECKOUT','PURCHASE');

-- ============================================================
-- 7. Spend Totals by Channel
-- ============================================================
SELECT
    ch.Channel_Name,
    ROUND(SUM(f.Ad_Spend), 2) AS Total_Spend
FROM Fact_FunnelEvent f
JOIN Dim_Channel ch ON f.Channel_ID = ch.Channel_ID
GROUP BY ch.Channel_Name;

-- ============================================================
-- 8. Purchase Count Validation
-- ============================================================
SELECT
    COUNT(*) AS Purchase_Events,
    COUNT(DISTINCT User_ID) AS Unique_Purchasers,
    ROUND(SUM(Revenue), 2) AS Total_Revenue,
    ROUND(AVG(Revenue), 2) AS Avg_Revenue
FROM Fact_FunnelEvent
WHERE Funnel_Stage = 'PURCHASE';

-- ============================================================
-- 9. Date Coverage
-- ============================================================
SELECT
    MIN(dt.`Date`) AS Earliest_Date,
    MAX(dt.`Date`) AS Latest_Date,
    COUNT(DISTINCT dt.`Date`) AS Days_Covered
FROM Fact_FunnelEvent f
JOIN Dim_Date dt ON f.Date_ID = dt.Date_ID;

-- ============================================================
-- 10. Negative Revenue Check
-- ============================================================
SELECT 'Negative Revenue Records' AS Issue, COUNT(*) AS Count
FROM Fact_FunnelEvent
WHERE Revenue < 0;

-- ============================================================
-- 11. Negative Spend Check
-- ============================================================
SELECT 'Negative Spend Records' AS Issue, COUNT(*) AS Count
FROM Fact_FunnelEvent
WHERE Ad_Spend < 0;

-- ============================================================
-- 12. Overall Validation Summary
-- ============================================================
SELECT 'VALIDATION COMPLETE' AS Status;
