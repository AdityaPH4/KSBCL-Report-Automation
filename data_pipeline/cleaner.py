import pandas as pd

# Columns that hold dates but arrive in inconsistent formats
# (DD/MM/YYYY, D-M-YYYY, YYYY-MM-DD, etc. depending on the report run).
DATE_COLUMNS = ["sales_invoice_date"]

STANDARD_DATE_FORMAT = "%Y-%m-%d"


def clean_d88(df):

    df.columns = df.columns.str.strip()

    df = df.dropna(how="all")

    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col], dayfirst=True, errors="coerce"
            ).dt.strftime(STANDARD_DATE_FORMAT)

    return df
