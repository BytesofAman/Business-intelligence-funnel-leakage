-- ============================================================
-- Cross-Channel Marketing Funnel Leakage Intelligence
-- SQL Script 04: Create Indexes
-- Performance optimization for analytical queries
-- ============================================================

USE marketing_funnel_dw;

-- Fact table indexes for common query patterns
CREATE INDEX idx_fact_funnel_stage ON Fact_FunnelEvent(Funnel_Stage);
CREATE INDEX idx_fact_date ON Fact_FunnelEvent(Date_ID);
CREATE INDEX idx_fact_channel ON Fact_FunnelEvent(Channel_ID);
CREATE INDEX idx_fact_campaign ON Fact_FunnelEvent(Campaign_ID);
CREATE INDEX idx_fact_device ON Fact_FunnelEvent(Device_ID);
CREATE INDEX idx_fact_geography ON Fact_FunnelEvent(Geography_ID);
CREATE INDEX idx_fact_landingpage ON Fact_FunnelEvent(LandingPage_ID);
CREATE INDEX idx_fact_user ON Fact_FunnelEvent(User_ID);
CREATE INDEX idx_fact_session ON Fact_FunnelEvent(Session_ID);
CREATE INDEX idx_fact_timestamp ON Fact_FunnelEvent(Event_Timestamp);
CREATE INDEX idx_fact_conversion ON Fact_FunnelEvent(Conversion_Flag);

-- Composite indexes for common joins and filters
CREATE INDEX idx_fact_stage_date ON Fact_FunnelEvent(Funnel_Stage, Date_ID);
CREATE INDEX idx_fact_channel_stage ON Fact_FunnelEvent(Channel_ID, Funnel_Stage);
CREATE INDEX idx_fact_campaign_stage ON Fact_FunnelEvent(Campaign_ID, Funnel_Stage);

-- Dimension indexes
CREATE INDEX idx_date_year_month ON Dim_Date(`Year`, `Month`);
CREATE INDEX idx_date_quarter ON Dim_Date(`Quarter`);
CREATE INDEX idx_geo_country ON Dim_Geography(Country);
CREATE INDEX idx_device_type ON Dim_Device(Device_Type);

SELECT 'All indexes created successfully' AS status;
