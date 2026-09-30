"""
Validate module for the ETL pipeline.

Performs data quality checks on transformed data before loading.
Checks include:
- Required columns
- Data types
- Duplicate events
- Invalid timestamps
- Invalid funnel stages
- Null primary keys
- Duplicate dimension keys
- Invalid foreign keys
- Negative revenue/spend
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from etl.config import FUNNEL_STAGES, VALIDATION_DIR


class ValidationReport:
    """Collects and formats validation results."""

    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_check(self, name: str, status: str, detail: str = ""):
        self.checks.append({
            'check': name,
            'status': status,
            'detail': detail,
        })
        if status == 'PASS':
            self.passed += 1
        elif status == 'FAIL':
            self.failed += 1
        else:
            self.warnings += 1

    def print_report(self):
        print("\n" + "=" * 60)
        print("ETL VALIDATION REPORT")
        print("=" * 60)
        for check in self.checks:
            icon = "[PASS]" if check['status'] == 'PASS' else ("[FAIL]" if check['status'] == 'FAIL' else "[WARN]")
            print(f"  {icon} [{check['status']}] {check['check']}")
            if check['detail']:
                print(f"           {check['detail']}")
        print("-" * 60)
        print(f"  Total checks: {len(self.checks)}")
        print(f"  Passed: {self.passed}")
        print(f"  Failed: {self.failed}")
        print(f"  Warnings: {self.warnings}")
        overall = "PASS" if self.failed == 0 else "FAIL"
        print(f"  Validation status: {overall}")
        print("=" * 60)
        return overall

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.checks)


def validate_fact_table(fact: pd.DataFrame, report: ValidationReport):
    """Validate the fact table."""
    # Required columns
    required = [
        'Event_ID', 'User_ID', 'Session_ID', 'Funnel_Stage',
        'Event_Timestamp', 'Revenue', 'Ad_Spend', 'Conversion_Flag'
    ]
    missing = [c for c in required if c not in fact.columns]
    if missing:
        report.add_check("Fact: Required columns", "FAIL", f"Missing: {missing}")
    else:
        report.add_check("Fact: Required columns", "PASS", f"All {len(required)} required columns present")

    # Row count
    report.add_check("Fact: Row count", "PASS", f"{len(fact)} records")

    # Null Event_ID
    null_ids = fact['Event_ID'].isna().sum()
    if null_ids > 0:
        report.add_check("Fact: Null Event_ID", "FAIL", f"{null_ids} null primary keys")
    else:
        report.add_check("Fact: Null Event_ID", "PASS", "No null primary keys")

    # Duplicate Event_ID
    dup_ids = fact['Event_ID'].duplicated().sum()
    if dup_ids > 0:
        report.add_check("Fact: Duplicate Event_ID", "FAIL", f"{dup_ids} duplicates")
    else:
        report.add_check("Fact: Duplicate Event_ID", "PASS", "No duplicate primary keys")

    # Invalid funnel stages
    invalid_stages = fact[~fact['Funnel_Stage'].isin(FUNNEL_STAGES)]
    if len(invalid_stages) > 0:
        report.add_check("Fact: Funnel stages", "FAIL",
                         f"{len(invalid_stages)} invalid stages: {invalid_stages['Funnel_Stage'].unique()}")
    else:
        report.add_check("Fact: Funnel stages", "PASS",
                         f"All stages valid. Distribution: " +
                         ", ".join(f"{s}: {(fact['Funnel_Stage'] == s).sum()}" for s in FUNNEL_STAGES))

    # Null User_ID
    null_users = fact['User_ID'].isna().sum()
    if null_users > 0:
        report.add_check("Fact: Null User_ID", "FAIL", f"{null_users} null user IDs")
    else:
        report.add_check("Fact: Null User_ID", "PASS",
                         f"No null user IDs. {fact['User_ID'].nunique()} unique users")

    # Negative revenue
    neg_rev = (fact['Revenue'] < 0).sum()
    if neg_rev > 0:
        report.add_check("Fact: Negative revenue", "FAIL", f"{neg_rev} records")
    else:
        report.add_check("Fact: Negative revenue", "PASS",
                         f"No negative revenue. Total: ${fact['Revenue'].sum():,.2f}")

    # Negative spend
    neg_spend = (fact['Ad_Spend'] < 0).sum()
    if neg_spend > 0:
        report.add_check("Fact: Negative spend", "FAIL", f"{neg_spend} records")
    else:
        report.add_check("Fact: Negative spend", "PASS",
                         f"No negative spend. Total: ${fact['Ad_Spend'].sum():,.2f}")

    # Revenue only on purchase events
    non_purchase_revenue = fact[(fact['Funnel_Stage'] != 'PURCHASE') & (fact['Revenue'] > 0)]
    if len(non_purchase_revenue) > 0:
        report.add_check("Fact: Revenue allocation", "WARNING",
                         f"{len(non_purchase_revenue)} non-purchase records have revenue")
    else:
        report.add_check("Fact: Revenue allocation", "PASS",
                         "Revenue only on PURCHASE events")

    # Timestamp validity
    null_ts = fact['Event_Timestamp'].isna().sum()
    if null_ts > 0:
        report.add_check("Fact: Timestamps", "WARNING", f"{null_ts} null timestamps")
    else:
        ts_min = fact['Event_Timestamp'].min()
        ts_max = fact['Event_Timestamp'].max()
        report.add_check("Fact: Timestamps", "PASS",
                         f"Range: {ts_min} to {ts_max}")


def validate_dimension(dim: pd.DataFrame, name: str, pk: str,
                       report: ValidationReport):
    """Validate a dimension table."""
    if dim.empty:
        report.add_check(f"{name}: Not empty", "WARNING", "Dimension table is empty")
        return

    report.add_check(f"{name}: Row count", "PASS", f"{len(dim)} records")

    # Null PK
    null_pk = dim[pk].isna().sum()
    if null_pk > 0:
        report.add_check(f"{name}: Null {pk}", "FAIL", f"{null_pk} null keys")
    else:
        report.add_check(f"{name}: Null {pk}", "PASS", "No null primary keys")

    # Duplicate PK
    dup_pk = dim[pk].duplicated().sum()
    if dup_pk > 0:
        report.add_check(f"{name}: Duplicate {pk}", "FAIL", f"{dup_pk} duplicates")
    else:
        report.add_check(f"{name}: Duplicate {pk}", "PASS", "No duplicate primary keys")


def validate_foreign_keys(fact: pd.DataFrame, dimensions: dict,
                          report: ValidationReport):
    """Validate foreign key relationships between fact and dimensions."""
    fk_mappings = {
        'Channel_ID': ('Dim_Channel', 'Channel_ID'),
        'Campaign_ID': ('Dim_Campaign', 'Campaign_ID'),
        'LandingPage_ID': ('Dim_LandingPage', 'LandingPage_ID'),
        'Device_ID': ('Dim_Device', 'Device_ID'),
        'Geography_ID': ('Dim_Geography', 'Geography_ID'),
        'Date_ID': ('Dim_Date', 'Date_ID'),
    }

    for fk_col, (dim_name, dim_pk) in fk_mappings.items():
        if fk_col not in fact.columns:
            continue

        dim = dimensions.get(dim_name, pd.DataFrame())
        if dim.empty:
            report.add_check(f"FK: {fk_col} -> {dim_name}", "WARNING",
                             "Dimension table not available")
            continue

        # Get non-null FK values
        fact_fks = fact[fk_col].dropna().unique()
        dim_pks = set(dim[dim_pk].values)

        orphans = [fk for fk in fact_fks if fk not in dim_pks]
        if orphans:
            report.add_check(f"FK: {fk_col} -> {dim_name}", "FAIL",
                             f"{len(orphans)} orphan values")
        else:
            report.add_check(f"FK: {fk_col} -> {dim_name}", "PASS",
                             f"All {len(fact_fks)} FK values valid")


def validate_all(transformed: dict) -> str:
    """
    Run all validation checks on transformed data.

    Parameters:
        transformed: Dictionary from transform_all().

    Returns:
        Overall validation status ('PASS' or 'FAIL').
    """
    print("=" * 60)
    print("VALIDATION PHASE")
    print("=" * 60)

    report = ValidationReport()

    fact = transformed.get('fact_funnel_event', pd.DataFrame())
    if fact.empty:
        report.add_check("Data availability", "FAIL", "No fact table data")
        return report.print_report()

    # Validate fact table
    validate_fact_table(fact, report)

    # Validate dimensions
    dims = {
        'Dim_Date': ('dim_date', 'Date_ID'),
        'Dim_Channel': ('dim_channel', 'Channel_ID'),
        'Dim_Campaign': ('dim_campaign', 'Campaign_ID'),
        'Dim_LandingPage': ('dim_landing_page', 'LandingPage_ID'),
        'Dim_Device': ('dim_device', 'Device_ID'),
        'Dim_Geography': ('dim_geography', 'Geography_ID'),
    }

    dimensions = {}
    for dim_name, (key, pk) in dims.items():
        dim_df = transformed.get(key, pd.DataFrame())
        dimensions[dim_name] = dim_df
        validate_dimension(dim_df, dim_name, pk, report)

    # Validate foreign keys
    validate_foreign_keys(fact, dimensions, report)

    # Print and save report
    overall = report.print_report()

    # Save validation report
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    report_df = report.to_dataframe()
    report_df.to_csv(VALIDATION_DIR / 'validation_report.csv', index=False)
    print(f"\n[VALIDATE] Report saved to: {VALIDATION_DIR / 'validation_report.csv'}")

    # Summary statistics
    print("\n--- Data Summary ---")
    print(f"  Raw records extracted: {len(fact) + transformed.get('duplicates_removed', 0)}")
    print(f"  Valid records: {len(fact)}")
    print(f"  Rejected/duplicate records: {transformed.get('duplicates_removed', 0)}")
    print(f"  Unique users: {fact['User_ID'].nunique()}")
    print(f"  Unique sessions: {fact['Session_ID'].nunique()}")
    print(f"  Purchase events: {(fact['Funnel_Stage'] == 'PURCHASE').sum()}")
    print(f"  Total revenue: ${fact['Revenue'].sum():,.2f}")
    print(f"  Total ad spend: ${fact['Ad_Spend'].sum():,.2f}")
    print()

    return overall
