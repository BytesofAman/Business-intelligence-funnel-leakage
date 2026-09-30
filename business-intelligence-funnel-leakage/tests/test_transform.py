"""
Test suite for ETL transformation logic.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.transform import (
    GA4_EVENT_MAPPING,
    MEDIUM_TO_CHANNEL,
    map_funnel_stages,
    normalize_channels,
    normalize_timestamps,
    remove_duplicates,
    handle_revenue,
    set_conversion_flag,
    standardize_columns,
    normalize_devices,
    normalize_geography,
    normalize_landing_pages,
)
from etl.config import FUNNEL_STAGES


class TestFunnelMapping:
    """Test GA4 event to funnel stage mapping."""

    def test_all_ga4_events_mapped(self):
        """Every GA4 event name should map to a valid funnel stage."""
        for event, stage in GA4_EVENT_MAPPING.items():
            assert stage in FUNNEL_STAGES, f"Event '{event}' maps to invalid stage '{stage}'"

    def test_purchase_maps_correctly(self):
        df = pd.DataFrame({'event_name': ['purchase']})
        result = map_funnel_stages(df)
        assert result.iloc[0]['funnel_stage'] == 'PURCHASE'

    def test_view_item_maps_to_product_view(self):
        df = pd.DataFrame({'event_name': ['view_item']})
        result = map_funnel_stages(df)
        assert result.iloc[0]['funnel_stage'] == 'PRODUCT_VIEW'

    def test_add_to_cart_maps_to_cart(self):
        df = pd.DataFrame({'event_name': ['add_to_cart']})
        result = map_funnel_stages(df)
        assert result.iloc[0]['funnel_stage'] == 'CART'

    def test_begin_checkout_maps_to_checkout(self):
        df = pd.DataFrame({'event_name': ['begin_checkout']})
        result = map_funnel_stages(df)
        assert result.iloc[0]['funnel_stage'] == 'CHECKOUT'

    def test_session_start_maps_to_impression(self):
        df = pd.DataFrame({'event_name': ['session_start']})
        result = map_funnel_stages(df)
        assert result.iloc[0]['funnel_stage'] == 'IMPRESSION'

    def test_unmapped_event_removed(self):
        df = pd.DataFrame({'event_name': ['unknown_event', 'purchase']})
        result = map_funnel_stages(df)
        assert len(result) == 1
        assert result.iloc[0]['funnel_stage'] == 'PURCHASE'

    def test_funnel_order_correct(self):
        """Funnel stages must be in correct order."""
        expected_order = [
            'IMPRESSION', 'CLICK', 'LANDING_PAGE',
            'PRODUCT_VIEW', 'CART', 'CHECKOUT', 'PURCHASE'
        ]
        assert FUNNEL_STAGES == expected_order


class TestChannelNormalization:
    """Test channel normalization logic."""

    def test_cpc_maps_to_paid_search(self):
        df = pd.DataFrame({'traffic_source_medium': ['cpc']})
        result = normalize_channels(df)
        assert result.iloc[0]['channel_name'] == 'Paid Search'

    def test_organic_maps_correctly(self):
        df = pd.DataFrame({'traffic_source_medium': ['organic']})
        result = normalize_channels(df)
        assert result.iloc[0]['channel_name'] == 'Organic Search'

    def test_null_medium_defaults_to_direct(self):
        df = pd.DataFrame({'traffic_source_medium': [None]})
        result = normalize_channels(df)
        assert result.iloc[0]['channel_name'] == 'Direct'

    def test_email_maps_correctly(self):
        df = pd.DataFrame({'traffic_source_medium': ['email']})
        result = normalize_channels(df)
        assert result.iloc[0]['channel_name'] == 'Email'


class TestDuplicateHandling:
    """Test duplicate detection and removal."""

    def test_duplicates_removed(self):
        df = pd.DataFrame({
            'event_id': ['a', 'b', 'a', 'c'],
            'value': [1, 2, 3, 4]
        })
        result, count = remove_duplicates(df)
        assert len(result) == 3
        assert count == 1

    def test_no_duplicates(self):
        df = pd.DataFrame({
            'event_id': ['a', 'b', 'c'],
            'value': [1, 2, 3]
        })
        result, count = remove_duplicates(df)
        assert len(result) == 3
        assert count == 0

    def test_first_occurrence_kept(self):
        df = pd.DataFrame({
            'event_id': ['a', 'a'],
            'value': [1, 2]
        })
        result, count = remove_duplicates(df)
        assert result.iloc[0]['value'] == 1


class TestRevenueHandling:
    """Test revenue allocation logic."""

    def test_revenue_only_on_purchase(self):
        df = pd.DataFrame({
            'funnel_stage': ['IMPRESSION', 'CLICK', 'PURCHASE'],
            'ecommerce_purchase_revenue': [100, 50, 200]
        })
        result = handle_revenue(df)
        assert result.iloc[0]['revenue'] == 0.0
        assert result.iloc[1]['revenue'] == 0.0
        assert result.iloc[2]['revenue'] == 200.0

    def test_missing_revenue_defaults_to_zero(self):
        df = pd.DataFrame({
            'funnel_stage': ['PURCHASE'],
            'ecommerce_purchase_revenue': [None]
        })
        result = handle_revenue(df)
        assert result.iloc[0]['revenue'] == 0.0


class TestConversionFlag:
    """Test conversion flag logic."""

    def test_purchase_flagged(self):
        df = pd.DataFrame({'funnel_stage': ['PURCHASE', 'CART', 'CHECKOUT']})
        result = set_conversion_flag(df)
        assert result.iloc[0]['conversion_flag'] == 1
        assert result.iloc[1]['conversion_flag'] == 0
        assert result.iloc[2]['conversion_flag'] == 0


class TestMissingValues:
    """Test missing value handling."""

    def test_null_device_defaults(self):
        df = pd.DataFrame({'device_category': [None], 'device_operating_system': [None], 'device_browser': [None]})
        result = normalize_devices(df)
        assert result.iloc[0]['device_type'] == 'unknown'
        assert result.iloc[0]['os'] == 'Unknown'
        assert result.iloc[0]['browser'] == 'Unknown'

    def test_null_geography_defaults(self):
        df = pd.DataFrame({'geo_country': [None], 'geo_region': [None], 'geo_city': [None]})
        result = normalize_geography(df)
        assert result.iloc[0]['geo_country'] == 'Unknown'

    def test_null_landing_page_defaults(self):
        df = pd.DataFrame({'landing_page': [None]})
        result = normalize_landing_pages(df)
        assert result.iloc[0]['landing_page'] == '/home'


class TestTimestamps:
    """Test timestamp normalization."""

    def test_microsecond_conversion(self):
        # 2024-01-01 00:00:00 UTC in microseconds
        ts = 1704067200000000
        df = pd.DataFrame({'event_timestamp': [ts], 'event_date': [20240101]})
        result = normalize_timestamps(df)
        assert result.iloc[0]['event_timestamp_dt'].year == 2024
        assert result.iloc[0]['event_timestamp_dt'].month == 1
        assert result.iloc[0]['event_timestamp_dt'].day == 1

    def test_invalid_timestamp_handled(self):
        df = pd.DataFrame({'event_timestamp': ['invalid'], 'event_date': ['invalid']})
        result = normalize_timestamps(df)
        assert pd.isna(result.iloc[0]['event_timestamp_dt'])


class TestColumnStandardization:
    """Test column name standardization."""

    def test_spaces_replaced(self):
        df = pd.DataFrame({'Column Name': [1]})
        result = standardize_columns(df)
        assert 'column_name' in result.columns

    def test_case_lowered(self):
        df = pd.DataFrame({'UPPER': [1]})
        result = standardize_columns(df)
        assert 'upper' in result.columns
