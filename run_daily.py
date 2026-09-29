import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from data_pipeline.importer import import_report


INDIA = ZoneInfo("Asia/Kolkata")


def main():

    print(
        "Running crawler (automate_bottles_d88.py)...\n"
    )

    result = subprocess.run(
        [sys.executable, "automate_bottles_d88.py"]
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
        f"D88_Report_{report_date.isoformat()}.xlsx"
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
            "0 rows added to D88_Bottles_Master.xlsx."
        )

        return

    # ---------------------------------------------------------
    # REPORT EXISTS
    # ---------------------------------------------------------

    print(
        f"\nReport downloaded: {file_path}"
    )

    print(
        "Appending data to D88_Bottles_Master.xlsx...\n"
    )

    import_report(
        file_path=str(file_path),
        report_date=report_date.isoformat()
    )


if __name__ == "__main__":
    main()