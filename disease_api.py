import os
import json
import csv
import numpy as np
from PIL import Image

# LiteRT runtime
try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    # Compatibility fallback for environments where the interpreter
    # is exposed directly by the package.
    from ai_edge_litert import Interpreter


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "disease_model",
    "plant_disease_model.tflite"
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

interpreter = None
input_details = None
output_details = None

class_names = []
disease_information = {}


# ============================================================
# LOAD TFLITE MODEL
# ============================================================

def load_disease_model():

    global interpreter
    global input_details
    global output_details

    if interpreter is None:

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Disease TFLite model not found:\n{MODEL_PATH}"
            )

        print("Loading disease TFLite model...")

        interpreter = Interpreter(model_path=MODEL_PATH)

        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        print("Disease TFLite model loaded successfully.")

        print(
            "Model input shape:",
            input_details[0]["shape"]
        )

        print(
            "Model output shape:",
            output_details[0]["shape"]
        )

    return interpreter


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

    image = image.convert("RGB")

    image = image.resize((224, 224))

    image_array = np.array(image)

    image_array = image_array.astype("float32") / 255.0

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    return image_array


# ============================================================
# DISEASE PREDICTION
# ============================================================

def predict_disease(image_path):

    global interpreter
    global input_details
    global output_details

    # Load model
    disease_model = load_disease_model()

    # Load classes
    classes = load_class_names()

    # Load disease information
    information = load_disease_information()

    # Prepare image
    image = preprocess_image(image_path)

    # --------------------------------------------------------
    # Handle model input datatype
    # --------------------------------------------------------

    input_info = input_details[0]

    input_dtype = input_info["dtype"]

    if input_dtype == np.float32:

        input_data = image.astype(np.float32)

    elif input_dtype == np.uint8:

        input_data = (image * 255).astype(np.uint8)

    elif input_dtype == np.int8:

        scale, zero_point = input_info["quantization"]

        if scale == 0:
            raise ValueError(
                "Invalid quantization scale in disease model."
            )

        input_data = (
            image / scale + zero_point
        ).astype(np.int8)

    else:

        raise TypeError(
            f"Unsupported model input type: {input_dtype}"
        )

    # --------------------------------------------------------
    # Run inference
    # --------------------------------------------------------

    disease_model.set_tensor(
        input_info["index"],
        input_data
    )

    disease_model.invoke()

    predictions = disease_model.get_tensor(
        output_details[0]["index"]
    )

    # --------------------------------------------------------
    # Handle quantized output if required
    # --------------------------------------------------------

    output_info = output_details[0]

    if output_info["dtype"] in (
        np.uint8,
        np.int8
    ):

        scale, zero_point = output_info["quantization"]

        if scale != 0:

            predictions = (
                predictions.astype(np.float32)
                - zero_point
            ) * scale

    predictions = np.asarray(
        predictions,
        dtype=np.float32
    )

    # Remove batch dimension
    predictions = predictions[0]

    # Get highest probability
    predicted_index = int(
        np.argmax(predictions)
    )

    confidence = float(
        predictions[predicted_index]
    ) * 100

    # Safety check
    if predicted_index >= len(classes):

        raise ValueError(
            "Model prediction index does not match "
            "class names."
        )

    predicted_disease = classes[predicted_index]

    # --------------------------------------------------------
    # Get disease details
    # --------------------------------------------------------

    details = information.get(
        predicted_disease,
        {}
    )

    # Fallback if CSV entry doesn't exist
    if not details:

        details = {
            "Disease": predicted_disease,
            "Crop": predicted_disease.split("_")[0],
            "Sensitivity": "Unknown",
            "Symptoms": (
                "Disease information not available."
            ),
            "Treatment": (
                "Consult a qualified agricultural expert."
            ),
            "Pesticide": (
                "Use only locally approved products "
                "according to the label."
            ),
            "Prevention": (
                "Maintain crop sanitation and "
                "regular monitoring."
            ),
            "Recommendation": (
                "Monitor the crop closely and seek "
                "expert confirmation."
            )
        }

    # --------------------------------------------------------
    # Return complete result
    # --------------------------------------------------------

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
    print("AGRI AI - TFLITE DISEASE DETECTOR TEST")
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