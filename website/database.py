from sqlalchemy import create_engine
import pandas as pd

# ==========================================
# PostgreSQL Configuration
# ==========================================

USERNAME = "postgres"
PASSWORD = "vnvb12345"
HOST = "localhost"
PORT = "5432"
DATABASE = "AgricultureDW"

engine = create_engine(
    f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

def get_weather_details(crop, state, season, year):

    query = f"""
    SELECT
        annual_rainfall,
        fertilizer,
        pesticide
    FROM staging_crop_yield
    WHERE crop_name = '{crop}'
      AND state = '{state}'
      AND season_name = '{season}'
    ORDER BY ABS(crop_year - {year})
    LIMIT 1
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return None

    return {
        "rainfall": float(df.iloc[0]["annual_rainfall"]),
        "fertilizer": float(df.iloc[0]["fertilizer"]),
        "pesticide": float(df.iloc[0]["pesticide"])
    }