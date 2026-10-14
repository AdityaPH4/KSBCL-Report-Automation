import subprocess
import sys
import time
from pathlib import Path

from .importer import import_report
from .report_date import resolve_report_date
from .notify import notify

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 15


def run(spec):

    # ---------------------------------------------------------
    # CALCULATE REPORT DATE (the one place this is decided)
    # ---------------------------------------------------------

    report_date = resolve_report_date()
    date_str = report_date.strftime("%d/%m/%Y")

    try:

        # ---------------------------------------------------------
        # RUN CRAWLER, RETRYING ON FAILURE
        # ---------------------------------------------------------

        for attempt in range(1, MAX_ATTEMPTS + 1):

            print(
                f"Running crawler ({spec.crawler_script}), "
                f"attempt {attempt}/{MAX_ATTEMPTS}...\n"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    spec.crawler_script,
                    "--date",
                    report_date.isoformat(),
                ]
            )

            if result.returncode == 0:
                break

            if attempt < MAX_ATTEMPTS:

                print(
                    f"\nAttempt {attempt} failed "
                    f"(exit code {result.returncode}). Retrying..."
                )

                notify(
                    f"⚠️ {spec.key}: attempt {attempt} failed for {date_str} "
                    f"(exit code {result.returncode}) — retrying..."
                )

                time.sleep(RETRY_DELAY_SECONDS)

        # ---------------------------------------------------------
        # CRAWLER FAILED (all attempts exhausted)
        # ---------------------------------------------------------

        if result.returncode != 0:

            print(
                f"\nCrawler did not complete successfully after "
                f"{MAX_ATTEMPTS} attempts."
            )

            print(
                "Skipping import."
            )

            notify(
                f"❌ {spec.key}: crawler failed for {date_str} after "
                f"{MAX_ATTEMPTS} attempts (exit code {result.returncode})."
            )

            raise SystemExit(
                result.returncode
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
                f"Zero data for {date_str}."
            )

            print(
                "No report file was created."
            )

            print(
                f"0 rows added to robinhood.{spec.table_name}."
            )

            notify(
                f"⚠️ {spec.key}: zero data for {date_str}. "
                f"Nothing added to robinhood.{spec.table_name}."
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

        inserted = import_report(
            file_path=str(file_path),
            report_date=report_date.isoformat(),
            spec=spec,
        )

        if inserted is None:

            notify(
                f"⚠️ {spec.key}: {date_str} was already imported. "
                f"No new rows added."
            )

        else:

            notify(
                f"✅ {spec.key}: imported {inserted} rows for {date_str} "
                f"into robinhood.{spec.table_name}."
            )

    except SystemExit:

        raise

    except Exception as e:

        notify(
            f"❌ {spec.key}: run failed for {date_str} — {e}"
        )

        raise
