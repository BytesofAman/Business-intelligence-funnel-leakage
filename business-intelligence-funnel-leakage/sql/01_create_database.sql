-- ============================================================
-- Cross-Channel Marketing Funnel Leakage Intelligence
-- SQL Script 01: Create Database
-- Database: MySQL 8.0
-- ============================================================

-- Create the data warehouse database
CREATE DATABASE IF NOT EXISTS marketing_funnel_dw
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE marketing_funnel_dw;

-- Verify creation
SELECT 'Database marketing_funnel_dw created successfully' AS status;
