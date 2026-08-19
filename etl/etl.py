import pandas as pd
from sqlalchemy import create_engine

# ===============================
# PostgreSQL Connection
# ===============================

USERNAME = "postgres"
PASSWORD = "vnvb12345"
HOST = "localhost"
PORT = "5432"
DATABASE = "AgricultureDW"

engine = create_engine(
    f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

# ===============================
# Load Dataset
# ===============================

print("Loading Dataset...")

df = pd.read_csv("dataset/crop_yield.csv")

print(df.head())

print("\nRows :", len(df))
print("Columns :", len(df.columns))

# ===============================
# Rename Columns
# ===============================

df.columns = [
    "crop_name",
    "crop_year",
    "season_name",
    "state",
    "area",
    "production",
    "annual_rainfall",
    "fertilizer",
    "pesticide",
    "yield"
]

# ===============================
# Remove Missing Values
# ===============================

df = df.dropna()

# ===============================
# Remove Duplicate Records
# ===============================

df = df.drop_duplicates()

print("\nCleaned Dataset")

print(df.head())

print("\nSaving into PostgreSQL...")

# ===============================
# Load into Staging Table
# ===============================

df.to_sql(
    "staging_crop_yield",
    engine,
    if_exists="replace",
    index=False
)

print("Done.")

print("ETL Completed Successfully")