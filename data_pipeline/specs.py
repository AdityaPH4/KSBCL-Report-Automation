"""
One ReportSpec per KSBCL automation. Everything that differs between
feeds (crawler script, output filename, report columns, DB table) lives
here; the parsing/cleaning/import/db engine in the rest of data_pipeline
is generic and driven entirely by these specs.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReportSpec:
    key: str  # internal identifier, e.g. "d88_bottles"
    crawler_script: str  # e.g. "automate_bottles_d88.py"
    filename_prefix: str  # report file is "{filename_prefix}_{date}.xlsx"
    import_id_prefix: str  # import_id is "{import_id_prefix}-{date}"
    table_name: str  # robinhood.{table_name}
    column_aliases: dict
    required_columns: list
    date_columns: list  # columns needing dayfirst date parsing during cleaning
    column_types: dict  # report column -> Postgres type, for DDL


# ---------------------------------------------------------------------
# D88 — per-invoice sales reports (Bottles + Cider share this shape)
# ---------------------------------------------------------------------

D88_COLUMN_ALIASES = {
    "sr_no": ["sr no", "serial no", "serial number", "sr number"],
    "depo_name": ["depo name", "depot name"],
    "supplier_name": ["supplier", "supplier name"],
    "retailer_name": ["retailer", "retailer name"],
    "sales_invoice_no": [
        "sales invoice",
        "sales invoice no",
        "sales invoice number",
        "invoice no",
        "invoice number",
    ],
    "vehicle_no": ["vehicle no", "vehicle number", "vehicle"],
    "sales_invoice_date": ["sales invoice date", "invoice date"],
    "item_name": ["item name", "item"],
    "slab": ["slab"],
    "rangename": ["rangename", "range name"],
    "supplier_type_name": ["supplier type", "supplier type name"],
    "brand_name": ["brand", "brand name"],
    "category_name": ["category", "category name"],
    "item_qty": ["item qty", "item quantity", "quantity", "qty"],
    "sales_cbs": ["sales cbs", "sales cb"],
    "sales_btls": ["sales btls", "sales bottles", "bottles"],
    "invoice_amount": ["invoice amount", "amount"],
}

D88_REQUIRED_COLUMNS = [
    "depo_name",
    "supplier_name",
    "retailer_name",
    "sales_invoice_no",
    "item_name",
    "item_qty",
    "invoice_amount",
]

D88_DATE_COLUMNS = ["sales_invoice_date"]

D88_COLUMN_TYPES = {
    "sr_no": "TEXT",
    "depo_name": "TEXT",
    "supplier_name": "TEXT",
    "retailer_name": "TEXT",
    "sales_invoice_no": "TEXT",
    "vehicle_no": "TEXT",
    "sales_invoice_date": "DATE",
    "item_name": "TEXT",
    "slab": "TEXT",
    "rangename": "TEXT",
    "supplier_type_name": "TEXT",
    "brand_name": "TEXT",
    "category_name": "TEXT",
    "item_qty": "NUMERIC",
    "sales_cbs": "NUMERIC",
    "sales_btls": "NUMERIC",
    "invoice_amount": "NUMERIC",
}


D88_BOTTLES = ReportSpec(
    key="d88_bottles",
    crawler_script="automate_bottles_d88.py",
    filename_prefix="D88_Report",
    import_id_prefix="D88",
    table_name="d88_bottles_sales",
    column_aliases=D88_COLUMN_ALIASES,
    required_columns=D88_REQUIRED_COLUMNS,
    date_columns=D88_DATE_COLUMNS,
    column_types=D88_COLUMN_TYPES,
)

D88_CIDER = ReportSpec(
    key="d88_cider",
    crawler_script="automate_cider_d88.py",
    filename_prefix="D88_Cider_Report",
    import_id_prefix="D88-CIDER",
    table_name="d88_cider_sales",
    column_aliases=D88_COLUMN_ALIASES,
    required_columns=D88_REQUIRED_COLUMNS,
    date_columns=D88_DATE_COLUMNS,
    column_types=D88_COLUMN_TYPES,
)


# ---------------------------------------------------------------------
# D94 — per-depot closing stock reports (Bottles + Cider share this shape)
# ---------------------------------------------------------------------

D94_COLUMN_ALIASES = {
    "sr_no": ["sr no", "serial no", "serial number", "sr number"],
    "depot_id": ["depot id", "depo id", "depot code"],
    "depot_name": ["depot name", "depo name"],
    "item_name": ["item name", "item"],
    "item_code": ["item code", "item cd"],
    "brand_name": ["brand", "brand name"],
    "item_size": ["item size", "size"],
    "item_qty": ["item qty", "item quantity", "quantity", "qty"],
    "landed_cost": ["landed cost"],
    "item_price": ["item price", "price"],
    "slab": ["slab"],
    "close_cbs": ["close cbs", "closing cbs"],
    "close_btls": ["close btls", "closing btls", "closing bottles"],
    "total_btls": ["total btls", "total bottles"],
    "total_cbs": ["total cbs"],
}

D94_REQUIRED_COLUMNS = [
    "depot_id",
    "depot_name",
    "item_name",
    "item_qty",
    "close_cbs",
    "close_btls",
]

D94_DATE_COLUMNS = []

D94_COLUMN_TYPES = {
    "sr_no": "TEXT",
    "depot_id": "TEXT",
    "depot_name": "TEXT",
    "item_name": "TEXT",
    "item_code": "TEXT",
    "brand_name": "TEXT",
    "item_size": "NUMERIC",
    "item_qty": "NUMERIC",
    "landed_cost": "NUMERIC",
    "item_price": "NUMERIC",
    "slab": "TEXT",
    "close_cbs": "NUMERIC",
    "close_btls": "NUMERIC",
    "total_btls": "NUMERIC",
    "total_cbs": "NUMERIC",
}


D94_BOTTLES = ReportSpec(
    key="d94_bottles",
    crawler_script="automate_bottles_d94.py",
    filename_prefix="D94_Bottles_Report",
    import_id_prefix="D94-BOTTLES",
    table_name="d94_bottles_stock",
    column_aliases=D94_COLUMN_ALIASES,
    required_columns=D94_REQUIRED_COLUMNS,
    date_columns=D94_DATE_COLUMNS,
    column_types=D94_COLUMN_TYPES,
)

D94_CIDER = ReportSpec(
    key="d94_cider",
    crawler_script="automate_cider_d94.py",
    filename_prefix="D94_Cider_Report",
    import_id_prefix="D94-CIDER",
    table_name="d94_cider_stock",
    column_aliases=D94_COLUMN_ALIASES,
    required_columns=D94_REQUIRED_COLUMNS,
    date_columns=D94_DATE_COLUMNS,
    column_types=D94_COLUMN_TYPES,
)

ALL_SPECS = [D88_BOTTLES, D88_CIDER, D94_BOTTLES, D94_CIDER]
