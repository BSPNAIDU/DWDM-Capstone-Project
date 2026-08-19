import os
import json
import numpy as np
import tensorflow as tf
from PIL import Image


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

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

IMAGE_SIZE = (224, 224)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading disease detection model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)


# ============================================================
# LOAD CLASS NAMES
# ============================================================

with open(
    CLASS_NAMES_PATH,
    "r",
    encoding="utf-8"
) as file:

    class_names = json.load(file)


print("Model loaded successfully.")

print(
    "Number of classes:",
    len(class_names)
)


# ============================================================
# PREDICT DISEASE
# ============================================================

def predict_disease(image_path):

    # --------------------------------------------------------
    # Check image
    # --------------------------------------------------------

    if not os.path.exists(image_path):

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    # --------------------------------------------------------
    # Open image
    # --------------------------------------------------------

    image = Image.open(
        image_path
    ).convert("RGB")


    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    image = image.resize(
        IMAGE_SIZE
    )


    # --------------------------------------------------------
    # Convert to NumPy
    # --------------------------------------------------------

    image_array = np.array(
        image,
        dtype=np.float32
    )


    # --------------------------------------------------------
    # Add batch dimension
    # --------------------------------------------------------

    image_array = np.expand_dims(
        image_array,
        axis=0
    )


    # --------------------------------------------------------
    # IMPORTANT:
    # MobileNetV2 preprocessing
    # --------------------------------------------------------

    image_array = (
        image_array / 127.5
    ) - 1.0


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    predictions = model.predict(
        image_array,
        verbose=0
    )


    # --------------------------------------------------------
    # Get highest probability
    # --------------------------------------------------------

    predicted_index = np.argmax(
        predictions[0]
    )

    confidence = float(
        predictions[0][predicted_index]
    )


    disease = class_names[
        predicted_index
    ]


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "disease": disease,

        "confidence": round(
            confidence * 100,
            2
        )

    }


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("DISEASE DETECTOR TEST")
    print("=" * 60)

    image_path = input(
        "Enter the full path of a leaf image: "
    ).strip().strip('"')


    try:

        result = predict_disease(
            image_path
        )


        print()
        print("=" * 60)
        print("PREDICTION RESULT")
        print("=" * 60)

        print(
            "Disease:",
            result["disease"]
        )

        print(
            "Confidence:",
            str(result["confidence"]) + "%"
        )

        print("=" * 60)


    except Exception as error:

        print()
        print("Prediction Error:")
        print(error)