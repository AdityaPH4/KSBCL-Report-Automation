from pathlib import Path

import pandas as pd

MASTER_PATH = Path(__file__).resolve().parent.parent / "D88_Bottles_Master.xlsx"


def load_master(path=MASTER_PATH):

    if path.exists():
        return pd.read_excel(path)

    return pd.DataFrame()


def already_imported(master_df, import_id):

    if "Import ID" not in master_df.columns:
        return False

    return import_id in master_df["Import ID"].values


def get_next_serial(master_df):

    if master_df.empty or "Serial No." not in master_df.columns:
        return 1

    return int(master_df["Serial No."].max()) + 1


def append_data(master_df, new_df, path=MASTER_PATH):

    combined = pd.concat([master_df, new_df], ignore_index=True)

    if "Serial No." in combined.columns:
        combined["Serial No."] = combined["Serial No."].astype(int)

    combined.to_excel(path, index=False)

    print(f"\nMASTER FILE SAVED TO:")
    print(path.resolve())
    print(f"Total rows now: {len(combined)}")
    print(f"File size: {path.stat().st_size} bytes\n")

    return combined
