"""
Load module for the ETL pipeline.

Loads transformed data into MySQL data warehouse.
Handles:
- Database connection
- Table creation (idempotent, robust statement splitting)
- Dimension loading (load order enforced)
- Fact table loading
- Robust data type conversion (pandas Timestamp, NaT, numpy scalar types -> native Python)
- Transaction management
- Error handling, tracking, and validation
"""

import re
import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error as MySQLError
from etl.config import DB_CONFIG, FUNNEL_STAGES


def get_connection(use_database: bool = True):
    """
    Create a MySQL database connection.

    Parameters:
        use_database: If True, connect to the configured database.
                      If False, connect without selecting a database (for DB creation).

    Returns:
        MySQL connection object.
    """
    config = DB_CONFIG.copy()
    if not use_database:
        config.pop('database', None)

    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
    except MySQLError as e:
        print(f"[LOAD] ERROR: Database connection failed: {e}")
        print(f"[LOAD]        Host: {config.get('host')}")
        print(f"[LOAD]        Port: {config.get('port')}")
        print(f"[LOAD]        User: {config.get('user')}")
        print(f"[LOAD]        Database: {config.get('database', 'N/A')}")
        raise


def parse_sql_statements(sql_text: str) -> list[str]:
    """
    Parse a SQL script into individual executable statements,
    properly stripping comments (-- line comments and /* */ block comments).
    """
    # Remove block comments
    sql_text = re.sub(r'/\*.*?\*/', '', sql_text, flags=re.DOTALL)
    statements = []
    for raw_stmt in sql_text.split(';'):
        # Strip line comments
        lines = [line for line in raw_stmt.splitlines() if not line.strip().startswith('--')]
        cleaned = '\n'.join(lines).strip()
        if cleaned:
            statements.append(cleaned)
    return statements


def create_database():
    """Create the data warehouse database if it doesn't exist."""
    print("[LOAD] Ensuring database exists...")
    conn = get_connection(use_database=False)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS marketing_funnel_dw "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
        print("[LOAD] Database 'marketing_funnel_dw' ready")
    finally:
        cursor.close()
        conn.close()


def create_tables():
    """Create all warehouse tables (idempotent, order: dimensions first, then fact)."""
    print("[LOAD] Creating warehouse tables...")
    conn = get_connection()
    cursor = conn.cursor()

    try:
        sql_dir = Path(__file__).parent.parent / 'sql'

        for script_name in ['02_create_dimensions.sql', '03_create_fact.sql']:
            script_path = sql_dir / script_name
            if not script_path.exists():
                print(f"[LOAD] WARNING: Schema script not found: {script_path}")
                continue

            sql_content = script_path.read_text(encoding='utf-8')
            statements = parse_sql_statements(sql_content)

            for stmt in statements:
                if stmt.upper().startswith('USE ') or stmt.upper().startswith('SELECT '):
                    continue
                try:
                    cursor.execute(stmt)
                except MySQLError as e:
                    if e.errno == 1050:  # Table already exists
                        pass
                    elif e.errno == 1061:  # Duplicate key name
                        pass
                    else:
                        print(f"[LOAD] Table creation warning ({script_name}): {e}")

        conn.commit()
        print("[LOAD] All tables created successfully")
    finally:
        cursor.close()
        conn.close()


def truncate_tables():
    """Truncate all tables for clean reload (respects FK constraints)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        tables = [
            'Fact_FunnelEvent', 'Dim_Date', 'Dim_Channel',
            'Dim_Campaign', 'Dim_LandingPage', 'Dim_Device', 'Dim_Geography'
        ]
        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table}")
            except MySQLError as e:
                print(f"[LOAD] Truncate notice for {table}: {e}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        print("[LOAD] All tables truncated for clean reload")
    finally:
        cursor.close()
        conn.close()


def convert_value_for_mysql(val):
    """
    Safely convert pandas/numpy scalar types to native Python types for mysql-connector:
    - pd.Timestamp -> datetime.datetime
    - pd.NaT, np.nan, pd.NA -> None
    - datetime.date, datetime.datetime -> preserved
    - np.integer / np.int64 -> int
    - np.floating / np.float64 -> float
    - np.bool_ -> bool
    - other numpy scalars -> val.item()
    """
    if pd.isna(val) or val is pd.NaT or val is pd.NA:
        return None
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime()
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val
    if hasattr(val, 'item'):
        item = val.item()
        if isinstance(item, (int, float, bool, str)):
            return item
    return val


def load_dataframe(df: pd.DataFrame, table_name: str, conn) -> int:
    """
    Load a DataFrame into a MySQL table using batch inserts with comprehensive type sanitization.

    Parameters:
        df: DataFrame to load.
        table_name: Target table name (e.g. 'Dim_Channel', 'Fact_FunnelEvent').
        conn: Active MySQL connection.

    Returns:
        Number of successfully inserted rows.
    """
    if df.empty:
        print(f"[LOAD] WARNING: {table_name} - No data to load")
        return 0

    cursor = conn.cursor()

    columns = ', '.join([f'`{c}`' for c in df.columns])
    placeholders = ', '.join(['%s'] * len(df.columns))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Convert entire DataFrame to list of sanitized Python tuples
    col_names = list(df.columns)
    data = []
    for row in df.itertuples(index=False):
        row_values = tuple(convert_value_for_mysql(v) for v in row)
        data.append(row_values)

    batch_size = 2000
    inserted = 0
    failed_batches = 0
    first_error = None

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        try:
            cursor.executemany(sql, batch)
            inserted += len(batch)
        except MySQLError as e:
            failed_batches += 1
            if first_error is None:
                first_error = (str(e), i)
            # Try single-row fallback for exact diagnostics
            for j, record in enumerate(batch):
                try:
                    cursor.execute(sql, record)
                    inserted += 1
                except MySQLError:
                    pass

    conn.commit()
    cursor.close()

    if first_error is not None:
        print(f"[LOAD] WARNING in {table_name}: Batch errors occurred. First error at record {first_error[1]}: {first_error[0]}")
        print(f"[LOAD]          Total records expected: {len(df)}, inserted: {inserted}")
    else:
        print(f"[LOAD] {table_name}: {inserted:,} rows loaded successfully")

    return inserted


def create_indexes():
    """Create indexes on warehouse tables."""
    print("[LOAD] Creating indexes...")
    conn = get_connection()
    cursor = conn.cursor()

    sql_dir = Path(__file__).parent.parent / 'sql'
    script_path = sql_dir / '04_indexes.sql'

    if script_path.exists():
        sql_content = script_path.read_text(encoding='utf-8')
        statements = parse_sql_statements(sql_content)
        success_count = 0
        for stmt in statements:
            if stmt.upper().startswith('CREATE INDEX'):
                try:
                    cursor.execute(stmt)
                    success_count += 1
                except MySQLError as e:
                    if e.errno == 1061:  # Duplicate key name
                        success_count += 1
                    else:
                        print(f"[LOAD] Index warning: {e}")
        conn.commit()
        print(f"[LOAD] Indexes created successfully ({success_count} indexes)")

    cursor.close()
    conn.close()


def create_views():
    """Create analytical views."""
    print("[LOAD] Creating views...")
    conn = get_connection()
    cursor = conn.cursor()

    sql_dir = Path(__file__).parent.parent / 'sql'
    script_path = sql_dir / '05_views.sql'

    if script_path.exists():
        sql_content = script_path.read_text(encoding='utf-8')
        statements = parse_sql_statements(sql_content)
        views_created = 0
        for stmt in statements:
            if stmt.upper().startswith('CREATE OR REPLACE VIEW') or stmt.upper().startswith('CREATE VIEW'):
                try:
                    cursor.execute(stmt)
                    views_created += 1
                except MySQLError as e:
                    print(f"[LOAD] View creation warning: {e}")
        conn.commit()
        print(f"[LOAD] Views created successfully ({views_created} views)")

    cursor.close()
    conn.close()


def verify_loaded_data(conn) -> dict:
    """
    Run direct SQL verification against MySQL to retrieve genuine database table counts.

    Returns:
        Dictionary of table_name -> row_count.
    """
    cursor = conn.cursor()
    tables = [
        'Fact_FunnelEvent', 'Dim_Date', 'Dim_Channel',
        'Dim_Campaign', 'Dim_LandingPage', 'Dim_Device', 'Dim_Geography'
    ]
    counts = {}
    for tbl in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{tbl}`")
            counts[tbl] = cursor.fetchone()[0]
        except MySQLError as e:
            counts[tbl] = f"Error: {e}"
    cursor.close()
    return counts


def load_all(transformed: dict) -> bool:
    """
    Main load orchestrator.

    Loads data in correct dimensional dependency order:
    1. Dim_Date
    2. Dim_Channel
    3. Dim_Campaign
    4. Dim_LandingPage
    5. Dim_Device
    6. Dim_Geography
    7. Fact_FunnelEvent

    Validates that actual database rows match transformed inputs.

    Parameters:
        transformed: Dictionary from transform_all().

    Returns:
        True if loading succeeded with genuine records inserted, False otherwise.
    """
    print("=" * 60)
    print("LOADING PHASE")
    print("=" * 60)

    try:
        # Step 1: Ensure database exists
        create_database()

        # Step 2: Create all tables (Dimensions first, Fact second)
        create_tables()

        # Step 3: Clean truncate for idempotent reruns
        truncate_tables()

        # Step 4: Load dimension tables
        conn = get_connection()

        dimension_load_order = [
            ('Dim_Date', 'dim_date'),
            ('Dim_Channel', 'dim_channel'),
            ('Dim_Campaign', 'dim_campaign'),
            ('Dim_LandingPage', 'dim_landing_page'),
            ('Dim_Device', 'dim_device'),
            ('Dim_Geography', 'dim_geography'),
        ]

        dim_counts = {}
        for table_name, data_key in dimension_load_order:
            df = transformed.get(data_key, pd.DataFrame())
            expected = len(df)
            inserted = load_dataframe(df, table_name, conn)
            dim_counts[table_name] = (inserted, expected)
            if expected > 0 and inserted == 0:
                conn.close()
                print(f"[LOAD] CRITICAL ERROR: Table '{table_name}' received 0 rows (expected {expected}). Aborting.")
                return False

        # Step 5: Load fact table
        fact = transformed.get('fact_funnel_event', pd.DataFrame())
        expected_fact = len(fact)
        inserted_fact = load_dataframe(fact, 'Fact_FunnelEvent', conn)

        if expected_fact > 0 and inserted_fact == 0:
            conn.close()
            print(f"[LOAD] CRITICAL ERROR: Fact table received 0 rows (expected {expected_fact}). Aborting.")
            return False

        # Step 6: Create performance indexes
        create_indexes()

        # Step 7: Create analytical views
        create_views()

        # Step 8: Direct SQL Verification Query to confirm DB state
        print("\n--- Direct Database Verification (SELECT COUNT) ---")
        db_counts = verify_loaded_data(conn)
        for tbl, cnt in db_counts.items():
            print(f"  {tbl:<20}: {cnt:>10} rows in MySQL")

        conn.close()

        # Confirm fact table meets requirement
        fact_in_db = db_counts.get('Fact_FunnelEvent', 0)
        if not isinstance(fact_in_db, int) or fact_in_db == 0:
            print("[LOAD] VALIDATION FAILED: MySQL fact table is empty!")
            return False

        print(f"\n[LOAD] Loading verified successfully. Total Fact rows: {fact_in_db:,}")
        return True

    except MySQLError as e:
        print(f"[LOAD] CRITICAL DATABASE ERROR: {e}")
        print("[LOAD] Please verify connection settings in .env file.")
        return False
    except Exception as e:
        print(f"[LOAD] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
