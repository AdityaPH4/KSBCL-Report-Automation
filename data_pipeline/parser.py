import pandas as pd

def parse_d88(file_path):
    df = pd.read_excel(file_path)

    return df