import os
import pandas as pd

# Path to your CSV
LOOKUP_PATH = os.path.join(
    os.path.dirname(__file__), "data", "store_lookup.csv"
)

# Load CSV with NO HEADER
df_lookup = pd.read_csv(LOOKUP_PATH, header=None, names=["Store_Number", "Store_Name"])

# Build lookup dictionary
STORE_NAME_MAP = {
    int(row["Store_Number"]): str(row["Store_Name"]).strip()
    for _, row in df_lookup.iterrows()
}

def get_store_name(store_id: int) -> str:
    """Return the store name for a given store ID."""
    return STORE_NAME_MAP.get(int(store_id), "")
