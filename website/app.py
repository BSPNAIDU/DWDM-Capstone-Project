from flask import Flask, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from pathlib import Path
import pandas as pd
import os
import sys
import uuid


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

# Production-safe settings for Render.
# Render sits behind a reverse proxy, so preserve the original
# request scheme/host information.
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1,
    x_prefix=1
)

# Maximum size for uploaded leaf images.
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Make project root importable.
# This fixes:
# ModuleNotFoundError: No module named 'disease_api'
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


# =========================================================
# EXISTING PROJECT MODULES
# =========================================================

try:
   from website.database import get_weather_details
except Exception as error:
    print("WARNING: database.py could not be imported.")
    print("Database import error:", error)

    def get_weather_details(crop, state, season, year):
        return None


try:
    from website.predictor import predict_crop_yield
except Exception as error:
    print("WARNING: predictor.py could not be imported.")
    print("Predictor import error:", error)

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
        return {
            "yield": 0,
            "production": 0,
            "confidence": 0
        }


# =========================================================
# FILE FINDER
# =========================================================

def find_file(filename):

    possible_paths = [
        PROJECT_DIR / "dataset" / filename,
        BASE_DIR / "dataset" / filename,
        PROJECT_DIR / filename,
        BASE_DIR / filename
    ]

    for path in possible_paths:

        if path.exists():
            return str(path)

    return str(possible_paths[0])


# =========================================================
# DATASET PATHS
# =========================================================

DATASET_PATH = find_file("crop_yield.csv")

WATER_DATASET_PATH = find_file(
    "water_usage_optimizer_large_dataset.csv"
)


# =========================================================
# LOAD MAIN AGRICULTURE DATASET
# =========================================================

if not os.path.exists(DATASET_PATH):

    raise FileNotFoundError(
        "\n\nCrop dataset not found.\n\n"
        f"Expected file:\n{DATASET_PATH}\n\n"
        "Please make sure crop_yield.csv exists."
    )


df = pd.read_csv(DATASET_PATH)


print("=" * 70)
print("AgriAI AGRICULTURE DATASET")
print("=" * 70)
print("Dataset:", DATASET_PATH)
print("Rows:", len(df))
print("Columns:", list(df.columns))
print("=" * 70)


# =========================================================
# REQUIRED CROP DATASET COLUMNS
# =========================================================

required_columns = [

    "Crop",
    "Crop_Year",
    "Season",
    "State",
    "Area",
    "Production",
    "Annual_Rainfall",
    "Fertilizer",
    "Pesticide",
    "Yield"

]


for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Required column '{column}' "
            "is missing from crop_yield.csv"
        )


# =========================================================
# CLEAN MAIN DATASET
# =========================================================

numeric_columns = [

    "Crop_Year",
    "Area",
    "Production",
    "Annual_Rainfall",
    "Fertilizer",
    "Pesticide",
    "Yield"

]


for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


df["Crop"] = (
    df["Crop"]
    .fillna("Unknown")
    .astype(str)
)


df["State"] = (
    df["State"]
    .fillna("Unknown")
    .astype(str)
)


df["Season"] = (
    df["Season"]
    .fillna("Unknown")
    .astype(str)
)


# =========================================================
# LOAD WATER USAGE DATASET
# =========================================================

water_df = pd.DataFrame()


if os.path.exists(WATER_DATASET_PATH):

    try:

        water_df = pd.read_csv(
            WATER_DATASET_PATH
        )

        print("=" * 70)
        print("WATER USAGE DATASET")
        print("=" * 70)
        print("Dataset:", WATER_DATASET_PATH)
        print("Rows:", len(water_df))
        print("Columns:", list(water_df.columns))
        print("=" * 70)

    except Exception as error:

        print(
            "WARNING: Unable to read water dataset:",
            error
        )

else:

    print("=" * 70)
    print("WARNING: WATER DATASET NOT FOUND")
    print("=" * 70)


# =========================================================
# CLEAN WATER DATA
# =========================================================

water_numeric_columns = [

    "Crop_Water_Requirement_mm",
    "Rainfall_mm",
    "Effective_Rainfall_mm",
    "Irrigation_Efficiency",
    "Net_Irrigation_Requirement_mm",
    "Recommended_Water_mm",
    "Potential_Water_Saving_Percent",
    "Farm_Area_Hectares",
    "Recommended_Water_m3"

]


for column in water_numeric_columns:

    if column in water_df.columns:

        water_df[column] = pd.to_numeric(
            water_df[column],
            errors="coerce"
        )


# =========================================================
# MAIN DATASET DROPDOWNS
# =========================================================

crop_list = sorted(
    df["Crop"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


state_list = sorted(
    df["State"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


season_list = sorted(
    df["Season"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


year_list = sorted(
    df["Crop_Year"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)


# =========================================================
# WATER DROPDOWNS
# =========================================================

if not water_df.empty:

    if "Crop" in water_df.columns:

        water_crop_list = sorted(
            water_df["Crop"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    else:

        water_crop_list = crop_list


    if "State" in water_df.columns:

        water_state_list = sorted(
            water_df["State"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    else:

        water_state_list = state_list


    if "Soil_Type" in water_df.columns:

        water_soil_list = sorted(
            water_df["Soil_Type"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    else:

        water_soil_list = []

else:

    water_crop_list = crop_list
    water_state_list = state_list
    water_soil_list = []


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html",

        crops=crop_list,

        states=state_list,

        seasons=season_list,

        years=year_list,

        water_crops=water_crop_list,

        water_states=water_state_list,

        water_soils=water_soil_list
    )


# =========================================================
# CROP YIELD PREDICTION
# =========================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        crop = request.form["crop"]

        state = request.form["state"]

        season = request.form["season"]

        year = int(
            request.form["year"]
        )

        area = float(
            request.form["area"]
        )


        # -------------------------------------------------
        # GET HISTORICAL DATA
        # -------------------------------------------------

        details = get_weather_details(
            crop,
            state,
            season,
            year
        )


        if details is None:

            return render_template(
                "result.html",

                error=(
                    "No historical data found "
                    "for the selected inputs."
                )
            )


        rainfall = details["rainfall"]

        fertilizer = details["fertilizer"]

        pesticide = details["pesticide"]


        # -------------------------------------------------
        # MACHINE LEARNING PREDICTION
        # -------------------------------------------------

        prediction = predict_crop_yield(

            crop,
            state,
            season,
            year,
            area,
            rainfall,
            fertilizer,
            pesticide
        )


        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        return render_template(

            "result.html",

            crop=crop,

            state=state,

            season=season,

            year=year,

            area=area,

            rainfall=rainfall,

            fertilizer=fertilizer,

            pesticide=pesticide,

            predicted_yield=
                prediction["yield"],

            estimated_production=
                prediction["production"],

            confidence=
                prediction["confidence"]
        )


    except Exception as error:

        print(
            "Prediction Error:",
            error
        )


        return render_template(

            "result.html",

            error=(
                "Unable to process prediction. "
                "Please check your inputs."
            )
        )


# =========================================================
# AGRICULTURE DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    data = df.copy()


    # -----------------------------------------------------
    # CLEAN DATA FOR JAVASCRIPT
    # -----------------------------------------------------

    data = data.replace(
        [float("inf"), float("-inf")],
        None
    )


    data = data.where(
        pd.notnull(data),
        None
    )


    # -----------------------------------------------------
    # DASHBOARD DATA
    #
    # This data is sent to dashboard.html.
    #
    # The dashboard JavaScript uses:
    # Crop
    # State
    # Season
    # Crop Year
    #
    # to dynamically filter the output.
    # -----------------------------------------------------

    dashboard_columns = [

        "Crop",
        "Crop_Year",
        "Season",
        "State",
        "Area",
        "Production",
        "Annual_Rainfall",
        "Fertilizer",
        "Pesticide",
        "Yield"

    ]


    dashboard_data = (

        data[dashboard_columns]

        .to_dict(
            orient="records"
        )

    )


    # -----------------------------------------------------
    # KPI VALUES
    # -----------------------------------------------------

    total_production = float(

        df["Production"]
        .fillna(0)
        .sum()

    )


    crop_count = int(

        df["Crop"]
        .nunique()

    )


    average_rainfall = float(

        df["Annual_Rainfall"]
        .dropna()
        .mean()

    )


    average_yield = float(

        df["Yield"]
        .dropna()
        .mean()

    )


    # -----------------------------------------------------
    # RENDER DASHBOARD
    # -----------------------------------------------------

    return render_template(

        "dashboard.html",

        dashboard_data=dashboard_data,

        total_production=round(
            total_production,
            2
        ),

        crop_count=crop_count,

        average_rainfall=round(
            average_rainfall,
            2
        ),

        average_yield=round(
            average_yield,
            2
        ),

        water_crops=water_crop_list,

        water_states=water_state_list,

        water_soils=water_soil_list

    )


# =========================================================
# WATER USAGE OPTIMIZER
# =========================================================

@app.route(
    "/dashboard/water-calculate",
    methods=["POST"]
)
def dashboard_water_calculate():

    try:

        # -------------------------------------------------
        # READ JSON
        # -------------------------------------------------

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No input data received."

            }), 400


        crop = str(
            data.get(
                "crop",
                ""
            )
        ).strip()


        state = str(
            data.get(
                "state",
                ""
            )
        ).strip()


        soil_type = str(
            data.get(
                "soil_type",
                ""
            )
        ).strip()


        farm_area = float(
            data.get(
                "farm_area",
                0
            )
        )


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not crop:

            return jsonify({

                "success": False,

                "error":
                    "Please select a crop."

            }), 400


        if not state:

            return jsonify({

                "success": False,

                "error":
                    "Please select a state."

            }), 400


        if not soil_type:

            return jsonify({

                "success": False,

                "error":
                    "Please select a soil type."

            }), 400


        if farm_area <= 0:

            return jsonify({

                "success": False,

                "error":
                    "Farm area must be greater than zero."

            }), 400


        # -------------------------------------------------
        # CHECK WATER DATASET
        # -------------------------------------------------

        if water_df.empty:

            return jsonify({

                "success": False,

                "error":
                    "Water usage dataset was not found."

            }), 404


        # -------------------------------------------------
        # EXACT MATCH
        #
        # Crop + State + Soil
        # -------------------------------------------------

        matches = water_df[

            (
                water_df["Crop"]
                .astype(str)
                == crop
            )

            &

            (
                water_df["State"]
                .astype(str)
                == state
            )

            &

            (
                water_df["Soil_Type"]
                .astype(str)
                == soil_type
            )

        ].copy()


        # -------------------------------------------------
        # FALLBACK 1
        #
        # Crop + Soil
        # -------------------------------------------------

        if matches.empty:

            matches = water_df[

                (
                    water_df["Crop"]
                    .astype(str)
                    == crop
                )

                &

                (
                    water_df["Soil_Type"]
                    .astype(str)
                    == soil_type
                )

            ].copy()


        # -------------------------------------------------
        # FALLBACK 2
        #
        # Crop only
        # -------------------------------------------------

        if matches.empty:

            matches = water_df[

                water_df["Crop"]
                .astype(str)
                == crop

            ].copy()


        # -------------------------------------------------
        # NO DATA
        # -------------------------------------------------

        if matches.empty:

            return jsonify({

                "success": False,

                "error":
                    "No water usage data found "
                    "for the selected combination."

            }), 404


        # -------------------------------------------------
        # SAFE AVERAGE
        # -------------------------------------------------

        def average_column(column):

            if column not in matches.columns:

                return 0


            value = pd.to_numeric(

                matches[column],

                errors="coerce"

            ).mean()


            if pd.isna(value):

                return 0


            return float(value)


        # -------------------------------------------------
        # GET WATER VALUES
        # -------------------------------------------------

        crop_water_requirement = average_column(

            "Crop_Water_Requirement_mm"

        )


        rainfall = average_column(

            "Rainfall_mm"

        )


        effective_rainfall = average_column(

            "Effective_Rainfall_mm"

        )


        efficiency = average_column(

            "Irrigation_Efficiency"

        )


        net_requirement = average_column(

            "Net_Irrigation_Requirement_mm"

        )


        water_saving = average_column(

            "Potential_Water_Saving_Percent"

        )


        # -------------------------------------------------
        # IRRIGATION EFFICIENCY
        # -------------------------------------------------

        if efficiency > 1:

            efficiency_decimal = (
                efficiency / 100
            )

        else:

            efficiency_decimal = efficiency


        if efficiency_decimal <= 0:

            efficiency_decimal = 1


        # -------------------------------------------------
        # RECOMMENDED WATER
        # -------------------------------------------------

        if net_requirement > 0:

            recommended_water_mm = (

                net_requirement
                /
                efficiency_decimal

            )

        else:

            recommended_water_mm = (

                crop_water_requirement
                -
                effective_rainfall

            )


        if recommended_water_mm < 0:

            recommended_water_mm = 0


        # -------------------------------------------------
        # WATER VOLUME
        #
        # 1 mm over 1 hectare
        # = 10 cubic metres
        # -------------------------------------------------

        recommended_water_m3 = (

            recommended_water_mm
            *
            farm_area
            *
            10

        )


        # -------------------------------------------------
        # IRRIGATION LEVEL
        # -------------------------------------------------

        if recommended_water_mm < 300:

            irrigation_level = "LOW"

        elif recommended_water_mm < 700:

            irrigation_level = "MODERATE"

        else:

            irrigation_level = "HIGH"


        # -------------------------------------------------
        # WATER SAVING METHOD
        # -------------------------------------------------

        method = "Controlled irrigation"


        if "Water_Saving_Method" in matches.columns:

            modes = (

                matches["Water_Saving_Method"]

                .dropna()

                .astype(str)

            )


            if not modes.empty:

                method = (

                    modes
                    .mode()
                    .iloc[0]

                )


        # -------------------------------------------------
        # WATER SAVING MESSAGE
        # -------------------------------------------------

        if water_saving >= 35:

            saving_message = (

                "High water-saving potential. "
                "Use the recommended irrigation "
                "method and avoid unnecessary irrigation."

            )

        elif water_saving >= 20:

            saving_message = (

                "Good water-saving potential. "
                "Monitor rainfall and irrigate "
                "only when required."

            )

        else:

            saving_message = (

                "Use controlled irrigation and "
                "regularly monitor soil moisture."

            )


        # -------------------------------------------------
        # RETURN WATER RESULT
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "crop": crop,

            "state": state,

            "soil_type": soil_type,

            "farm_area": round(
                farm_area,
                2
            ),

            "crop_water_requirement": round(
                crop_water_requirement,
                2
            ),

            "rainfall": round(
                rainfall,
                2
            ),

            "effective_rainfall": round(
                effective_rainfall,
                2
            ),

            "irrigation_efficiency": round(
                efficiency_decimal * 100,
                2
            ),

            "net_requirement": round(
                net_requirement,
                2
            ),

            "recommended_water_mm": round(
                recommended_water_mm,
                2
            ),

            "recommended_water_m3": round(
                recommended_water_m3,
                2
            ),

            "irrigation_level":
                irrigation_level,

            "saving_percentage": round(
                water_saving,
                2
            ),

            "water_saving_method":
                method,

            "saving_message":
                saving_message

        })


    except Exception as error:

        print(
            "Dashboard Water Error:",
            error
        )


        return jsonify({

            "success": False,

            "error":
                "Unable to calculate water usage. "
                + str(error)

        }), 500


# =========================================================
# POWER BI DATA API
# =========================================================

@app.route("/powerbi-data")
def powerbi_data():

    try:

        # -------------------------------------------------
        # CROP DATA
        # -------------------------------------------------

        crop_columns = [

            "Crop",
            "Crop_Year",
            "Season",
            "State",
            "Area",
            "Production",
            "Annual_Rainfall",
            "Fertilizer",
            "Pesticide",
            "Yield"

        ]


        crop_data = df[
            crop_columns
        ].copy()


        crop_data = crop_data.replace(

            [
                float("inf"),
                float("-inf")
            ],

            None

        )


        crop_data = crop_data.where(

            pd.notnull(crop_data),

            None

        )


        crop_records = (

            crop_data

            .to_dict(
                orient="records"
            )

        )


        # -------------------------------------------------
        # WATER DATA
        # -------------------------------------------------

        water_records = []


        if not water_df.empty:

            water_copy = water_df.copy()


            water_copy = water_copy.replace(

                [
                    float("inf"),
                    float("-inf")
                ],

                None

            )


            water_copy = water_copy.where(

                pd.notnull(water_copy),

                None

            )


            water_records = (

                water_copy

                .to_dict(
                    orient="records"
                )

            )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "crop_data":
                crop_records,

            "water_data":
                water_records,

            "metadata": {

                "crop_count":
                    int(
                        df["Crop"]
                        .nunique()
                    ),

                "state_count":
                    int(
                        df["State"]
                        .nunique()
                    ),

                "season_count":
                    int(
                        df["Season"]
                        .nunique()
                    ),

                "total_records":
                    int(
                        len(df)
                    )

            }

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 500


# =========================================================
# DISEASE DETECTOR
# =========================================================
#
# Flow:
#
# User uploads image
#        ↓
# Flask receives image
#        ↓
# disease_api.py
#        ↓
# TensorFlow model
#        ↓
# class_names.json
#        ↓
# disease_information.csv
#        ↓
# Disease information
#
# Result:
# Disease
# Crop
# Confidence
# Sensitivity
# Symptoms
# Treatment
# Pesticide guidance
# Prevention
# Recommendation
#
# =========================================================

@app.route(
    "/dashboard/disease-detect",
    methods=["POST"]
)
def dashboard_disease_detect():

    image_path = None


    try:

        # -------------------------------------------------
        # CHECK IMAGE
        # -------------------------------------------------

        if "image" not in request.files:

            return jsonify({

                "success": False,

                "error":
                    "Please upload a leaf image."

            }), 400


        image = request.files["image"]


        if image.filename == "":

            return jsonify({

                "success": False,

                "error":
                    "No image was selected."

            }), 400


        # -------------------------------------------------
        # ALLOWED IMAGE TYPES
        # -------------------------------------------------

        allowed_extensions = {

            ".jpg",
            ".jpeg",
            ".png",
            ".webp"

        }


        extension = (

            Path(
                image.filename
            )
            .suffix
            .lower()

        )


        if extension not in allowed_extensions:

            return jsonify({

                "success": False,

                "error":
                    "Please upload JPG, JPEG, PNG, "
                    "or WEBP image."

            }), 400


        # -------------------------------------------------
        # CREATE TEMPORARY UPLOAD DIRECTORY
        # -------------------------------------------------

        upload_folder = (

            PROJECT_DIR
            /
            "disease_uploads"

        )


        upload_folder.mkdir(

            parents=True,

            exist_ok=True

        )


        # -------------------------------------------------
        # CREATE UNIQUE FILE
        # -------------------------------------------------

        temporary_filename = (

            str(uuid.uuid4())
            +
            extension

        )


        image_path = (

            upload_folder
            /
            temporary_filename

        )


        # -------------------------------------------------
        # SAVE IMAGE
        # -------------------------------------------------

        image.save(
            str(image_path)
        )


        print("=" * 70)
        print("DISEASE DETECTION")
        print("=" * 70)
        print("Uploaded image:", image.filename)
        print("Temporary path:", image_path)


        # -------------------------------------------------
        # IMPORT DISEASE API
        #
        # PROJECT_DIR is already added to sys.path
        # above, so this works even though app.py
        # is inside website/.
        # -------------------------------------------------

        from disease_api import predict_disease


        # -------------------------------------------------
        # RUN DISEASE MODEL
        # -------------------------------------------------

        result = predict_disease(

            str(image_path)

        )


        # -------------------------------------------------
        # RETURN RESULT
        # -------------------------------------------------

        response = {

            "success": True,

            "disease":
                result.get(
                    "disease",
                    "Unknown"
                ),

            "crop":
                result.get(
                    "crop",
                    "Unknown"
                ),

            "confidence":
                result.get(
                    "confidence",
                    0
                ),

            "sensitivity":
                result.get(
                    "sensitivity",
                    "-"
                ),

            "symptoms":
                result.get(
                    "symptoms",
                    "No symptom information available."
                ),

            "treatment":
                result.get(
                    "treatment",
                    "No treatment information available."
                ),

            "pesticide":
                result.get(
                    "pesticide",
                    "Follow approved local agricultural guidance and product label."
                ),

            "prevention":
                result.get(
                    "prevention",
                    "Maintain crop sanitation and regular monitoring."
                ),

            "recommendation":
                result.get(
                    "recommendation",
                    "Monitor the crop regularly and seek local agricultural advice."
                )

        }


        return jsonify(response)


    except Exception as error:

        print("=" * 70)
        print("DISEASE DETECTION ERROR")
        print("=" * 70)
        print(error)


        return jsonify({

            "success": False,

            "error":
                "Unable to analyze the image. "
                + str(error)

        }), 500


    finally:

        # -------------------------------------------------
        # DELETE TEMPORARY IMAGE
        # -------------------------------------------------

        if image_path is not None:

            try:

                if image_path.exists():

                    image_path.unlink()

            except Exception as cleanup_error:

                print(
                    "Temporary image cleanup error:",
                    cleanup_error
                )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "running",

        "application":
            "AgriAI Agriculture Data Warehouse",

        "crop_dataset":
            os.path.exists(DATASET_PATH),

        "water_dataset":
            os.path.exists(WATER_DATASET_PATH),

        "disease_api":
            os.path.exists(
                PROJECT_DIR /
                "disease_api.py"
            ),

        "disease_model":
            os.path.exists(
                PROJECT_DIR /
                "disease_model" /
                "plant_disease_model.keras"
            ),

        "disease_classes":
            os.path.exists(
                PROJECT_DIR /
                "disease_model" /
                "class_names.json"
            )

    })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AgriAI Agriculture Data Warehouse")
    print("=" * 70)

    print()
    print("MAIN WEBSITE:")
    print(
        "http://127.0.0.1:5000/"
    )

    print()
    print("DASHBOARD:")
    print(
        "http://127.0.0.1:5000/dashboard"
    )

    print()
    print("HEALTH CHECK:")
    print(
        "http://127.0.0.1:5000/health"
    )

    print()
    print("Features:")
    print("1. Crop Yield Prediction")
    print("2. Agriculture Dashboard")
    print("3. Crop / State / Season / Year Filtering")
    print("4. Water Usage Optimizer")
    print("5. Disease Detector")
    print("6. Power BI Data API")

    print()
    print("=" * 70)


    # Local development only. Render uses Gunicorn and does not execute
    # this block when started with the production start command.
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    app.run(
        debug=debug,
        host=host,
        port=port
    )