-- ============================================================
-- Cross-Channel Marketing Funnel Leakage Intelligence
-- SQL Script 03: Create Fact Table
-- Star Schema Central Fact Table
-- ============================================================
-- GRAIN: One record = one standardized funnel event
--        for a user/session at a specific funnel stage.
-- ============================================================

USE marketing_funnel_dw;

CREATE TABLE IF NOT EXISTS Fact_FunnelEvent (
    Event_ID        VARCHAR(36)     PRIMARY KEY,
    User_ID         VARCHAR(100)    NOT NULL,
    Session_ID      VARCHAR(100)    NOT NULL,
    Campaign_ID     VARCHAR(10)     DEFAULT NULL,
    Channel_ID      INT             DEFAULT NULL,
    LandingPage_ID  INT             DEFAULT NULL,
    Device_ID       INT             DEFAULT NULL,
    Geography_ID    INT             DEFAULT NULL,
    Date_ID         INT             DEFAULT NULL,
    Funnel_Stage    VARCHAR(20)     NOT NULL,
    Event_Timestamp DATETIME        NOT NULL,
    Source_Platform  VARCHAR(100)   DEFAULT NULL,
    Ad_Spend        DECIMAL(12,4)   DEFAULT 0.0000,
    Revenue         DECIMAL(12,4)   DEFAULT 0.0000,
    Conversion_Flag TINYINT(1)      DEFAULT 0,

    -- Foreign key constraints
    CONSTRAINT fk_fact_campaign
        FOREIGN KEY (Campaign_ID) REFERENCES Dim_Campaign(Campaign_ID)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_fact_channel
        FOREIGN KEY (Channel_ID) REFERENCES Dim_Channel(Channel_ID)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_fact_landingpage
        FOREIGN KEY (LandingPage_ID) REFERENCES Dim_LandingPage(LandingPage_ID)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_fact_device
        FOREIGN KEY (Device_ID) REFERENCES Dim_Device(Device_ID)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_fact_geography
        FOREIGN KEY (Geography_ID) REFERENCES Dim_Geography(Geography_ID)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_fact_date
        FOREIGN KEY (Date_ID) REFERENCES Dim_Date(Date_ID)
        ON DELETE SET NULL ON UPDATE CASCADE,

    -- Funnel stage must be valid
    CONSTRAINT chk_funnel_stage
        CHECK (Funnel_Stage IN ('IMPRESSION', 'CLICK', 'LANDING_PAGE',
                                'PRODUCT_VIEW', 'CART', 'CHECKOUT', 'PURCHASE'))
) ENGINE=InnoDB;

SELECT 'Fact_FunnelEvent table created successfully' AS status;
