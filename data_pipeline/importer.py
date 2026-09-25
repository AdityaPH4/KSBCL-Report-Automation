from .parser import parse_d88
from .cleaner import clean_d88
from .serial import assign_serial_numbers
from .sheets import (
    get_sheet,
    get_next_serial,
    already_imported,
    append_data
)


def import_report(file_path, report_date):

    # 1. Excel → DataFrame
    df = parse_d88(file_path)

    # 2. Clean
    df = clean_d88(df)

    # 3. Identify this report
    import_id = f"D88-{report_date:%Y-%m-%d}"

    # 4. Open Google Sheet
    sheet = get_sheet()

    # 5. Don't import same report twice
    if already_imported(sheet, import_id):
        print(f"{import_id} already imported.")
        return

    # 6. Get next serial
    next_serial = get_next_serial(sheet)

    # 7. Generate OUR serial numbers
    df = assign_serial_numbers(
        df,
        next_serial
    )

    # 8. Add import metadata
    df.insert(1, "Import ID", import_id)

    # 9. Append to Sheet
    append_data(sheet, df)

    print(
        f"Imported {len(df)} rows "
        f"starting from {next_serial}"
    )