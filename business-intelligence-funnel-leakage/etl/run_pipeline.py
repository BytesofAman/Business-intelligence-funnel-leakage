"""
ETL Pipeline Runner.

Orchestrates the complete ETL process:
1. Extract raw data from source files
2. Transform data into star schema format
3. Validate data quality
4. Load into MySQL data warehouse

Usage:
    python -m etl.run_pipeline          # Run full pipeline
    python -m etl.run_pipeline --no-db  # Run without database loading (CSV only)
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from etl.extract import extract_all
from etl.transform import transform_all
from etl.validate import validate_all
from etl.load import load_all


def run_pipeline(skip_db: bool = False):
    """
    Execute the complete ETL pipeline.

    Parameters:
        skip_db: If True, skip database loading (useful for testing).
    """
    start_time = time.time()

    print("+" + "=" * 58 + "+")
    print("|  CROSS-CHANNEL MARKETING FUNNEL LEAKAGE INTELLIGENCE    |")
    print("|  ETL Pipeline                                           |")
    print("|  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " * 36 + "|")
    print("+" + "=" * 58 + "+")
    print()

    # Phase 1: EXTRACT
    print("[*] Phase 1/4: EXTRACTION")
    try:
        sources = extract_all()
        ga4_count = len(sources.get('ga4_events', []))
        if ga4_count == 0:
            print("[PIPELINE] FATAL: No GA4 event data found.")
            print("[PIPELINE]        Place ga4_events.csv in data/raw/ga4/")
            print("[PIPELINE]        Run: python data/raw/ga4/generate_raw_data.py")
            return False
    except Exception as e:
        print(f"[PIPELINE] EXTRACTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Phase 2: TRANSFORM
    print("[*] Phase 2/4: TRANSFORMATION")
    try:
        transformed = transform_all(sources)
        if not transformed:
            print("[PIPELINE] TRANSFORMATION FAILED: No output produced.")
            return False
    except Exception as e:
        print(f"[PIPELINE] TRANSFORMATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Phase 3: VALIDATE
    print("[*] Phase 3/4: VALIDATION")
    try:
        validation_status = validate_all(transformed)
    except Exception as e:
        print(f"[PIPELINE] VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        validation_status = "ERROR"

    # Phase 4: LOAD
    if skip_db:
        print("[*] Phase 4/4: LOADING (SKIPPED - --no-db flag)")
        print("[PIPELINE] Data saved as CSV in data/processed/")
        load_status = True
    else:
        print("[*] Phase 4/4: LOADING")
        try:
            load_status = load_all(transformed)
        except Exception as e:
            print(f"[PIPELINE] LOADING FAILED: {e}")
            import traceback
            traceback.print_exc()
            load_status = False

    # Final Report
    elapsed = time.time() - start_time
    print()
    print("+" + "=" * 58 + "+")
    print("|  PIPELINE EXECUTION REPORT                              |")
    print("+" + "=" * 58 + "+")

    fact = transformed.get('fact_funnel_event')
    if fact is not None:
        print(f"|  Records processed:  {len(fact):>10,}                       |")
        print(f"|  Unique users:       {fact['User_ID'].nunique():>10,}                       |")
        print(f"|  Unique sessions:    {fact['Session_ID'].nunique():>10,}                       |")
        print(f"|  Purchase events:    {(fact['Funnel_Stage'] == 'PURCHASE').sum():>10,}                       |")
        print(f"|  Total revenue:      ${fact['Revenue'].sum():>12,.2f}                     |")
        print(f"|  Total ad spend:     ${fact['Ad_Spend'].sum():>12,.2f}                     |")

    print(f"|  Validation:         {'PASS' if validation_status == 'PASS' else 'NEEDS REVIEW':>10}                       |")
    print(f"|  DB Loading:         {'SUCCESS' if load_status else 'SKIPPED/FAILED':>10}                       |")
    print(f"|  Elapsed time:       {elapsed:>10.1f}s                      |")
    print("+" + "=" * 58 + "+")

    return validation_status == 'PASS' and load_status


if __name__ == '__main__':
    skip_db = '--no-db' in sys.argv
    success = run_pipeline(skip_db=skip_db)
    sys.exit(0 if success else 1)
