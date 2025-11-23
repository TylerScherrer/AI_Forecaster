# services/store_service.py
from typing import Optional
import pandas as pd

from model_utils import get_store_list_from_features

_store_list_cache: Optional[pd.DataFrame] = None


def get_store_list() -> pd.DataFrame:
    """
    Return store list as a DataFrame, cached in memory.
    """
    global _store_list_cache
    if _store_list_cache is not None:
        return _store_list_cache

    df = get_store_list_from_features()
    _store_list_cache = df
    return _store_list_cache
