-- ============================================================
-- Cross-Channel Marketing Funnel Leakage Intelligence
-- SQL Script 02: Create Dimension Tables
-- Star Schema Dimensions
-- ============================================================

USE marketing_funnel_dw;

-- ============================================================
-- Dim_Date: Calendar dimension
-- ============================================================
CREATE TABLE IF NOT EXISTS Dim_Date (
    Date_ID         INT             PRIMARY KEY,
    `Date`          DATE            NOT NULL,
    Day_of_Week     VARCHAR(10)     NOT NULL,
    Day_of_Month    INT             NOT NULL,
    Week            INT             NOT NULL,
    `Month`         INT             NOT NULL,
    Month_Name      VARCHAR(10)     NOT NULL,
    `Quarter`       INT             NOT NULL,
    `Year`          INT             NOT NULL,
    Is_Weekend      TINYINT(1)      NOT NULL DEFAULT 0,

    UNIQUE KEY uq_date (`Date`)
) ENGINE=InnoDB;

-- ============================================================
-- Dim_Channel: Marketing channel dimension
-- ============================================================
CREATE TABLE IF NOT EXISTS Dim_Channel (
    Channel_ID      INT             PRIMARY KEY AUTO_INCREMENT,
    Channel_Name    VARCHAR(100)    NOT NULL,
    Platform        VARCHAR(100)    DEFAULT NULL,
    Campaign_Type   VARCHAR(100)    DEFAULT NULL,

    UNIQUE KEY uq_channel_name (Channel_Name)
) ENGINE=InnoDB;

-- ============================================================
-- Dim_Campaign: Marketing campaign dimension
-- ============================================================
CREATE TABLE IF NOT EXISTS Dim_Campaign (
    Campaign_ID     VARCHAR(10)     PRIMARY KEY,
    Campaign_Name   VARCHAR(200)    NOT NULL,
    Objective       VARCHAR(100)    DEFAULT NULL,
    Budget          DECIMAL(12,2)   DEFAULT NULL,

    UNIQUE KEY uq_campaign_name (Campaign_Name)
) ENGINE=InnoDB;

-- ============================================================
-- Dim_LandingPage: Landing page dimension
-- ============================================================
CREATE TABLE IF NOT EXISTS Dim_LandingPage (
    LandingPage_ID  INT             PRIMARY KEY AUTO_INCREMENT,
    Page_URL        VARCHAR(500)    NOT NULL,
    Page_Category   VARCHAR(100)    DEFAULT NULL,

    UNIQUE KEY uq_page_url (Page_URL)
) ENGINE=InnoDB;

-- ============================================================
-- Dim_Device: Device dimension
-- ============================================================
CREATE TABLE IF NOT EXISTS Dim_Device (
    Device_ID       INT             PRIMARY KEY AUTO_INCREMENT,
    Device_Type     VARCHAR(50)     NOT NULL,
    OS              VARCHAR(100)    DEFAULT NULL,
    Browser         VARCHAR(100)    DEFAULT NULL,

    UNIQUE KEY uq_device (Device_Type, OS, Browser)
) ENGINE=InnoDB;

-- ============================================================
-- Dim_Geography: Geography dimension
-- ============================================================
CREATE TABLE IF NOT EXISTS Dim_Geography (
    Geography_ID    INT             PRIMARY KEY AUTO_INCREMENT,
    Country         VARCHAR(100)    NOT NULL,
    Region          VARCHAR(200)    DEFAULT NULL,
    City            VARCHAR(200)    DEFAULT NULL,

    UNIQUE KEY uq_geography (Country, Region, City)
) ENGINE=InnoDB;

SELECT 'All dimension tables created successfully' AS status;
