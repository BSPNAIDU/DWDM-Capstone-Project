import os
import json
import csv
import numpy as np
import tensorflow as tf
from PIL import Image


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "disease_model",
    "plant_disease_model.keras"
)

CLASS_NAMES_PATH = os.path.join(
    BASE_DIR,
    "disease_model",
    "class_names.json"
)

DISEASE_INFO_PATH = os.path.join(
    BASE_DIR,
    "disease_data",
    "disease_information.csv"
)


# ============================================================
# GLOBAL VARIABLES
# ============================================================

model = None
class_names = []
disease_information = {}


# ============================================================
# LOAD MODEL
# ============================================================

def load_disease_model():

    global model

    if model is None:

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Disease model not found:\n{MODEL_PATH}"
            )

        print("Loading disease model...")

        model = tf.keras.models.load_model(MODEL_PATH)

        print("Disease model loaded successfully.")

    return model


# ============================================================
# LOAD CLASS NAMES
# ============================================================

def load_class_names():

    global class_names

    if not class_names:

        if not os.path.exists(CLASS_NAMES_PATH):
            raise FileNotFoundError(
                f"Class names file not found:\n{CLASS_NAMES_PATH}"
            )

        with open(
            CLASS_NAMES_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            class_names = json.load(file)

    return class_names


# ============================================================
# LOAD DISEASE INFORMATION
# ============================================================

def load_disease_information():

    global disease_information

    if not disease_information:

        if not os.path.exists(DISEASE_INFO_PATH):
            raise FileNotFoundError(
                f"Disease information file not found:\n"
                f"{DISEASE_INFO_PATH}"
            )

        with open(
            DISEASE_INFO_PATH,
            "r",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                disease_name = row["Disease"].strip()

                disease_information[disease_name] = {
                    "Disease": disease_name,
                    "Crop": row.get("Crop", ""),
                    "Sensitivity": row.get("Sensitivity", ""),
                    "Symptoms": row.get("Symptoms", ""),
                    "Treatment": row.get("Treatment", ""),
                    "Pesticide": row.get("Pesticide", ""),
                    "Prevention": row.get("Prevention", ""),
                    "Recommendation": row.get(
                        "Recommendation",
                        ""
                    )
                }

    return disease_information


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image_path):

    if not os.path.exists(image_path):

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = Image.open(image_path)

    # Convert image to RGB
    image = image.convert("RGB")

    # Resize to model input size
    image = image.resize((224, 224))

    # Convert to numpy
    image_array = np.array(image)

    # Normalize
    image_array = image_array.astype("float32") / 255.0

    # Add batch dimension
    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    return image_array


# ============================================================
# DISEASE PREDICTION
# ============================================================

def predict_disease(image_path):

    # Load model
    disease_model = load_disease_model()

    # Load classes
    classes = load_class_names()

    # Load information
    information = load_disease_information()

    # Prepare image
    image = preprocess_image(image_path)

    # Prediction
    predictions = disease_model.predict(
        image,
        verbose=0
    )

    # Get highest probability
    predicted_index = int(
        np.argmax(predictions[0])
    )

    confidence = float(
        predictions[0][predicted_index]
    ) * 100

    # Safety check
    if predicted_index >= len(classes):

        raise ValueError(
            "Model prediction index does not match "
            "class names."
        )

    predicted_disease = classes[predicted_index]

    # Get disease details
    details = information.get(
        predicted_disease,
        {}
    )

    # If no CSV entry exists
    if not details:

        details = {
            "Disease": predicted_disease,
            "Crop": predicted_disease.split("_")[0],
            "Sensitivity": "Unknown",
            "Symptoms": "Disease information not available.",
            "Treatment": "Consult a qualified agricultural expert.",
            "Pesticide": "Use only locally approved products according to the label.",
            "Prevention": "Maintain crop sanitation and regular monitoring.",
            "Recommendation": "Monitor the crop closely and seek expert confirmation."
        }

    # Return complete result
    result = {

        "disease": details.get(
            "Disease",
            predicted_disease
        ),

        "crop": details.get(
            "Crop",
            ""
        ),

        "confidence": round(
            confidence,
            2
        ),

        "sensitivity": details.get(
            "Sensitivity",
            ""
        ),

        "symptoms": details.get(
            "Symptoms",
            ""
        ),

        "treatment": details.get(
            "Treatment",
            ""
        ),

        "pesticide": details.get(
            "Pesticide",
            ""
        ),

        "prevention": details.get(
            "Prevention",
            ""
        ),

        "recommendation": details.get(
            "Recommendation",
            ""
        )
    }

    return result


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AGRI AI - DISEASE DETECTOR TEST")
    print("=" * 70)

    load_disease_model()
    load_class_names()
    load_disease_information()

    print(
        f"Classes loaded: {len(class_names)}"
    )

    image_path = input(
        "Enter the full path of a leaf image: "
    ).strip().strip('"')

    try:

        result = predict_disease(image_path)

        print()
        print("=" * 70)
        print("DISEASE DETECTION RESULT")
        print("=" * 70)

        print(
            f"Disease: {result['disease']}"
        )

        print(
            f"Crop: {result['crop']}"
        )

        print(
            f"Confidence: {result['confidence']}%"
        )

        print(
            f"Sensitivity: {result['sensitivity']}"
        )

        print()
        print("Symptoms:")
        print(result["symptoms"])

        print()
        print("Treatment:")
        print(result["treatment"])

        print()
        print("Pesticide:")
        print(result["pesticide"])

        print()
        print("Prevention:")
        print(result["prevention"])

        print()
        print("Recommendation:")
        print(result["recommendation"])

        print("=" * 70)

    except Exception as error:

        print()
        print("Prediction Error:")
        print(str(error))