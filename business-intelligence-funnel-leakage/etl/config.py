"""Configuration module for the ETL pipeline."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'
VALIDATION_DIR = DATA_DIR / 'validation'

# Source directories
GA4_DIR = RAW_DIR / 'ga4'
GOOGLE_ADS_DIR = RAW_DIR / 'google_ads'
META_DIR = RAW_DIR / 'meta'
HUBSPOT_DIR = RAW_DIR / 'hubspot'
EMAIL_DIR = RAW_DIR / 'email'

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'marketing_funnel_dw'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# Funnel stages in order
FUNNEL_STAGES = [
    'IMPRESSION',
    'CLICK',
    'LANDING_PAGE',
    'PRODUCT_VIEW',
    'CART',
    'CHECKOUT',
    'PURCHASE',
]

FUNNEL_STAGE_ORDER = {stage: i for i, stage in enumerate(FUNNEL_STAGES)}

# Canonical columns for the unified event model
CANONICAL_COLUMNS = [
    'Event_ID', 'User_ID', 'Session_ID', 'Campaign_ID', 'Channel_ID',
    'LandingPage_ID', 'Device_ID', 'Geography_ID', 'Date_ID',
    'Event_Timestamp', 'Funnel_Stage', 'Source_Platform',
    'Campaign_Name', 'Channel_Name', 'Landing_Page',
    'Device_Type', 'OS', 'Browser',
    'Country', 'Region', 'City',
    'Ad_Spend', 'Revenue', 'Conversion_Flag',
]
