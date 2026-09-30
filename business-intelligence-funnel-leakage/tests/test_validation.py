"""
Test suite for ETL validation logic.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.validate import (
    ValidationReport,
    validate_fact_table,
    validate_dimension,
    validate_foreign_keys,
)
from etl.config import FUNNEL_STAGES


class TestValidationReport:
    """Test the ValidationReport class."""

    def test_pass_count(self):
        report = ValidationReport()
        report.add_check("Test 1", "PASS")
        report.add_check("Test 2", "PASS")
        assert report.passed == 2
        assert report.failed == 0

    def test_fail_count(self):
        report = ValidationReport()
        report.add_check("Test 1", "FAIL")
        assert report.failed == 1

    def test_to_dataframe(self):
        report = ValidationReport()
        report.add_check("Test 1", "PASS", "detail")
        df = report.to_dataframe()
        assert len(df) == 1
        assert df.iloc[0]['check'] == "Test 1"


class TestFactValidation:
    """Test fact table validation."""

    def _make_valid_fact(self):
        return pd.DataFrame({
            'Event_ID': ['e1', 'e2', 'e3'],
            'User_ID': ['u1', 'u2', 'u3'],
            'Session_ID': ['s1', 's2', 's3'],
            'Campaign_ID': ['C001', 'C002', 'C001'],
            'Channel_ID': [1, 2, 1],
            'LandingPage_ID': [1, 1, 2],
            'Device_ID': [1, 2, 1],
            'Geography_ID': [1, 2, 3],
            'Date_ID': [20240101, 20240102, 20240103],
            'Funnel_Stage': ['IMPRESSION', 'CLICK', 'PURCHASE'],
            'Event_Timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
            'Source_Platform': ['google', 'google', 'facebook'],
            'Ad_Spend': [1.0, 0.5, 0.0],
            'Revenue': [0.0, 0.0, 100.0],
            'Conversion_Flag': [0, 0, 1],
        })

    def test_valid_fact_passes(self):
        report = ValidationReport()
        fact = self._make_valid_fact()
        validate_fact_table(fact, report)
        assert report.failed == 0

    def test_null_event_id_fails(self):
        report = ValidationReport()
        fact = self._make_valid_fact()
        fact.loc[0, 'Event_ID'] = None
        validate_fact_table(fact, report)
        assert report.failed > 0

    def test_duplicate_event_id_fails(self):
        report = ValidationReport()
        fact = self._make_valid_fact()
        fact.loc[1, 'Event_ID'] = 'e1'
        validate_fact_table(fact, report)
        assert report.failed > 0

    def test_invalid_funnel_stage_fails(self):
        report = ValidationReport()
        fact = self._make_valid_fact()
        fact.loc[0, 'Funnel_Stage'] = 'INVALID'
        validate_fact_table(fact, report)
        assert report.failed > 0

    def test_negative_revenue_fails(self):
        report = ValidationReport()
        fact = self._make_valid_fact()
        fact.loc[0, 'Revenue'] = -10.0
        validate_fact_table(fact, report)
        assert report.failed > 0


class TestDimensionValidation:
    """Test dimension validation."""

    def test_valid_dimension_passes(self):
        report = ValidationReport()
        dim = pd.DataFrame({
            'Channel_ID': [1, 2, 3],
            'Channel_Name': ['Organic', 'Paid', 'Social'],
        })
        validate_dimension(dim, "Dim_Channel", "Channel_ID", report)
        assert report.failed == 0

    def test_duplicate_pk_fails(self):
        report = ValidationReport()
        dim = pd.DataFrame({
            'Channel_ID': [1, 1, 3],
            'Channel_Name': ['A', 'B', 'C'],
        })
        validate_dimension(dim, "Dim_Channel", "Channel_ID", report)
        assert report.failed > 0

    def test_empty_dimension_warns(self):
        report = ValidationReport()
        validate_dimension(pd.DataFrame(), "Dim_Empty", "ID", report)
        assert report.warnings > 0


class TestForeignKeyValidation:
    """Test foreign key validation."""

    def test_valid_fks_pass(self):
        report = ValidationReport()
        fact = pd.DataFrame({
            'Channel_ID': [1, 2],
        })
        dims = {
            'Dim_Channel': pd.DataFrame({'Channel_ID': [1, 2, 3]}),
        }
        validate_foreign_keys(fact, dims, report)
        assert report.failed == 0

    def test_orphan_fk_fails(self):
        report = ValidationReport()
        fact = pd.DataFrame({
            'Channel_ID': [1, 99],
        })
        dims = {
            'Dim_Channel': pd.DataFrame({'Channel_ID': [1, 2, 3]}),
        }
        validate_foreign_keys(fact, dims, report)
        assert report.failed > 0
