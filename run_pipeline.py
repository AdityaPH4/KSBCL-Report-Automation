import re
import sys
from pathlib import Path

from data_pipeline.importer import import_report
from data_pipeline.specs import ALL_SPECS

DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")

DEFAULT_FILE = "D88_Report_2026-09-24.xlsx"


def find_spec(file_path):
    name = Path(file_path).name

    for spec in ALL_SPECS:
        if name.startswith(f"{spec.filename_prefix}_"):
            return spec

    raise SystemExit(
        f"Could not tell which report type {file_path!r} is "
        "(no known filename prefix matched)."
    )


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE

    match = DATE_PATTERN.search(Path(file_path).stem)

    if not match:
        raise SystemExit(
            f"Could not find a YYYY-MM-DD date in filename: {file_path}"
        )

    spec = find_spec(file_path)

    import_report(
        file_path=file_path,
        report_date=match.group(0),
        spec=spec,
    )


if __name__ == "__main__":
    main()
