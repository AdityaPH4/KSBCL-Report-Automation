from data_pipeline.importer import import_report

file_path = "downloaded_files/D88_Report_2026-09-24.xlsx"

import_report(
    file_path=file_path,
    report_date="2026-09-24"
)