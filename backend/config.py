# config.py
import os

# Base directories
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

# Data paths
IOWA_CSV_PATH = os.path.join(DATA_DIR, "Iowa_Liquor_Sales.csv")

# CORS
CORS_ALLOW_ORIGIN = "https://ambitious-dune-04477dd10.3.azurestaticapps.net"
