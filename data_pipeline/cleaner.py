import pandas as pd

STANDARD_DATE_FORMAT = "%Y-%m-%d"


def clean_report(df, spec):

    df.columns = df.columns.str.strip()

    df = df.dropna(how="all")

    # Columns that hold dates but arrive in inconsistent formats
    # (DD/MM/YYYY, D-M-YYYY, YYYY-MM-DD, etc. depending on the report run).
    for col in spec.date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col], dayfirst=True, errors="coerce"
            ).dt.strftime(STANDARD_DATE_FORMAT)

    return df
