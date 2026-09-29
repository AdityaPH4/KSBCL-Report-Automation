import re
import pandas as pd


def normalize_column_name(name):
    """
    Normalize a column name for reliable matching.

    Handles:
    - Capital letters
    - Lowercase letters
    - Spaces
    - Underscores
    - Hyphens
    - Other punctuation
    - Mixed formats

    Examples:

        RANGENAME       -> rangename
        RANGE_NAME      -> rangename
        Range_Name      -> rangename
        range_name      -> rangename
        Range Name      -> rangename
        RANGE NAME      -> rangename
        range-name      -> rangename
        RANGE-NAME      -> rangename

        DEPO_NAME       -> deponame
        DEPO NAME       -> deponame
        Depo Name       -> deponame
        deponame        -> deponame
    """

    if pd.isna(name):
        return ""

    # Convert to string and remove leading/trailing whitespace
    name = str(name).strip()

    # Convert everything to lowercase
    name = name.lower()

    # Remove EVERYTHING except letters and numbers.
    # This removes:
    # spaces
    # underscores _
    # hyphens -
    # slashes /
    # dots .
    # brackets
    # other punctuation
    name = re.sub(r"[^a-z0-9]", "", name)

    return name


def find_header_row(raw_df, column_aliases):
    """
    Searches every row until it finds the actual report header.
    Does NOT assume the header is on a fixed row.
    """

    normalized_aliases = {
        canonical: {
            normalize_column_name(alias)
            for alias in aliases
        }
        for canonical, aliases in column_aliases.items()
    }

    for row_index in range(len(raw_df)):

        row_values = [
            normalize_column_name(value)
            for value in raw_df.iloc[row_index].tolist()
        ]

        # Count how many known columns appear in this row
        matched_columns = 0

        for value in row_values:

            for aliases in normalized_aliases.values():

                if value in aliases:
                    matched_columns += 1
                    break

        # A real header row should contain several known columns
        if matched_columns >= 5:
            return row_index

    raise ValueError(
        "Could not find the report header row. "
        "The Excel format may have changed."
    )


def map_columns(columns, column_aliases):
    """
    Maps whatever column names KSBCL gives us
    to our stable internal column names.
    """

    normalized_aliases = {
        canonical: {
            normalize_column_name(alias)
            for alias in aliases
        }
        for canonical, aliases in column_aliases.items()
    }

    column_mapping = {}

    for original_column in columns:

        normalized = normalize_column_name(original_column)

        if not normalized:
            continue

        for canonical_name, aliases in normalized_aliases.items():

            if normalized in aliases:

                column_mapping[original_column] = canonical_name
                break

    return column_mapping


def parse_report(file_path, spec):

    print(f"Reading report: {file_path}")

    # Read the entire sheet without assuming where the header is
    raw_df = pd.read_excel(
        file_path,
        header=None
    )

    print(f"Loaded {len(raw_df)} rows")

    # Find the real header dynamically
    header_row = find_header_row(raw_df, spec.column_aliases)

    print(f"Found report header at Excel row {header_row + 1}")

    # Everything below the header is data
    headers = raw_df.iloc[header_row].tolist()

    data = raw_df.iloc[header_row + 1:].copy()

    # Assign the detected headers
    data.columns = headers

    # Remove completely empty rows
    data = data.dropna(
        how="all"
    ).reset_index(drop=True)

    # Map KSBCL's column names to ours
    column_mapping = map_columns(data.columns, spec.column_aliases)

    print("\nDetected columns:")

    for original, canonical in column_mapping.items():
        print(f"  {original!r} -> {canonical}")

    # Rename recognized columns
    data = data.rename(
        columns=column_mapping
    )

    # Check required columns
    missing_columns = [
        column
        for column in spec.required_columns
        if column not in data.columns
    ]

    if missing_columns:

        raise ValueError(
            f"\n{spec.key} report is missing required columns:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing_columns
            )
            + "\n\nThe report format may have changed."
        )

    # Keep only columns we understand
    recognized_columns = [
        column
        for column in spec.column_aliases
        if column in data.columns
    ]

    data = data[recognized_columns]

    # Remove rows that contain no useful data
    data = data.dropna(
        how="all"
    ).reset_index(drop=True)

    print(
        f"\nSuccessfully parsed {len(data)} data rows."
    )

    return data
