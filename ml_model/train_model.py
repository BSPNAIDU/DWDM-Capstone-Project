import pandas as pd
import joblib

from sqlalchemy import create_engine

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ==========================================
# PostgreSQL Connection
# ==========================================

USERNAME = "postgres"
PASSWORD = "vnvb12345"
HOST = "localhost"
PORT = "5432"
DATABASE = "AgricultureDW"

engine = create_engine(
    f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

print("Connected to PostgreSQL")

# ==========================================
# Read Data
# ==========================================

query = "SELECT * FROM staging_crop_yield"

df = pd.read_sql(query, engine)

print("\nDataset Loaded Successfully")
print(df.head())

# ==========================================
# Encode Categorical Columns
# ==========================================

encoders = {}

categorical_columns = [
    "crop_name",
    "season_name",
    "state"
]

for column in categorical_columns:

    encoder = LabelEncoder()

    df[column] = encoder.fit_transform(df[column])

    encoders[column] = encoder

# ==========================================
# Features and Target
# ==========================================

X = df[
    [
        "crop_name",
        "crop_year",
        "season_name",
        "state",
        "area",
        "annual_rainfall",
        "fertilizer",
        "pesticide"
    ]
]

y = df["yield"]

# ==========================================
# Train/Test Split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ==========================================
# Train Random Forest Model
# ==========================================

print("\nTraining Model...")

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

print("Training Completed")

# ==========================================
# Predictions
# ==========================================

predictions = model.predict(X_test)

# ==========================================
# Evaluation
# ==========================================

mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5
r2 = r2_score(y_test, predictions)

print("\nModel Evaluation")
print("---------------------------")
print("MAE :", round(mae,4))
print("RMSE:", round(rmse,4))
print("R2  :", round(r2,4))

# ==========================================
# Save Model
# ==========================================

joblib.dump(model, "ml_model/model.pkl")
joblib.dump(encoders, "ml_model/label_encoders.pkl")

print("\nModel Saved Successfully")