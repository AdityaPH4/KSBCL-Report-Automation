import re
import sys
from pathlib import Path

from data_pipeline.importer import import_report

DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")

DEFAULT_FILE = "D88_Report_2026-09-24.xlsx"


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE

    match = DATE_PATTERN.search(Path(file_path).stem)

    if not match:
        raise SystemExit(
            f"Could not find a YYYY-MM-DD date in filename: {file_path}"
        )

    import_report(
        file_path=file_path,
        report_date=match.group(0)
    )


if __name__ == "__main__":
    main()
