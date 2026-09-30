"""
Transform module for the ETL pipeline.

Implements all data transformation logic:
- Column name standardization
- Data type conversion
- Timestamp normalization
- Event normalization & funnel stage mapping
- Duplicate detection/removal
- Missing value handling
- Dimension table preparation
- Fact table preparation
"""

import pandas as pd
import numpy as np
import hashlib
from datetime import datetime
from etl.config import FUNNEL_STAGES, FUNNEL_STAGE_ORDER, PROCESSED_DIR


# ============================================================
# GA4 Event to Funnel Stage Mapping
# ============================================================
GA4_EVENT_MAPPING = {
    # GA4 event_name -> Canonical Funnel_Stage
    'session_start':    'IMPRESSION',
    'first_visit':      'IMPRESSION',
    'click':            'CLICK',
    'page_view':        'LANDING_PAGE',
    'view_item':        'PRODUCT_VIEW',
    'add_to_cart':      'CART',
    'begin_checkout':   'CHECKOUT',
    'purchase':         'PURCHASE',
}

# Channel normalization mapping
MEDIUM_TO_CHANNEL = {
    'cpc':      'Paid Search',
    'organic':  'Organic Search',
    'email':    'Email',
    'social':   'Social',
    'referral': 'Referral',
    'direct':   'Direct',
    'display':  'Display',
    '(none)':   'Direct',
    '':         'Direct',
}

# Landing page category mapping
PAGE_CATEGORY_MAP = {
    '/home':                'Home',
    '/products/apparel':    'Apparel',
    '/products/bags':       'Bags',
    '/products/electronics':'Electronics',
    '/products/drinkware':  'Drinkware',
    '/products/accessories':'Accessories',
    '/products/brands':     'Brands',
    '/basket':              'Cart',
    '/checkout':            'Checkout',
    '/order-confirmation':  'Confirmation',
    '/sale':                'Sale',
    '/about':               'About',
    '/support':             'Support',
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to snake_case."""
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df


def normalize_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert GA4 event_timestamp (Unix microseconds) to datetime.
    Also parse event_date from YYYYMMDD format.
    """
    if 'event_timestamp' in df.columns:
        # GA4 timestamps are in microseconds
        df['event_timestamp_dt'] = pd.to_datetime(
            df['event_timestamp'], unit='us', errors='coerce'
        )

    if 'event_date' in df.columns:
        df['event_date_dt'] = pd.to_datetime(
            df['event_date'].astype(str), format='%Y%m%d', errors='coerce'
        )

    return df


def map_funnel_stages(df: pd.DataFrame) -> pd.DataFrame:
    """Map GA4 event names to canonical funnel stages."""
    df['funnel_stage'] = df['event_name'].map(GA4_EVENT_MAPPING)

    unmapped = df[df['funnel_stage'].isna()]['event_name'].unique()
    if len(unmapped) > 0:
        print(f"[TRANSFORM] WARNING: Unmapped event names: {unmapped}")

    # Remove events that don't map to funnel stages
    before = len(df)
    df = df.dropna(subset=['funnel_stage']).copy()
    after = len(df)
    if before != after:
        print(f"[TRANSFORM] Removed {before - after} events with unmapped funnel stages")

    return df


def normalize_channels(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize traffic source medium to standard channel names."""
    if 'traffic_source_medium' in df.columns:
        df['channel_name'] = df['traffic_source_medium'].fillna('direct').str.lower().map(
            MEDIUM_TO_CHANNEL
        ).fillna('Direct')
    else:
        df['channel_name'] = 'Direct'
    return df


def normalize_campaigns(df: pd.DataFrame, campaign_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize campaign names and merge with campaign reference data.
    """
    if 'traffic_source_name' in df.columns:
        df['campaign_name'] = df['traffic_source_name'].fillna('(not set)')
    else:
        df['campaign_name'] = '(not set)'

    # Merge campaign IDs from reference data
    if not campaign_df.empty:
        campaign_lookup = campaign_df[['campaign_id', 'campaign_name']].copy()
        campaign_lookup.columns = ['campaign_id_ref', 'campaign_name']
        df = df.merge(campaign_lookup, on='campaign_name', how='left')
        df['campaign_id'] = df['campaign_id_ref'].fillna('C000')
        df.drop(columns=['campaign_id_ref'], inplace=True)
    else:
        df['campaign_id'] = 'C000'

    return df


def normalize_devices(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize device information."""
    if 'device_category' in df.columns:
        df['device_type'] = df['device_category'].fillna('unknown').str.lower()
    else:
        df['device_type'] = 'unknown'

    if 'device_operating_system' in df.columns:
        df['os'] = df['device_operating_system'].fillna('Unknown')
    else:
        df['os'] = 'Unknown'

    if 'device_browser' in df.columns:
        df['browser'] = df['device_browser'].fillna('Unknown')
    else:
        df['browser'] = 'Unknown'

    return df


def normalize_geography(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize geography fields."""
    for col in ['geo_country', 'geo_region', 'geo_city']:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
        else:
            df[col] = 'Unknown'
    return df


def normalize_landing_pages(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize landing page URLs and assign categories."""
    if 'landing_page' in df.columns:
        df['landing_page'] = df['landing_page'].fillna('/home')
    else:
        df['landing_page'] = '/home'

    df['page_category'] = df['landing_page'].map(PAGE_CATEGORY_MAP).fillna('Other')
    return df


def handle_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure revenue is only on PURCHASE events.
    Clean and convert revenue to numeric.
    """
    if 'ecommerce_purchase_revenue' in df.columns:
        df['revenue'] = pd.to_numeric(df['ecommerce_purchase_revenue'], errors='coerce').fillna(0.0)
    else:
        df['revenue'] = 0.0

    # Revenue should only exist for purchase events
    df.loc[df['funnel_stage'] != 'PURCHASE', 'revenue'] = 0.0

    return df


def set_conversion_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Set conversion flag = 1 for PURCHASE events."""
    df['conversion_flag'] = (df['funnel_stage'] == 'PURCHASE').astype(int)
    return df


def generate_dimension_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate surrogate keys for dimension lookups.
    Uses deterministic hashing for consistency.
    """
    # Date_ID: YYYYMMDD integer format
    if 'event_date_dt' in df.columns:
        df['date_id'] = df['event_date_dt'].dt.strftime('%Y%m%d').astype(int, errors='ignore')
    elif 'event_date' in df.columns:
        df['date_id'] = df['event_date'].astype(int, errors='ignore')

    return df


def remove_duplicates(df: pd.DataFrame) -> tuple:
    """
    Remove duplicate events based on event_id.

    Returns:
        Tuple of (deduplicated DataFrame, duplicate count)
    """
    before = len(df)
    df = df.drop_duplicates(subset=['event_id'], keep='first')
    after = len(df)
    dup_count = before - after
    if dup_count > 0:
        print(f"[TRANSFORM] Removed {dup_count} duplicate events")
    return df, dup_count


def allocate_ad_spend(df: pd.DataFrame, spend_df: pd.DataFrame,
                      campaign_df: pd.DataFrame) -> pd.DataFrame:
    """
    Allocate daily ad spend proportionally to events per campaign per day.
    Only allocates spend to IMPRESSION events to avoid double-counting.
    """
    df['ad_spend'] = 0.0

    if spend_df.empty:
        print("[TRANSFORM] No ad spend data available. Setting all Ad_Spend to 0.")
        return df

    # Parse spend dates
    spend_df = spend_df.copy()
    spend_df['date'] = pd.to_datetime(spend_df['date'], errors='coerce')
    spend_df['date_id'] = spend_df['date'].dt.strftime('%Y%m%d').astype(int, errors='ignore')

    # Merge campaign IDs
    if 'campaign_id' not in spend_df.columns and not campaign_df.empty:
        spend_df = spend_df.merge(
            campaign_df[['campaign_id', 'campaign_name']],
            on='campaign_name', how='left'
        )

    # Allocate spend to IMPRESSION events proportionally
    impression_mask = df['funnel_stage'] == 'IMPRESSION'
    impression_events = df[impression_mask].copy()

    if impression_events.empty:
        return df

    # Count impressions per campaign per day
    imp_counts = (
        impression_events
        .groupby(['campaign_id', 'date_id'])
        .size()
        .reset_index(name='event_count')
    )

    # Merge with spend
    spend_alloc = imp_counts.merge(
        spend_df[['campaign_id', 'date_id', 'daily_spend']],
        on=['campaign_id', 'date_id'],
        how='left'
    )
    spend_alloc['daily_spend'] = spend_alloc['daily_spend'].fillna(0)
    spend_alloc['spend_per_event'] = (
        spend_alloc['daily_spend'] / spend_alloc['event_count'].replace(0, np.nan)
    ).fillna(0)

    # Apply allocated spend back to impression events
    spend_lookup = spend_alloc.set_index(['campaign_id', 'date_id'])['spend_per_event'].to_dict()

    def get_spend(row):
        key = (row['campaign_id'], row['date_id'])
        return spend_lookup.get(key, 0.0)

    df.loc[impression_mask, 'ad_spend'] = (
        impression_events.apply(get_spend, axis=1).values
    )

    total_allocated = df['ad_spend'].sum()
    total_available = spend_df['daily_spend'].sum()
    print(f"[TRANSFORM] Ad spend allocated: ${total_allocated:,.2f} of ${total_available:,.2f} total")

    return df


def build_date_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """Build Dim_Date from unique dates in the data."""
    if 'event_date_dt' not in df.columns:
        return pd.DataFrame()

    dates = df['event_date_dt'].dropna().unique()
    dates = pd.to_datetime(dates)
    dates = sorted(dates)

    records = []
    for d in dates:
        records.append({
            'Date_ID': int(d.strftime('%Y%m%d')),
            'Date': d.date(),
            'Day_of_Week': d.strftime('%A'),
            'Day_of_Month': d.day,
            'Week': d.isocalendar()[1],
            'Month': d.month,
            'Month_Name': d.strftime('%B'),
            'Quarter': (d.month - 1) // 3 + 1,
            'Year': d.year,
            'Is_Weekend': 1 if d.weekday() >= 5 else 0,
        })

    return pd.DataFrame(records)


def build_channel_dimension(df: pd.DataFrame, campaign_df: pd.DataFrame) -> pd.DataFrame:
    """Build Dim_Channel from unique channels."""
    if 'channel_name' not in df.columns:
        return pd.DataFrame()

    channels = df[['channel_name']].drop_duplicates().copy()
    channels = channels[channels['channel_name'].notna()].reset_index(drop=True)

    # Merge platform and campaign_type from campaign reference
    if not campaign_df.empty and 'channel' in campaign_df.columns:
        channel_info = campaign_df.groupby('channel').agg({
            'platform': 'first',
            'campaign_type': 'first'
        }).reset_index()
        channel_info.columns = ['channel_name', 'Platform', 'Campaign_Type']
        channels = channels.merge(channel_info, on='channel_name', how='left')
    else:
        channels['Platform'] = None
        channels['Campaign_Type'] = None

    channels.insert(0, 'Channel_ID', range(1, len(channels) + 1))
    channels.columns = ['Channel_ID', 'Channel_Name', 'Platform', 'Campaign_Type']
    return channels


def build_campaign_dimension(campaign_df: pd.DataFrame) -> pd.DataFrame:
    """Build Dim_Campaign from campaign reference data."""
    if campaign_df.empty:
        return pd.DataFrame(columns=['Campaign_ID', 'Campaign_Name', 'Objective', 'Budget'])

    dim = campaign_df[['campaign_id', 'campaign_name', 'objective', 'monthly_budget']].copy()
    dim.columns = ['Campaign_ID', 'Campaign_Name', 'Objective', 'Budget']
    dim = dim.drop_duplicates(subset=['Campaign_ID']).reset_index(drop=True)
    return dim


def build_landing_page_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """Build Dim_LandingPage from unique landing pages."""
    if 'landing_page' not in df.columns:
        return pd.DataFrame()

    pages = df[['landing_page', 'page_category']].drop_duplicates().copy()
    pages = pages[pages['landing_page'].notna()].reset_index(drop=True)
    pages.insert(0, 'LandingPage_ID', range(1, len(pages) + 1))
    pages.columns = ['LandingPage_ID', 'Page_URL', 'Page_Category']
    return pages


def build_device_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """Build Dim_Device from unique device combinations."""
    if 'device_type' not in df.columns:
        return pd.DataFrame()

    devices = df[['device_type', 'os', 'browser']].drop_duplicates().copy()
    devices = devices.reset_index(drop=True)
    devices.insert(0, 'Device_ID', range(1, len(devices) + 1))
    devices.columns = ['Device_ID', 'Device_Type', 'OS', 'Browser']
    return devices


def build_geography_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """Build Dim_Geography from unique geography combinations."""
    geo_cols = ['geo_country', 'geo_region', 'geo_city']
    if not all(c in df.columns for c in geo_cols):
        return pd.DataFrame()

    geos = df[geo_cols].drop_duplicates().copy()
    geos = geos.reset_index(drop=True)
    geos.insert(0, 'Geography_ID', range(1, len(geos) + 1))
    geos.columns = ['Geography_ID', 'Country', 'Region', 'City']
    return geos


def build_fact_table(df: pd.DataFrame, dim_channel: pd.DataFrame,
                     dim_landing_page: pd.DataFrame, dim_device: pd.DataFrame,
                     dim_geography: pd.DataFrame) -> pd.DataFrame:
    """
    Build Fact_FunnelEvent by mapping dimension surrogate keys.
    """
    fact = df.copy()

    # Map Channel_ID
    if not dim_channel.empty:
        channel_map = dim_channel.set_index('Channel_Name')['Channel_ID'].to_dict()
        fact['channel_id_fk'] = fact['channel_name'].map(channel_map)
    else:
        fact['channel_id_fk'] = None

    # Map LandingPage_ID
    if not dim_landing_page.empty:
        lp_map = dim_landing_page.set_index('Page_URL')['LandingPage_ID'].to_dict()
        fact['landingpage_id_fk'] = fact['landing_page'].map(lp_map)
    else:
        fact['landingpage_id_fk'] = None

    # Map Device_ID
    if not dim_device.empty:
        device_key = dim_device.copy()
        device_key['key'] = (
            device_key['Device_Type'] + '|' +
            device_key['OS'] + '|' +
            device_key['Browser']
        )
        device_map = device_key.set_index('key')['Device_ID'].to_dict()
        fact['device_key'] = fact['device_type'] + '|' + fact['os'] + '|' + fact['browser']
        fact['device_id_fk'] = fact['device_key'].map(device_map)
        fact.drop(columns=['device_key'], inplace=True)
    else:
        fact['device_id_fk'] = None

    # Map Geography_ID
    if not dim_geography.empty:
        geo_key = dim_geography.copy()
        geo_key['key'] = (
            geo_key['Country'] + '|' +
            geo_key['Region'] + '|' +
            geo_key['City']
        )
        geo_map = geo_key.set_index('key')['Geography_ID'].to_dict()
        fact['geo_key'] = (
            fact['geo_country'] + '|' +
            fact['geo_region'] + '|' +
            fact['geo_city']
        )
        fact['geography_id_fk'] = fact['geo_key'].map(geo_map)
        fact.drop(columns=['geo_key'], inplace=True)
    else:
        fact['geography_id_fk'] = None

    # Select and rename final columns
    result = pd.DataFrame({
        'Event_ID': fact['event_id'],
        'User_ID': fact['user_pseudo_id'],
        'Session_ID': fact['ga_session_id'].astype(str),
        'Campaign_ID': fact['campaign_id'],
        'Channel_ID': fact['channel_id_fk'],
        'LandingPage_ID': fact['landingpage_id_fk'],
        'Device_ID': fact['device_id_fk'],
        'Geography_ID': fact['geography_id_fk'],
        'Date_ID': fact['date_id'],
        'Funnel_Stage': fact['funnel_stage'],
        'Event_Timestamp': fact['event_timestamp_dt'],
        'Source_Platform': fact.get('traffic_source_source', 'unknown'),
        'Ad_Spend': fact['ad_spend'],
        'Revenue': fact['revenue'],
        'Conversion_Flag': fact['conversion_flag'],
    })

    # Convert nullable integer columns
    for col in ['Channel_ID', 'LandingPage_ID', 'Device_ID', 'Geography_ID', 'Date_ID']:
        result[col] = pd.to_numeric(result[col], errors='coerce')
        result[col] = result[col].astype('Int64')  # Nullable integer type

    return result


def transform_all(sources: dict) -> dict:
    """
    Main transformation orchestrator.

    Parameters:
        sources: Dictionary of extracted DataFrames from extract_all().

    Returns:
        Dictionary with dimension tables and fact table.
    """
    print("=" * 60)
    print("TRANSFORMATION PHASE")
    print("=" * 60)

    ga4_events = sources.get('ga4_events', pd.DataFrame())
    campaign_data = sources.get('campaign_data', pd.DataFrame())
    ad_spend_data = sources.get('ad_spend', pd.DataFrame())

    if ga4_events.empty:
        print("[TRANSFORM] ERROR: No GA4 event data available. Cannot proceed.")
        return {}

    # Step 1: Standardize column names
    print("[TRANSFORM] Step 1: Standardizing column names...")
    df = standardize_columns(ga4_events.copy())
    campaign_df = standardize_columns(campaign_data.copy()) if not campaign_data.empty else pd.DataFrame()
    spend_df = standardize_columns(ad_spend_data.copy()) if not ad_spend_data.empty else pd.DataFrame()

    # Step 2: Normalize timestamps
    print("[TRANSFORM] Step 2: Normalizing timestamps...")
    df = normalize_timestamps(df)

    # Step 3: Map funnel stages
    print("[TRANSFORM] Step 3: Mapping funnel stages...")
    df = map_funnel_stages(df)

    # Step 4: Normalize channels
    print("[TRANSFORM] Step 4: Normalizing channels...")
    df = normalize_channels(df)

    # Step 5: Normalize campaigns
    print("[TRANSFORM] Step 5: Normalizing campaigns...")
    df = normalize_campaigns(df, campaign_df)

    # Step 6: Normalize devices
    print("[TRANSFORM] Step 6: Normalizing devices...")
    df = normalize_devices(df)

    # Step 7: Normalize geography
    print("[TRANSFORM] Step 7: Normalizing geography...")
    df = normalize_geography(df)

    # Step 8: Normalize landing pages
    print("[TRANSFORM] Step 8: Normalizing landing pages...")
    df = normalize_landing_pages(df)

    # Step 9: Handle revenue
    print("[TRANSFORM] Step 9: Handling revenue...")
    df = handle_revenue(df)

    # Step 10: Set conversion flags
    print("[TRANSFORM] Step 10: Setting conversion flags...")
    df = set_conversion_flag(df)

    # Step 11: Generate dimension IDs
    print("[TRANSFORM] Step 11: Generating dimension IDs...")
    df = generate_dimension_ids(df)

    # Step 12: Remove duplicates
    print("[TRANSFORM] Step 12: Removing duplicates...")
    df, dup_count = remove_duplicates(df)

    # Step 13: Allocate ad spend
    print("[TRANSFORM] Step 13: Allocating ad spend...")
    df = allocate_ad_spend(df, spend_df, campaign_df)

    # Step 14: Build dimension tables
    print("[TRANSFORM] Step 14: Building dimension tables...")
    dim_date = build_date_dimension(df)
    dim_channel = build_channel_dimension(df, campaign_df)
    dim_campaign = build_campaign_dimension(campaign_df)
    dim_landing_page = build_landing_page_dimension(df)
    dim_device = build_device_dimension(df)
    dim_geography = build_geography_dimension(df)

    # Step 15: Build fact table
    print("[TRANSFORM] Step 15: Building fact table...")
    fact_funnel = build_fact_table(
        df, dim_channel, dim_landing_page, dim_device, dim_geography
    )

    # Save processed data
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    fact_funnel.to_csv(PROCESSED_DIR / 'fact_funnel_event.csv', index=False)
    dim_date.to_csv(PROCESSED_DIR / 'dim_date.csv', index=False)
    dim_channel.to_csv(PROCESSED_DIR / 'dim_channel.csv', index=False)
    dim_campaign.to_csv(PROCESSED_DIR / 'dim_campaign.csv', index=False)
    dim_landing_page.to_csv(PROCESSED_DIR / 'dim_landing_page.csv', index=False)
    dim_device.to_csv(PROCESSED_DIR / 'dim_device.csv', index=False)
    dim_geography.to_csv(PROCESSED_DIR / 'dim_geography.csv', index=False)
    print(f"[TRANSFORM] Processed data saved to: {PROCESSED_DIR}")

    result = {
        'fact_funnel_event': fact_funnel,
        'dim_date': dim_date,
        'dim_channel': dim_channel,
        'dim_campaign': dim_campaign,
        'dim_landing_page': dim_landing_page,
        'dim_device': dim_device,
        'dim_geography': dim_geography,
        'duplicates_removed': dup_count,
    }

    # Summary
    print("\n--- Transformation Summary ---")
    for name, data in result.items():
        if isinstance(data, pd.DataFrame):
            print(f"  {name}: {len(data)} rows, {len(data.columns)} columns")
        else:
            print(f"  {name}: {data}")
    print()

    return result
