import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SCHEMA = "robinhood"

# Maps the DataFrame column names used throughout the pipeline
# (importer.py's metadata columns) to DB columns.
DF_COLUMN_MAP = {
    "Serial No.": "serial_no",
    "Date of Extraction": "date_of_extraction",
    "Import ID": "import_id",
}


def get_connection():
    url = os.environ["DATABASE_URL"]
    is_rds = ".rds.amazonaws.com" in url
    return psycopg.connect(
        url,
        sslmode="require" if is_rds else "prefer",
        connect_timeout=10,
    )


class Table:
    """
    An append-only robinhood.<table_name> table for one ReportSpec:
    serial_no / date_of_extraction / import_id metadata columns, plus
    that feed's own report columns. Never updates or deletes existing
    rows — inserts are keyed on serial_no, so a re-run of an already
    imported report is silently skipped rather than duplicated.
    """

    def __init__(self, spec):
        self.name = spec.table_name
        self.report_columns = list(spec.column_aliases.keys())
        self.column_types = spec.column_types
        self.columns = (
            ["serial_no", "date_of_extraction", "import_id"] + self.report_columns
        )

    def _ddl(self):
        column_defs = ",\n    ".join(
            f"{col} {self.column_types.get(col, 'TEXT')}"
            for col in self.report_columns
        )

        return f"""
CREATE SCHEMA IF NOT EXISTS {SCHEMA};

CREATE TABLE IF NOT EXISTS {SCHEMA}.{self.name} (
    serial_no           BIGINT PRIMARY KEY,
    date_of_extraction  DATE NOT NULL,
    import_id           TEXT NOT NULL,
    {column_defs},
    inserted_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS {self.name}_import_id_idx
    ON {SCHEMA}.{self.name} (import_id);
"""

    def ensure_schema(self, conn):
        with conn.cursor() as cur:
            cur.execute(self._ddl())
        conn.commit()

    def already_imported(self, conn, import_id):
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT EXISTS (SELECT 1 FROM {SCHEMA}.{self.name} WHERE import_id = %s)",
                (import_id,),
            )
            return cur.fetchone()[0]

    def get_next_serial(self, conn):
        with conn.cursor() as cur:
            cur.execute(f"SELECT COALESCE(MAX(serial_no), 0) FROM {SCHEMA}.{self.name}")
            return cur.fetchone()[0] + 1

    def append_dataframe(self, conn, df):
        renamed = df.rename(columns=DF_COLUMN_MAP)
        aligned = renamed.reindex(columns=self.columns).astype(object)
        aligned = aligned.where(pd.notnull(aligned), None)

        records = [tuple(row) for row in aligned.itertuples(index=False, name=None)]

        column_list = ", ".join(self.columns)
        placeholders = ", ".join(["%s"] * len(self.columns))

        insert_sql = f"""
            INSERT INTO {SCHEMA}.{self.name} ({column_list})
            VALUES ({placeholders})
            ON CONFLICT (serial_no) DO NOTHING
        """

        with conn.cursor() as cur:
            cur.executemany(insert_sql, records)
        conn.commit()

        return len(records)
