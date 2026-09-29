import re
import pandas as pd


# Our internal, stable column names
COLUMN_ALIASES = {
    "sr_no": [
        "sr no",
        "serial no",
        "serial number",
        "sr number",
    ],
    "depo_name": [
        "depo name",
        "depot name",
    ],
    "supplier_name": [
        "supplier",
        "supplier name",
    ],
    "retailer_name": [
        "retailer",
        "retailer name",
    ],
    "sales_invoice_no": [
        "sales invoice",
        "sales invoice no",
        "sales invoice number",
        "invoice no",
        "invoice number",
    ],
    "vehicle_no": [
        "vehicle no",
        "vehicle number",
        "vehicle",
    ],
    "sales_invoice_date": [
        "sales invoice date",
        "invoice date",
    ],
    "item_name": [
        "item name",
        "item",
    ],
    "slab": [
        "slab",
    ],
    "rangename": [
        "rangename",
        "range name",
    ],
    "supplier_type_name": [
        "supplier type",
        "supplier type name",
    ],
    "brand_name": [
        "brand",
        "brand name",
    ],
    "category_name": [
        "category",
        "category name",
    ],
    "item_qty": [
        "item qty",
        "item quantity",
        "quantity",
        "qty",
    ],
    "sales_cbs": [
        "sales cbs",
        "sales cb",
    ],
    "sales_btls": [
        "sales btls",
        "sales bottles",
        "bottles",
    ],
    "invoice_amount": [
        "invoice amount",
        "amount",
    ],
}


# Columns that must exist for the report to be considered valid
REQUIRED_COLUMNS = [
    "depo_name",
    "supplier_name",
    "retailer_name",
    "sales_invoice_no",
    "item_name",
    "item_qty",
    "invoice_amount",
]


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


def find_header_row(raw_df):
    """
    Searches every row until it finds the actual D88 header.
    Does NOT assume the header is on a fixed row.
    """

    normalized_aliases = {
        canonical: {
            normalize_column_name(alias)
            for alias in aliases
        }
        for canonical, aliases in COLUMN_ALIASES.items()
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

        # A real D88 header should contain several known columns
        if matched_columns >= 5:
            return row_index

    raise ValueError(
        "Could not find the D88 header row. "
        "The Excel format may have changed."
    )


def map_columns(columns):
    """
    Maps whatever column names KSBCL gives us
    to our stable internal column names.
    """

    normalized_aliases = {
        canonical: {
            normalize_column_name(alias)
            for alias in aliases
        }
        for canonical, aliases in COLUMN_ALIASES.items()
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


def parse_d88(file_path):

    print(f"Reading report: {file_path}")

    # Read the entire sheet without assuming where the header is
    raw_df = pd.read_excel(
        file_path,
        header=None
    )

    print(f"Loaded {len(raw_df)} rows")

    # Find the real header dynamically
    header_row = find_header_row(raw_df)

    print(f"Found D88 header at Excel row {header_row + 1}")

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
    column_mapping = map_columns(data.columns)

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
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:

        raise ValueError(
            "\nD88 report is missing required columns:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing_columns
            )
            + "\n\nThe report format may have changed."
        )

    # Keep only columns we understand
    recognized_columns = [
        column
        for column in COLUMN_ALIASES
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