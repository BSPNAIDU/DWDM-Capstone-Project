import os
import joblib
import numpy as np

# =====================================================
# Project Paths
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

MODEL_DIR = os.path.join(PROJECT_DIR, "ml_model")

# =====================================================
# Load Model
# =====================================================

model = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
encoders = joblib.load(os.path.join(MODEL_DIR, "label_encoders.pkl"))

# =====================================================
# Prediction Function
# =====================================================

def predict_crop_yield(
    crop,
    state,
    season,
    year,
    area,
    rainfall,
    fertilizer,
    pesticide
):

    crop_encoded = encoders["crop_name"].transform([crop])[0]
    season_encoded = encoders["season_name"].transform([season])[0]
    state_encoded = encoders["state"].transform([state])[0]

    features = np.array([[
        crop_encoded,
        year,
        season_encoded,
        state_encoded,
        area,
        rainfall,
        fertilizer,
        pesticide
    ]])

    predicted_yield = float(model.predict(features)[0])

    estimated_production = predicted_yield * area

    confidence = 97.95

    return {

        "yield": round(predicted_yield, 2),

        "production": round(estimated_production, 2),

        "confidence": confidence

    }