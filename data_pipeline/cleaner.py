def clean_d88(df):

    df.columns = df.columns.str.strip()

    df = df.dropna(how="all")

    return df