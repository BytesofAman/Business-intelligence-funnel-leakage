"""
Extract module for the ETL pipeline.

Reads raw data files from source directories and returns structured DataFrames.
Each source has its own extraction function.
"""

import pandas as pd
from pathlib import Path
from etl.config import GA4_DIR, GOOGLE_ADS_DIR, META_DIR, HUBSPOT_DIR, EMAIL_DIR


def load_ga4_events(filepath: Path = None) -> pd.DataFrame:
    """
    Load GA4 events data from CSV.

    Parameters:
        filepath: Optional explicit path. Defaults to ga4_events.csv in GA4_DIR.

    Returns:
        DataFrame with raw GA4 event data.
    """
    if filepath is None:
        filepath = GA4_DIR / 'ga4_events.csv'

    if not filepath.exists():
        print(f"[EXTRACT] WARNING: GA4 events file not found: {filepath}")
        return pd.DataFrame()

    print(f"[EXTRACT] Loading GA4 events from: {filepath}")
    df = pd.read_csv(filepath, low_memory=False)
    print(f"[EXTRACT] GA4 events loaded: {len(df)} rows, {len(df.columns)} columns")
    return df


def load_campaign_data(filepath: Path = None) -> pd.DataFrame:
    """
    Load campaign reference data from CSV.

    Parameters:
        filepath: Optional explicit path. Defaults to campaign_data.csv in GA4_DIR.

    Returns:
        DataFrame with campaign metadata.
    """
    if filepath is None:
        filepath = GA4_DIR / 'campaign_data.csv'

    if not filepath.exists():
        print(f"[EXTRACT] WARNING: Campaign data file not found: {filepath}")
        return pd.DataFrame()

    print(f"[EXTRACT] Loading campaign data from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"[EXTRACT] Campaign data loaded: {len(df)} rows, {len(df.columns)} columns")
    return df


def load_ad_spend_data(filepath: Path = None) -> pd.DataFrame:
    """
    Load daily ad spend data from CSV.

    Parameters:
        filepath: Optional explicit path. Defaults to ad_spend.csv in GA4_DIR.

    Returns:
        DataFrame with daily ad spend by campaign.
    """
    if filepath is None:
        filepath = GA4_DIR / 'ad_spend.csv'

    if not filepath.exists():
        print(f"[EXTRACT] WARNING: Ad spend data file not found: {filepath}")
        return pd.DataFrame()

    print(f"[EXTRACT] Loading ad spend data from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"[EXTRACT] Ad spend data loaded: {len(df)} rows, {len(df.columns)} columns")
    return df


def load_google_ads_data(filepath: Path = None) -> pd.DataFrame:
    """
    Load Google Ads data (requires API credentials).

    Returns:
        Empty DataFrame with status message if credentials unavailable.
    """
    if filepath is None:
        filepath = GOOGLE_ADS_DIR / 'google_ads_data.csv'

    if not filepath.exists():
        print("[EXTRACT] INFO: Google Ads data not available (requires API credentials).")
        print("[EXTRACT]       Source adapter ready for future integration.")
        return pd.DataFrame()

    print(f"[EXTRACT] Loading Google Ads data from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"[EXTRACT] Google Ads data loaded: {len(df)} rows")
    return df


def load_meta_data(filepath: Path = None) -> pd.DataFrame:
    """
    Load Meta (Facebook/Instagram) Marketing data (requires API credentials).

    Returns:
        Empty DataFrame with status message if credentials unavailable.
    """
    if filepath is None:
        filepath = META_DIR / 'meta_data.csv'

    if not filepath.exists():
        print("[EXTRACT] INFO: Meta Marketing data not available (requires API credentials).")
        print("[EXTRACT]       Source adapter ready for future integration.")
        return pd.DataFrame()

    print(f"[EXTRACT] Loading Meta data from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"[EXTRACT] Meta data loaded: {len(df)} rows")
    return df


def load_hubspot_data(filepath: Path = None) -> pd.DataFrame:
    """
    Load HubSpot CRM data (requires API credentials).

    Returns:
        Empty DataFrame with status message if credentials unavailable.
    """
    if filepath is None:
        filepath = HUBSPOT_DIR / 'hubspot_data.csv'

    if not filepath.exists():
        print("[EXTRACT] INFO: HubSpot CRM data not available (requires API credentials).")
        print("[EXTRACT]       Source adapter ready for future integration.")
        return pd.DataFrame()

    print(f"[EXTRACT] Loading HubSpot data from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"[EXTRACT] HubSpot data loaded: {len(df)} rows")
    return df


def load_email_data(filepath: Path = None) -> pd.DataFrame:
    """
    Load Email Campaign data (requires API credentials).

    Returns:
        Empty DataFrame with status message if credentials unavailable.
    """
    if filepath is None:
        filepath = EMAIL_DIR / 'email_data.csv'

    if not filepath.exists():
        print("[EXTRACT] INFO: Email Campaign data not available (requires API credentials).")
        print("[EXTRACT]       Source adapter ready for future integration.")
        return pd.DataFrame()

    print(f"[EXTRACT] Loading Email data from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"[EXTRACT] Email data loaded: {len(df)} rows")
    return df


def extract_all() -> dict:
    """
    Extract data from all available sources.

    Returns:
        Dictionary of source name -> DataFrame.
    """
    print("=" * 60)
    print("EXTRACTION PHASE")
    print("=" * 60)

    sources = {
        'ga4_events': load_ga4_events(),
        'campaign_data': load_campaign_data(),
        'ad_spend': load_ad_spend_data(),
        'google_ads': load_google_ads_data(),
        'meta': load_meta_data(),
        'hubspot': load_hubspot_data(),
        'email': load_email_data(),
    }

    print("\n--- Extraction Summary ---")
    for name, df in sources.items():
        status = f"{len(df)} rows" if not df.empty else "Not available"
        print(f"  {name}: {status}")
    print()

    return sources
