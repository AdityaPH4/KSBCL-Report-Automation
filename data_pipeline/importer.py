from datetime import datetime
from zoneinfo import ZoneInfo

from .parser import parse_report
from .cleaner import clean_report
from .serial import assign_serial_numbers
from .db import get_connection, Table


def import_report(file_path, report_date, spec):

    # report_date is a "YYYY-MM-DD" string identifying which day's report this is
    report_date = datetime.strptime(report_date, "%Y-%m-%d").date()

    # 1. Excel -> DataFrame
    df = parse_report(file_path, spec)

    # 2. Clean + standardize (e.g. date formats)
    df = clean_report(df, spec)

    # 3. Identify this report
    import_id = f"{spec.import_id_prefix}-{report_date.isoformat()}"

    conn = get_connection()
    table = Table(spec)

    try:
        # 4. Make sure the robinhood schema/table exist
        table.ensure_schema(conn)

        # 5. Don't import same report twice
        if table.already_imported(conn, import_id):
            print(f"{import_id} already imported.")
            return

        # 6. Get next serial
        next_serial = table.get_next_serial(conn)

        # 7. Generate our serial numbers
        df = assign_serial_numbers(df, next_serial)

        # 8. Add import metadata
        extraction_date = datetime.now(ZoneInfo("Asia/Kolkata")).date()
        df.insert(1, "Date of Extraction", extraction_date.isoformat())
        df.insert(2, "Import ID", import_id)

        # 9. Append to robinhood.<table> (Postgres, AWS)
        inserted = table.append_dataframe(conn, df)
    finally:
        conn.close()

    print(
        f"Imported {inserted} rows "
        f"starting from {next_serial}"
    )
