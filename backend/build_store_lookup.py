import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

BIG_CSV = os.path.join(DATA_DIR, "Iowa_Liquor_Sales.csv")
LOOKUP_CSV = os.path.join(DATA_DIR, "store_lookup.csv")

def main():
    print("Reading big CSV once to build store lookup...")
    df = pd.read_csv(
        BIG_CSV,
        usecols=["Store Number", "Store Name"],
    ).dropna()

    # unique store id → name
    df = (
        df.drop_duplicates(subset="Store Number")
          .rename(columns={
              "Store Number": "store_id",
              "Store Name": "store_name",
          })
          .sort_values("store_name")
          .reset_index(drop=True)
    )

    df.to_csv(LOOKUP_CSV, index=False)
    print(f"Wrote {LOOKUP_CSV} with {len(df)} stores")

if __name__ == "__main__":
    main()
