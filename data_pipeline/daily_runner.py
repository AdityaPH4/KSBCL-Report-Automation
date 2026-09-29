import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .importer import import_report

INDIA = ZoneInfo("Asia/Kolkata")


def run(spec):

    print(f"Running crawler ({spec.crawler_script})...\n")

    result = subprocess.run(
        [sys.executable, spec.crawler_script]
    )

    # ---------------------------------------------------------
    # CRAWLER FAILED
    # ---------------------------------------------------------

    if result.returncode != 0:

        print(
            "\nCrawler did not complete successfully."
        )

        print(
            "Skipping import."
        )

        raise SystemExit(
            result.returncode
        )

    # ---------------------------------------------------------
    # CALCULATE REPORT DATE
    # ---------------------------------------------------------

    report_date = (
        datetime.now(INDIA).date()
        - timedelta(days=1)
    )

    file_path = Path(
        f"{spec.filename_prefix}_{report_date.isoformat()}.xlsx"
    )

    # ---------------------------------------------------------
    # ZERO-DATA DAY
    # ---------------------------------------------------------

    # The crawler exits successfully but creates no file
    # when KSBCL reports zero data.

    if not file_path.exists():

        print()
        print(
            f"Zero data for {report_date.strftime('%d/%m/%Y')}."
        )

        print(
            "No report file was created."
        )

        print(
            f"0 rows added to robinhood.{spec.table_name}."
        )

        return

    # ---------------------------------------------------------
    # REPORT EXISTS
    # ---------------------------------------------------------

    print(
        f"\nReport downloaded: {file_path}"
    )

    print(
        f"Appending data to robinhood.{spec.table_name}...\n"
    )

    import_report(
        file_path=str(file_path),
        report_date=report_date.isoformat(),
        spec=spec,
    )
