"""
One-time backfill: loads the existing D88_Bottles_Master.xlsx history
into robinhood.d88_bottles_sales on the AWS Postgres DB.

Safe to re-run: inserts are keyed on serial_no, so rows already present
are skipped rather than duplicated.
"""

import pandas as pd

from data_pipeline.db import get_connection, Table
from data_pipeline.specs import D88_BOTTLES

MASTER_PATH = "D88_Bottles_Master.xlsx"


def main():
    master_df = pd.read_excel(MASTER_PATH)
    print(f"Loaded {len(master_df)} rows from {MASTER_PATH}")

    table = Table(D88_BOTTLES)
    conn = get_connection()
    try:
        table.ensure_schema(conn)
        inserted = table.append_dataframe(conn, master_df)
    finally:
        conn.close()

    print(
        f"Backfilled {inserted} rows into "
        f"robinhood.{table.name}"
    )


if __name__ == "__main__":
    main()
