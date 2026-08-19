from pathlib import Path

app_file = Path(r".\website\app.py")

text = app_file.read_text(encoding="utf-8")

marker = "# =========================================================\n# RUN APPLICATION"

if marker not in text:
    raise SystemExit(
        "Could not find the RUN APPLICATION section in website\\app.py"
    )

# Prevent duplicate insertion
if '@app.route("/dashboard/disease-detect"' in text:
    print("Disease Detector route is already present.")
    raise SystemExit(0)

disease_route = r'''
# =========================================================
# DISEASE DETECTOR
# =========================================================
#
# This is a backend API used by the existing dashboard.
# It does NOT create a separate page.
#
# Flow:
# Leaf image
#     ↓
# TensorFlow disease model
#     ↓
# Disease information CSV
#     ↓
# Disease + treatment + prevention
# =========================================================

@app.route(
    "/dashboard/disease-detect",
    methods=["POST"]
)
def dashboard_disease_detect():

    try:

        # -------------------------------------------------
        # CHECK IMAGE
        # -------------------------------------------------

        if "image" not in request.files:

            return jsonify({
                "success": False,
                "error": "Please upload a leaf image."
            }), 400


        image = request.files["image"]


        if image.filename == "":

            return jsonify({
                "success": False,
                "error": "No image was selected."
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
            Path(image.filename)
            .suffix
            .lower()
        )


        if extension not in allowed_extensions:

            return jsonify({
                "success": False,
                "error":
                    "Please upload JPG, JPEG, PNG, or WEBP image."
            }), 400


        # -------------------------------------------------
        # SAVE TEMPORARY IMAGE
        # -------------------------------------------------

        upload_folder = (
            Path(app.root_path)
            / "disease_uploads"
        )

        upload_folder.mkdir(
            parents=True,
            exist_ok=True
        )


        import uuid

        temporary_filename = (
            str(uuid.uuid4())
            + extension
        )

        image_path = (
            upload_folder
            / temporary_filename
        )


        image.save(
            str(image_path)
        )


        # -------------------------------------------------
        # RUN AI MODEL
        # -------------------------------------------------

        from disease_api import predict_disease


        result = predict_disease(
            str(image_path)
        )


        # -------------------------------------------------
        # DELETE TEMPORARY IMAGE
        # -------------------------------------------------

        try:

            image_path.unlink()

        except Exception:

            pass


        # -------------------------------------------------
        # RETURN RESULT
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "disease":
                result["disease"],

            "crop":
                result["crop"],

            "confidence":
                result["confidence"],

            "sensitivity":
                result["sensitivity"],

            "symptoms":
                result["symptoms"],

            "treatment":
                result["treatment"],

            "pesticide":
                result["pesticide"],

            "prevention":
                result["prevention"],

            "recommendation":
                result["recommendation"]

        })


    except Exception as error:

        print(
            "Disease Detection Error:",
            error
        )


        return jsonify({

            "success": False,

            "error":
                "Unable to analyze the image. "
                + str(error)

        }), 500


'''

new_text = text.replace(
    marker,
    disease_route + "\n" + marker,
    1
)

app_file.write_text(
    new_text,
    encoding="utf-8"
)

print()
print("=" * 70)
print("DISEASE DETECTOR ROUTE ADDED SUCCESSFULLY")
print("=" * 70)
print()
print("Updated file:")
print(app_file.resolve())
print()
print("Existing Water Usage code was not replaced.")
print("=" * 70)