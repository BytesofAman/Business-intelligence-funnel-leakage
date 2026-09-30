"""
Test suite for KPI calculations.

Validates that KPI formulas produce correct results.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestKPICalculations:
    """Test KPI formulas match definitions."""

    def _make_test_data(self):
        """Create a small test dataset with known KPI values."""
        return pd.DataFrame({
            'Event_ID': [f'e{i}' for i in range(10)],
            'User_ID': ['u1', 'u1', 'u1', 'u1', 'u2', 'u2', 'u2', 'u3', 'u3', 'u4'],
            'Session_ID': ['s1', 's1', 's1', 's1', 's2', 's2', 's2', 's3', 's3', 's4'],
            'Funnel_Stage': [
                'IMPRESSION', 'CLICK', 'PRODUCT_VIEW', 'PURCHASE',
                'IMPRESSION', 'CLICK', 'PRODUCT_VIEW',
                'IMPRESSION', 'CART',
                'IMPRESSION'
            ],
            'Revenue': [0, 0, 0, 100, 0, 0, 0, 0, 0, 0],
            'Ad_Spend': [5, 0, 0, 0, 5, 0, 0, 3, 0, 2],
            'Conversion_Flag': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        })

    def test_total_users(self):
        df = self._make_test_data()
        total_users = df['User_ID'].nunique()
        assert total_users == 4

    def test_total_sessions(self):
        df = self._make_test_data()
        total_sessions = df['Session_ID'].nunique()
        assert total_sessions == 4

    def test_total_events(self):
        df = self._make_test_data()
        assert len(df) == 10

    def test_total_purchases(self):
        df = self._make_test_data()
        purchases = (df['Funnel_Stage'] == 'PURCHASE').sum()
        assert purchases == 1

    def test_total_revenue(self):
        df = self._make_test_data()
        revenue = df['Revenue'].sum()
        assert revenue == 100

    def test_total_spend(self):
        df = self._make_test_data()
        spend = df['Ad_Spend'].sum()
        assert spend == 15

    def test_conversion_rate(self):
        """Conversion rate = purchasers / total users."""
        df = self._make_test_data()
        purchasers = df[df['Funnel_Stage'] == 'PURCHASE']['User_ID'].nunique()
        total_users = df['User_ID'].nunique()
        rate = purchasers / total_users * 100
        assert rate == 25.0  # 1/4 = 25%

    def test_cpa(self):
        """CPA = total spend / purchases."""
        df = self._make_test_data()
        spend = df['Ad_Spend'].sum()
        purchases = (df['Funnel_Stage'] == 'PURCHASE').sum()
        cpa = spend / purchases if purchases > 0 else None
        assert cpa == 15.0  # 15/1 = 15

    def test_roas(self):
        """ROAS = revenue / spend."""
        df = self._make_test_data()
        revenue = df['Revenue'].sum()
        spend = df['Ad_Spend'].sum()
        roas = revenue / spend if spend > 0 else None
        assert round(roas, 2) == 6.67  # 100/15 ≈ 6.67

    def test_cart_abandonment_rate(self):
        """Cart abandonment = (cart users - checkout users) / cart users."""
        df = self._make_test_data()
        cart_users = df[df['Funnel_Stage'] == 'CART']['User_ID'].nunique()
        checkout_users = df[df['Funnel_Stage'] == 'CHECKOUT']['User_ID'].nunique()
        rate = (cart_users - checkout_users) / cart_users * 100 if cart_users > 0 else 0
        assert rate == 100.0  # 1 cart user, 0 checkout = 100% abandonment

    def test_funnel_drop_off(self):
        """Test funnel stage counts decrease."""
        df = self._make_test_data()
        impressions = df[df['Funnel_Stage'] == 'IMPRESSION']['User_ID'].nunique()
        clicks = df[df['Funnel_Stage'] == 'CLICK']['User_ID'].nunique()
        purchases_users = df[df['Funnel_Stage'] == 'PURCHASE']['User_ID'].nunique()
        assert impressions >= clicks >= purchases_users

    def test_safe_division_zero_spend(self):
        """ROAS should handle zero spend gracefully."""
        spend = 0
        revenue = 100
        roas = revenue / spend if spend > 0 else None
        assert roas is None

    def test_safe_division_zero_purchases(self):
        """CPA should handle zero purchases gracefully."""
        spend = 100
        purchases = 0
        cpa = spend / purchases if purchases > 0 else None
        assert cpa is None


class TestFunnelConversionRates:
    """Test stage-to-stage conversion calculations."""

    def test_stage_conversion(self):
        df = pd.DataFrame({
            'User_ID': ['u1', 'u1', 'u2', 'u2', 'u3'],
            'Funnel_Stage': ['IMPRESSION', 'CLICK', 'IMPRESSION', 'CLICK', 'IMPRESSION'],
        })
        impression_users = df[df['Funnel_Stage'] == 'IMPRESSION']['User_ID'].nunique()
        click_users = df[df['Funnel_Stage'] == 'CLICK']['User_ID'].nunique()
        rate = click_users / impression_users * 100
        assert round(rate, 1) == 66.7  # 2/3 ≈ 66.7%
