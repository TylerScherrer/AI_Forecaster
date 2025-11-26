# backend/services/store_service.py
from model_utils import get_latest_features_df
from store_lookup import get_store_name

def get_store_list():
    df = get_latest_features_df()

    stores = []
    seen = set()

    for _, row in df.iterrows():
        store_id = int(row["Store Number"])  # this column EXISTS in your features file

        if store_id in seen:
            continue
        seen.add(store_id)

        store_name = get_store_name(store_id)
        label = f"{store_id} - {store_name}" if store_name else str(store_id)

        stores.append({"value": store_id, "label": label})

    stores.sort(key=lambda s: s["value"])
    return stores
