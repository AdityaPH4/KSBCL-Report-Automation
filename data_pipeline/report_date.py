"""
The one place that decides which date a crawler run is for.

Both daily_runner.py (the orchestrator) and each automate_*.py crawler
(when run standalone, e.g. for a manual backfill) call resolve_report_date()
instead of each computing "yesterday" independently — that duplication is
exactly what caused the crawler and the runner to silently disagree on the
target date.

Resolution order:
  1. --date YYYY-MM-DD on the command line
  2. REPORT_DATE=YYYY-MM-DD in the environment
  3. yesterday (Asia/Kolkata) — the default for normal daily runs
"""

import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

INDIA = ZoneInfo("Asia/Kolkata")


def resolve_report_date(argv=None):

    argv = sys.argv if argv is None else argv

    if "--date" in argv:

        idx = argv.index("--date")

        return datetime.strptime(
            argv[idx + 1],
            "%Y-%m-%d"
        ).date()

    env_value = os.environ.get("REPORT_DATE")

    if env_value:

        return datetime.strptime(
            env_value,
            "%Y-%m-%d"
        ).date()

    return (
        datetime.now(INDIA).date()
        - timedelta(days=1)
    )
