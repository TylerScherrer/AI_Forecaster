# backend/services/store_service.py
from typing import List, Dict
from model_utils import get_latest_features_df


def get_store_list() -> List[Dict]:
    """
    Build a list of stores from the latest features DataFrame.

    Returns
    -------
    List[Dict]
        Each dict: {"value": store_id, "label": "1234 - Store Name"}
    """
    df = get_latest_features_df()   # <-- this is a pandas DataFrame

    stores = []
    seen_ids = set()

    # Adjust these column names if yours are slightly different
    STORE_ID_COL = "Store Number"
    STORE_NAME_COL = "Store Name"

    for _, row in df.iterrows():
        store_id = int(row[STORE_ID_COL])

        # skip duplicates (multiple rows per store)
        if store_id in seen_ids:
            continue
        seen_ids.add(store_id)

        store_name = str(row.get(STORE_NAME_COL, "")).strip()
        if store_name:
            label = f"{store_id} - {store_name}"
        else:
            label = str(store_id)

        stores.append({
            "value": store_id,
            "label": label,
        })

    # Optional: sort alphabetically by label
    stores.sort(key=lambda s: s["label"])

    return stores
