from pathlib import Path

FILE = Path(r".\website\templates\dashboard.html")

html = FILE.read_text(encoding="utf-8")

# ============================================================
# 1. ADD DISEASE CSS
# ============================================================

css_marker = """
        /* =====================================================
           FOOTER
        ===================================================== */
"""

disease_css = r"""
        /* =====================================================
           DISEASE DETECTOR
        ===================================================== */

        #diseaseSection {
            display: none;
        }

        .disease-header {
            background:
                linear-gradient(
                    135deg,
                    rgba(9,124,99,0.85),
                    rgba(12,77,91,0.85)
                );
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 15px;
        }

        .disease-header h2 {
            margin: 0 0 7px;
            font-size: 22px;
        }

        .disease-header p {
            margin: 0;
            color: #b8d8d1;
            font-size: 11px;
            line-height: 1.6;
        }

        .disease-upload-box {
            background:
                rgba(255,255,255,0.08);
            border:
                1px solid
                rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 18px;
        }

        .disease-upload-label {
            display: block;
            font-size: 11px;
            color: #b8d8d1;
            margin-bottom: 8px;
            font-weight: bold;
        }

        .disease-file-input {
            width: 100%;
            padding: 12px;
            border-radius: 9px;
            border:
                1px solid
                rgba(255,255,255,0.15);
            background:
                rgba(255,255,255,0.08);
            color: white;
            cursor: pointer;
        }

        .disease-preview {
            display: none;
            margin-top: 18px;
            text-align: center;
        }

        .disease-preview img {
            max-width: 320px;
            max-height: 280px;
            border-radius: 14px;
            border:
                2px solid
                rgba(60,235,145,0.5);
            object-fit: contain;
        }

        .disease-button {
            width: 100%;
            margin-top: 18px;
            padding: 14px;
            border: none;
            border-radius: 9px;
            background:
                linear-gradient(
                    90deg,
                    #0fc96a,
                    #00e083
                );
            color: white;
            font-weight: bold;
            cursor: pointer;
            font-size: 13px;
        }

        .disease-button:hover {
            transform: translateY(-1px);
        }

        .disease-button:disabled {
            opacity: 0.55;
            cursor: not-allowed;
            transform: none;
        }

        .disease-loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #52e99a;
            font-size: 12px;
        }

        .disease-error {
            display: none;
            background:
                rgba(239,68,68,0.15);
            border:
                1px solid
                rgba(239,68,68,0.3);
            padding: 14px;
            border-radius: 10px;
            color: #ffb2b2;
            margin-top: 12px;
            font-size: 11px;
        }

        .disease-result {
            display: none;
        }

        .disease-result-header {
            background:
                linear-gradient(
                    135deg,
                    rgba(20,150,95,0.22),
                    rgba(20,80,100,0.22)
                );
            border:
                1px solid
                rgba(60,235,145,0.18);
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 15px;
        }

        .disease-result-title {
            font-size: 10px;
            color: #9fc3bd;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .disease-name {
            font-size: 25px;
            font-weight: bold;
            margin-top: 7px;
            color: #48e99a;
        }

        .disease-meta {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 15px;
        }

        .disease-meta-card {
            background:
                rgba(255,255,255,0.07);
            border-radius: 10px;
            padding: 13px;
        }

        .disease-meta-card .label {
            font-size: 9px;
            color: #9fc3bd;
        }

        .disease-meta-card .value {
            font-size: 16px;
            font-weight: bold;
            margin-top: 5px;
        }

        .disease-info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .disease-info-card {
            background:
                rgba(255,255,255,0.08);
            border:
                1px solid
                rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 18px;
        }

        .disease-info-card.full {
            grid-column: 1 / -1;
        }

        .disease-info-card h3 {
            margin: 0 0 10px;
            font-size: 13px;
        }

        .disease-info-card p {
            margin: 0;
            color: #c3d6d2;
            font-size: 11px;
            line-height: 1.7;
        }

        .disease-info-card.symptoms h3 {
            color: #ffd166;
        }

        .disease-info-card.treatment h3 {
            color: #5ee7ff;
        }

        .disease-info-card.pesticide h3 {
            color: #ffbd69;
        }

        .disease-info-card.prevention h3 {
            color: #48e99a;
        }

        .disease-info-card.recommendation h3 {
            color: #b79cff;
        }

        .disease-warning {
            margin-top: 12px;
            padding: 12px;
            border-radius: 9px;
            background:
                rgba(255,193,7,0.10);
            border:
                1px solid
                rgba(255,193,7,0.20);
            color: #ffe5a3;
            font-size: 10px;
            line-height: 1.5;
        }

        @media(max-width: 700px) {

            .disease-info-grid {
                grid-template-columns: 1fr;
            }

            .disease-info-card.full {
                grid-column: auto;
            }

            .disease-meta {
                grid-template-columns: 1fr;
            }

        }

"""

if "DISEASE DETECTOR" not in html:

    if css_marker not in html:
        raise SystemExit(
            "Could not find CSS insertion point."
        )

    html = html.replace(
        css_marker,
        disease_css + css_marker,
        1
    )


# ============================================================
# 2. ADD SIDEBAR BUTTON
# ============================================================

water_button_end = """
    <button
        class="menu-item"
        onclick="showWaterUsage()"
        id="waterMenu"
    >
        <i class="fas fa-droplet"></i>

        <span>Water Usage</span>

    </button>
"""

disease_button = """

    <button
        class="menu-item"
        onclick="showDiseaseDetector()"
        id="diseaseMenu"
    >
        <i class="fas fa-virus"></i>

        <span>Disease Detector</span>

    </button>
"""

if 'id="diseaseMenu"' not in html:

    if water_button_end not in html:
        raise SystemExit(
            "Could not find Water Usage menu button."
        )

    html = html.replace(
        water_button_end,
        water_button_end + disease_button,
        1
    )


# ============================================================
# 3. ADD DISEASE SECTION
# ============================================================

main_end = """
</main>


<script>
"""

disease_section = r"""
<!-- =================================================
     DISEASE DETECTOR SECTION
================================================== -->

<section id="diseaseSection">

    <div class="disease-header">

        <h2>
            🦠 Disease Detector
        </h2>

        <p>
            Upload a crop or leaf image and let the
            AI model identify the most likely disease,
            then view treatment guidance and prevention
            recommendations.
        </p>

    </div>


    <div class="disease-upload-box">

        <label
            class="disease-upload-label"
            for="diseaseImage"
        >
            📷 Upload Leaf / Crop Image
        </label>


        <input
            type="file"
            id="diseaseImage"
            class="disease-file-input"
            accept="image/jpeg,image/jpg,image/png,image/webp"
            onchange="previewDiseaseImage()"
        >


        <div
            id="diseasePreview"
            class="disease-preview"
        >

            <img
                id="diseasePreviewImage"
                src=""
                alt="Leaf image preview"
            >

        </div>


        <button
            type="button"
            id="diseaseAnalyzeButton"
            class="disease-button"
            onclick="detectDisease()"
        >

            <i class="fas fa-microscope"></i>

            Analyze Disease

        </button>


        <div
            id="diseaseLoading"
            class="disease-loading"
        >

            <i class="fas fa-spinner fa-spin"></i>

            Analyzing leaf image with AI...

        </div>


        <div
            id="diseaseError"
            class="disease-error"
        ></div>

    </div>


    <!-- =================================================
         DISEASE RESULT
    ================================================== -->

    <div
        id="diseaseResult"
        class="disease-result"
    >

        <div class="disease-result-header">

            <div class="disease-result-title">
                AI Disease Detection Result
            </div>


            <div
                id="diseaseName"
                class="disease-name"
            >
                -
            </div>


            <div class="disease-meta">

                <div class="disease-meta-card">

                    <div class="label">
                        CROP
                    </div>

                    <div
                        id="diseaseCrop"
                        class="value"
                    >
                        -
                    </div>

                </div>


                <div class="disease-meta-card">

                    <div class="label">
                        CONFIDENCE
                    </div>

                    <div
                        id="diseaseConfidence"
                        class="value"
                    >
                        -
                    </div>

                </div>


                <div class="disease-meta-card">

                    <div class="label">
                        SENSITIVITY
                    </div>

                    <div
                        id="diseaseSensitivity"
                        class="value"
                    >
                        -
                    </div>

                </div>

            </div>

        </div>


        <div class="disease-info-grid">


            <div
                class="disease-info-card symptoms"
            >

                <h3>
                    🔎 Symptoms
                </h3>

                <p id="diseaseSymptoms">
                    -
                </p>

            </div>


            <div
                class="disease-info-card treatment"
            >

                <h3>
                    💊 Treatment
                </h3>

                <p id="diseaseTreatment">
                    -
                </p>

            </div>


            <div
                class="disease-info-card pesticide"
            >

                <h3>
                    🧪 Pesticide Guidance
                </h3>

                <p id="diseasePesticide">
                    -
                </p>

                <div class="disease-warning">

                    Always use only products approved
                    for the crop and disease in your
                    location and follow the product label.

                </div>

            </div>


            <div
                class="disease-info-card prevention"
            >

                <h3>
                    🛡️ Prevention
                </h3>

                <p id="diseasePrevention">
                    -
                </p>

            </div>


            <div
                class="disease-info-card recommendation full"
            >

                <h3>
                    💡 Recommendation
                </h3>

                <p id="diseaseRecommendation">
                    -
                </p>

            </div>


        </div>

    </div>

</section>


"""

if 'id="diseaseSection"' not in html:

    if main_end not in html:
        raise SystemExit(
            "Could not find main closing point."
        )

    html = html.replace(
        main_end,
        disease_section + main_end,
        1
    )


# ============================================================
# 4. ADD JAVASCRIPT
# ============================================================

script_marker = """
/* =========================================================
   INITIALIZE
========================================================= */
"""

disease_js = r"""
/* =========================================================
   DISEASE DETECTOR
========================================================= */

function showDiseaseDetector() {

    document.getElementById(
        "dashboardSection"
    ).style.display = "none";


    document.getElementById(
        "waterSection"
    ).style.display = "none";


    document.getElementById(
        "diseaseSection"
    ).style.display = "block";


    document.querySelectorAll(
        ".menu-item"
    ).forEach(
        function(item) {

            item.classList.remove(
                "active"
            );

        }
    );


    const menu =
        document.getElementById(
            "diseaseMenu"
        );


    if (menu) {

        menu.classList.add(
            "active"
        );

    }


    window.scrollTo(
        {
            top: 0,
            behavior: "smooth"
        }
    );

}


/* =========================================================
   IMAGE PREVIEW
========================================================= */

function previewDiseaseImage() {

    const input =
        document.getElementById(
            "diseaseImage"
        );


    const preview =
        document.getElementById(
            "diseasePreview"
        );


    const previewImage =
        document.getElementById(
            "diseasePreviewImage"
        );


    const result =
        document.getElementById(
            "diseaseResult"
        );


    const error =
        document.getElementById(
            "diseaseError"
        );


    result.style.display =
        "none";


    error.style.display =
        "none";


    if (
        !input.files ||
        !input.files[0]
    ) {

        preview.style.display =
            "none";

        return;

    }


    const file =
        input.files[0];


    const allowedTypes = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp"
    ];


    if (
        !allowedTypes.includes(
            file.type
        )
    ) {

        showDiseaseError(
            "Please select a JPG, JPEG, PNG, or WEBP image."
        );


        input.value = "";


        preview.style.display =
            "none";


        return;

    }


    const reader =
        new FileReader();


    reader.onload =
        function(event) {

            previewImage.src =
                event.target.result;


            preview.style.display =
                "block";

        };


    reader.readAsDataURL(
        file
    );

}


/* =========================================================
   DISEASE DETECTION
========================================================= */

async function detectDisease() {

    const input =
        document.getElementById(
            "diseaseImage"
        );


    const loading =
        document.getElementById(
            "diseaseLoading"
        );


    const button =
        document.getElementById(
            "diseaseAnalyzeButton"
        );


    const resultBox =
        document.getElementById(
            "diseaseResult"
        );


    const errorBox =
        document.getElementById(
            "diseaseError"
        );


    errorBox.style.display =
        "none";


    resultBox.style.display =
        "none";


    if (
        !input.files ||
        !input.files[0]
    ) {

        showDiseaseError(
            "Please select a leaf image first."
        );

        return;

    }


    const formData =
        new FormData();


    formData.append(
        "image",
        input.files[0]
    );


    loading.style.display =
        "block";


    button.disabled =
        true;


    try {

        const response =
            await fetch(
                "/dashboard/disease-detect",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        loading.style.display =
            "none";


        button.disabled =
            false;


        if (
            !response.ok ||
            !data.success
        ) {

            showDiseaseError(
                data.error ||
                "Unable to detect disease."
            );

            return;

        }


        /* -----------------------------------------
           DISPLAY RESULT
        ----------------------------------------- */


        document.getElementById(
            "diseaseName"
        ).textContent =
            formatDiseaseName(
                data.disease
            );


        document.getElementById(
            "diseaseCrop"
        ).textContent =
            data.crop ||
            "-";


        document.getElementById(
            "diseaseConfidence"
        ).textContent =
            Number(
                data.confidence
            ).toFixed(2)
            + "%";


        document.getElementById(
            "diseaseSensitivity"
        ).textContent =
            data.sensitivity ||
            "-";


        document.getElementById(
            "diseaseSymptoms"
        ).textContent =
            data.symptoms ||
            "-";


        document.getElementById(
            "diseaseTreatment"
        ).textContent =
            data.treatment ||
            "-";


        document.getElementById(
            "diseasePesticide"
        ).textContent =
            data.pesticide ||
            "-";


        document.getElementById(
            "diseasePrevention"
        ).textContent =
            data.prevention ||
            "-";


        document.getElementById(
            "diseaseRecommendation"
        ).textContent =
            data.recommendation ||
            "-";


        resultBox.style.display =
            "block";


        resultBox.scrollIntoView(
            {
                behavior: "smooth",
                block: "start"
            }
        );


    }
    catch(error) {

        loading.style.display =
            "none";


        button.disabled =
            false;


        showDiseaseError(
            "Server error. Please make sure Flask is running."
        );


        console.error(
            error
        );

    }

}


/* =========================================================
   DISEASE ERROR
========================================================= */

function showDiseaseError(
    message
) {

    const errorBox =
        document.getElementById(
            "diseaseError"
        );


    errorBox.textContent =
        message;


    errorBox.style.display =
        "block";

}


/* =========================================================
   DISEASE NAME FORMATTER
========================================================= */

function formatDiseaseName(
    name
) {

    if (!name) {

        return "-";

    }


    return name

        .replace(
            /__/g,
            " "
        )

        .replace(
            /___/g,
            " "
        )

        .replace(
            /_/g,
            " "
        )

        .replace(
            /\s+/g,
            " "
        )

        .trim();

}


"""

if "function detectDisease()" not in html:

    if script_marker not in html:
        raise SystemExit(
            "Could not find JavaScript initialization section."
        )

    html = html.replace(
        script_marker,
        disease_js + "\n" + script_marker,
        1
    )


# ============================================================
# 5. SAVE
# ============================================================

FILE.write_text(
    html,
    encoding="utf-8"
)


print()
print("=" * 70)
print("DISEASE DETECTOR ADDED SUCCESSFULLY")
print("=" * 70)
print()
print("Updated:")
print(FILE.resolve())
print()
print("Existing Dashboard: PRESERVED")
print("Existing Water Usage: PRESERVED")
print("Disease Detector: ADDED")
print("Separate URL: NOT CREATED")
print("=" * 70)