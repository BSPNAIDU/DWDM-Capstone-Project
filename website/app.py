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
    from database import get_weather_details
except Exception as error:
    print("WARNING: database.py could not be imported.")
    print("Database import error:", error)

    def get_weather_details(crop, state, season, year):
        return None


try:
    from predictor import predict_crop_yield
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
# AGRICULTURAL SOLID WASTE MANAGEMENT
# =========================================================
#
# This module is intentionally DATASET-FREE.
# It uses agriculture-specific rule-based processing so it can
# be added to the existing AgriAI application without changing
# the crop-yield or disease datasets.
#
# Flow:
# Waste generation -> Collection & segregation -> Treatment /
# Conversion -> Resource recovery -> Utilization -> Benefits
#
# The values returned by this module are planning estimates for
# demonstration/academic use, not laboratory measurements.
# =========================================================

SOLID_WASTE_PROFILES = {
    "crop_residues": {
        "name": "Crop Residues",
        "examples": "Straw, stalks, leaves, husks",
        "category": "Organic / Biodegradable",
        "treatments": ["Composting", "Biogas Production", "Thermal Conversion"],
        "default_treatment": "Composting",
        "recovery_rate": 0.90,
        "primary_output": "Compost / Vermicompost",
        "secondary_output": "Biochar / Biogas",
        "utilization": "Agricultural Use",
        "benefits": [
            "Reduces open burning and field pollution",
            "Improves soil fertility",
            "Supports circular agriculture"
        ]
    },
    "fruit_vegetable_waste": {
        "name": "Fruit & Vegetable Waste",
        "examples": "Peels, rotten produce, market waste",
        "category": "Organic / Biodegradable",
        "treatments": ["Composting", "Biogas Production"],
        "default_treatment": "Composting",
        "recovery_rate": 0.88,
        "primary_output": "Compost / Vermicompost",
        "secondary_output": "Biogas",
        "utilization": "Agricultural Use / Energy Generation",
        "benefits": [
            "Reduces organic waste accumulation",
            "Produces useful organic fertilizer",
            "Can recover energy through anaerobic digestion"
        ]
    },
    "animal_farm_waste": {
        "name": "Animal & Farm Waste",
        "examples": "Cow dung, poultry litter, manure",
        "category": "Organic / Biodegradable",
        "treatments": ["Biogas Production", "Composting"],
        "default_treatment": "Biogas Production",
        "recovery_rate": 0.92,
        "primary_output": "Biogas",
        "secondary_output": "Digestate / Organic Fertilizer",
        "utilization": "Energy Generation / Agricultural Use",
        "benefits": [
            "Generates renewable biogas",
            "Produces nutrient-rich digestate",
            "Reduces unmanaged manure pollution"
        ]
    },
    "agro_processing_waste": {
        "name": "Agro-Processing Waste",
        "examples": "Hulls, bagasse, shells, seed waste",
        "category": "Organic / Recoverable",
        "treatments": ["Composting", "Thermal Conversion", "Biogas Production"],
        "default_treatment": "Thermal Conversion",
        "recovery_rate": 0.86,
        "primary_output": "Biochar / Bio-oil",
        "secondary_output": "Compost / Bioenergy",
        "utilization": "Industrial Use / Energy Generation",
        "benefits": [
            "Converts processing residues into useful resources",
            "Reduces disposal requirements",
            "Supports renewable energy and material recovery"
        ]
    },
    "agricultural_plastic": {
        "name": "Agricultural Plastic Waste",
        "examples": "Mulching sheets, bags, drip components",
        "category": "Recyclable Material",
        "treatments": ["Recycling", "Safe Collection"],
        "default_treatment": "Recycling",
        "recovery_rate": 0.85,
        "primary_output": "Recycled Materials",
        "secondary_output": "Reusable Plastic Products",
        "utilization": "Industrial Use / Reuse in Production",
        "benefits": [
            "Reduces plastic leakage into soil and water",
            "Recovers material for reuse",
            "Supports circular resource utilization"
        ]
    },
    "hazardous_farm_waste": {
        "name": "Hazardous Farm Waste",
        "examples": "Pesticide containers, fertilizer bags, contaminated materials",
        "category": "Hazardous / Special Handling",
        "treatments": ["Safe Treatment", "Authorized Disposal"],
        "default_treatment": "Safe Treatment",
        "recovery_rate": 0.0,
        "primary_output": "Safe Disposal",
        "secondary_output": "No direct resource recovery",
        "utilization": "Environmental Protection",
        "benefits": [
            "Reduces chemical exposure risk",
            "Prevents contamination of soil and water",
            "Supports safe agricultural waste handling"
        ]
    }
}


def _solid_waste_profile(waste_type):
    key = str(waste_type or "").strip().lower()
    aliases = {
        "crop residues": "crop_residues",
        "crop residue": "crop_residues",
        "straw": "crop_residues",
        "fruit and vegetable waste": "fruit_vegetable_waste",
        "fruit & vegetable waste": "fruit_vegetable_waste",
        "fruit_vegetable_waste": "fruit_vegetable_waste",
        "animal and farm waste": "animal_farm_waste",
        "animal & farm waste": "animal_farm_waste",
        "animal_farm_waste": "animal_farm_waste",
        "agro-processing waste": "agro_processing_waste",
        "agro_processing_waste": "agro_processing_waste",
        "agricultural plastic waste": "agricultural_plastic",
        "agricultural plastic": "agricultural_plastic",
        "agricultural_plastic": "agricultural_plastic",
        "hazardous farm waste": "hazardous_farm_waste",
        "hazardous_farm_waste": "hazardous_farm_waste",
    }
    key = aliases.get(key, key)
    return key, SOLID_WASTE_PROFILES.get(key)


@app.route("/dashboard/solid-waste-options")
def solid_waste_options():
    """Return the agriculture solid-waste categories for the dashboard UI."""
    return jsonify({
        "success": True,
        "dataset_required": False,
        "categories": [
            {
                "key": key,
                "name": profile["name"],
                "examples": profile["examples"],
                "category": profile["category"],
                "treatments": profile["treatments"]
            }
            for key, profile in SOLID_WASTE_PROFILES.items()
        ]
    })


@app.route("/dashboard/solid-waste-calculate", methods=["POST"])
def dashboard_solid_waste_calculate():
    """
    Calculate a dataset-free agricultural solid-waste management plan.

    Expected JSON:
        {
            "waste_type": "crop_residues",
            "quantity_kg": 100,
            "treatment": "Composting"   # optional
        }
    """
    try:
        data = request.get_json(silent=True) or {}

        waste_type = str(data.get("waste_type", "")).strip()
        quantity_kg = float(data.get("quantity_kg", 0))
        selected_treatment = str(data.get("treatment", "")).strip()

        if not waste_type:
            return jsonify({
                "success": False,
                "error": "Please select an agricultural waste type."
            }), 400

        if quantity_kg <= 0:
            return jsonify({
                "success": False,
                "error": "Waste quantity must be greater than zero."
            }), 400

        if quantity_kg > 1000000:
            return jsonify({
                "success": False,
                "error": "Please enter a realistic waste quantity."
            }), 400

        key, profile = _solid_waste_profile(waste_type)
        if profile is None:
            return jsonify({
                "success": False,
                "error": "Unknown agricultural waste type."
            }), 400

        treatment = selected_treatment or profile["default_treatment"]
        if treatment not in profile["treatments"]:
            return jsonify({
                "success": False,
                "error": "Selected treatment is not suitable for this waste category.",
                "available_treatments": profile["treatments"]
            }), 400

        # Rule-based planning estimates. These are intentionally transparent
        # and do not require a machine-learning model or additional dataset.
        recovery_kg = quantity_kg * profile["recovery_rate"]
        residual_kg = max(quantity_kg - recovery_kg, 0)

        if treatment == "Composting":
            primary_output_kg = quantity_kg * 0.55
            output_unit = "kg compost / vermicompost"
            process_note = "Aerobic biological conversion of biodegradable agricultural waste."
        elif treatment == "Biogas Production":
            primary_output_kg = quantity_kg * 0.70
            output_unit = "kg digestate / fertilizer equivalent"
            process_note = "Anaerobic digestion with biogas recovery and digestate utilization."
        elif treatment == "Thermal Conversion":
            primary_output_kg = quantity_kg * 0.30
            output_unit = "kg biochar / recovered solid product"
            process_note = "Controlled thermal conversion for biochar/bio-oil resource recovery."
        elif treatment == "Recycling":
            primary_output_kg = recovery_kg
            output_unit = "kg recycled material"
            process_note = "Segregation, cleaning and material recovery for reuse/reprocessing."
        elif treatment == "Safe Treatment":
            primary_output_kg = 0
            output_unit = "kg requiring authorized safe handling"
            process_note = "Segregate and route hazardous agricultural waste to authorized treatment/disposal."
        elif treatment == "Safe Collection":
            primary_output_kg = recovery_kg
            output_unit = "kg collected for authorized recovery"
            process_note = "Separate agricultural plastics and prevent uncontrolled dumping or burning."
        elif treatment == "Authorized Disposal":
            primary_output_kg = 0
            output_unit = "kg safely disposed"
            process_note = "Use an authorized hazardous-waste collection and disposal pathway."
        else:
            primary_output_kg = recovery_kg
            output_unit = "kg recovered material"
            process_note = "Controlled resource recovery."

        if key == "hazardous_farm_waste":
            risk_level = "HIGH"
            handling = "Do not burn, bury, reuse or mix with organic waste. Use authorized collection/disposal."
            output = profile["primary_output"]
        elif key == "agricultural_plastic":
            risk_level = "MEDIUM"
            handling = "Keep plastics separate, dry and free from soil/chemical contamination before recovery."
            output = "Recycled Materials"
        else:
            risk_level = "LOW"
            handling = "Segregate at source and keep biodegradable waste free from hazardous contaminants."
            output = profile["primary_output"]

        # Simple planning indicators for the dashboard.
        landfill_avoidance_kg = round(recovery_kg, 2)
        recovery_percent = round(profile["recovery_rate"] * 100, 2)
        residual_percent = round(max(100 - recovery_percent, 0), 2)

        if recovery_percent >= 85:
            efficiency = "HIGH"
        elif recovery_percent >= 60:
            efficiency = "MODERATE"
        else:
            efficiency = "CONTROLLED"

        return jsonify({
            "success": True,
            "dataset_required": False,
            "module": "Agricultural Solid Waste Management",
            "waste_type": key,
            "waste_name": profile["name"],
            "examples": profile["examples"],
            "segregation_category": profile["category"],
            "quantity_kg": round(quantity_kg, 2),
            "treatment": treatment,
            "recommended_treatment": profile["default_treatment"],
            "available_treatments": profile["treatments"],
            "recovery_percent": recovery_percent,
            "recovery_kg": round(recovery_kg, 2),
            "residual_kg": round(residual_kg, 2),
            "residual_percent": residual_percent,
            "primary_output": output,
            "estimated_output_kg": round(primary_output_kg, 2),
            "output_unit": output_unit,
            "secondary_output": profile["secondary_output"],
            "utilization": profile["utilization"],
            "process_note": process_note,
            "risk_level": risk_level,
            "handling_guidance": handling,
            "efficiency": efficiency,
            "landfill_avoidance_kg": landfill_avoidance_kg,
            "benefits": profile["benefits"],
            "monitoring": [
                "Record waste quantity at source",
                "Check segregation quality before treatment",
                "Track recovered material or energy output",
                "Monitor residual waste and environmental impact"
            ]
        })

    except Exception as error:
        print("Solid Waste Management Error:", error)
        return jsonify({
            "success": False,
            "error": "Unable to process agricultural solid waste request. " + str(error)
        }), 500


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