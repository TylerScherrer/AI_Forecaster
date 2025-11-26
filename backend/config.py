# config.py
import os

# Base directories
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

# Data paths
IOWA_CSV_PATH = os.path.join(DATA_DIR, "Iowa_Liquor_Sales.csv")

# CORS – allow both deployed SWA and local dev
CORS_ALLOWED_ORIGINS = [
    "https://ambitious-dune-04477dd10.3.azurestaticapps.net",  # your Static Web App
    "http://localhost:5173",                                   # Vite dev
    "http://127.0.0.1:5173",                                   # alt localhost
]
