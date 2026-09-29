from datetime import datetime
from zoneinfo import ZoneInfo

from .parser import parse_d88
from .cleaner import clean_d88
from .serial import assign_serial_numbers
from .sheets import (
    load_master,
    get_next_serial,
    already_imported,
    append_data,
)


def import_report(file_path, report_date):

    # report_date is a "YYYY-MM-DD" string identifying which day's report this is
    report_date = datetime.strptime(report_date, "%Y-%m-%d").date()

    # 1. Excel -> DataFrame
    df = parse_d88(file_path)

    # 2. Clean + standardize (e.g. date formats)
    df = clean_d88(df)

    # 3. Identify this report
    import_id = f"D88-{report_date.isoformat()}"

    # 4. Load master sheet
    master_df = load_master()

    # 5. Don't import same report twice
    if already_imported(master_df, import_id):
        print(f"{import_id} already imported.")
        return

    # 6. Get next serial
    next_serial = get_next_serial(master_df)

    # 7. Generate our serial numbers
    df = assign_serial_numbers(df, next_serial)

    # 8. Add import metadata
    extraction_date = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    df.insert(1, "Date of Extraction", extraction_date.isoformat())
    df.insert(2, "Import ID", import_id)

    # 9. Append to master sheet
    append_data(master_df, df)

    print(
        f"Imported {len(df)} rows "
        f"starting from {next_serial}"
    )
