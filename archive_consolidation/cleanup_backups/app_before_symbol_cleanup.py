
import streamlit as st

from clinical_validation import validate_patient_data
from clinical_assessment import generate_risk_assessment
from evidence_verifier import verify_assessment


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="T2D-EviGuide",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GENERAL APPLICATION
       ======================================================== */

    .stApp {
        background-color: #f4f8fc;
    }

    .main .block-container {
        max-width: 1400px;
        padding-top: 25px;
        padding-bottom: 40px;
    }

    /* ========================================================
       GENERAL TEXT VISIBILITY
       ======================================================== */

    .stApp p,
    .stApp span,
    .stApp div,
    .stApp label {
        color: #16324f;
    }

    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4 {
        color: #123b5d !important;
    }

    /* ========================================================
       MAIN HEADER
       ======================================================== */

    .main-header {
        background: linear-gradient(
            135deg,
            #0d47a1,
            #1976d2
        );
        padding: 28px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.10);
    }

    .main-header h1 {
        color: white !important;
        font-size: 32px;
        margin-bottom: 8px;
    }

    .main-header p {
        color: #eaf4ff !important;
        font-size: 16px;
        margin-bottom: 0;
    }

    /* ========================================================
       SECTION HEADINGS
       ======================================================== */

    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #123b5d !important;
        background: #eaf4fb;
        padding: 12px 16px;
        border-radius: 10px;
        margin-top: 22px;
        margin-bottom: 15px;
        border-left: 5px solid #1565c0;
    }

    .section-subtitle {
        color: #526575 !important;
        font-size: 14px;
        margin-bottom: 15px;
    }

    /* ========================================================
       FORM LABELS
       ======================================================== */

    .stSelectbox label,
    .stNumberInput label,
    .stTextInput label,
    .stTextArea label,
    .stFileUploader label,
    .stRadio label,
    .stCheckbox label,
    .stSlider label {
        color: #16324f !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* ========================================================
       SELECT BOXES
       ======================================================== */

    div[data-baseweb="select"] {
        color: #16324f !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #f8fbff !important;
        border-radius: 8px !important;
        border: 1px solid #c8d8e8 !important;
    }

    div[data-baseweb="select"] span {
        color: #16324f !important;
    }

    /* ========================================================
       NUMBER / TEXT INPUTS
       ======================================================== */

    .stNumberInput input,
    .stTextInput input,
    .stTextArea textarea {
        color: #16324f !important;
        background-color: #f8fbff !important;
        border-radius: 8px !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #607080 !important;
        opacity: 1 !important;
    }

    /* ========================================================
       INPUT HELP TEXT
       ======================================================== */

    .stSelectbox small,
    .stNumberInput small,
    .stTextInput small,
    .stTextArea small {
        color: #526575 !important;
    }

    /* ========================================================
       CLINICAL DOCUMENT UPLOAD
       ======================================================== */

    [data-testid="stFileUploader"] {
        width: 100% !important;
        min-height: 170px;
        padding: 16px !important;
        border: 2px dashed #4f81bd !important;
        border-radius: 16px !important;
        background: #f7fbff !important;
        box-sizing: border-box;
    }

    [data-testid="stFileUploader"] section {
        background: transparent !important;
        border: none !important;
        width: 100% !important;
    }

    [data-testid="stFileUploader"] section > div {
        width: 100% !important;
    }

    [data-testid="stFileUploader"] button {
        color: #16324f !important;
        background: white !important;
        border: 1px solid #4f81bd !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    [data-testid="stFileUploader"] * {
        color: #16324f !important;
    }

    [data-testid="stFileUploaderFileName"] {
        color: #16324f !important;
        font-weight: 600 !important;
    }

    /* ========================================================
       METRIC CARDS
       ======================================================== */

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 14px;
        border-radius: 12px;
        border: 1px solid #d9e3ee;
        box-shadow: 0 2px 7px rgba(0,0,0,0.04);
    }

    /* ========================================================
       TABLES
       ======================================================== */

    [data-testid="stTable"],
    .stDataFrame {
        color: #16324f !important;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton button {
        border-radius: 9px;
        font-weight: 600;
        padding: 8px 18px;
    }

    .stButton button p {
        color: white !important;
    }

    /* ========================================================
       SUCCESS / WARNING / ERROR
       ======================================================== */

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* ========================================================
       AI RESULT BOX
       ======================================================== */

    .ai-box {
        background: #ffffff;
        border: 1px solid #b9d7ef;
        border-left: 5px solid #1565c0;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    }

    /* ========================================================
       EVIDENCE BOX
       ======================================================== */

    .evidence-box {
        background: #f7fbff;
        border: 1px solid #c8dff2;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
    }

    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        text-align: center;
        color: #607080 !important;
        font-size: 13px;
        margin-top: 35px;
        padding-top: 15px;
        border-top: 1px solid #d9e3ee;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-header">
        <h1>🩺 T2D-EviGuide</h1>
        <p>
            AI-Based Early Risk Assessment of Type 2 Diabetes
        </p>
        <p>
            Evidence-grounded clinical decision-support prototype
            using multimodal clinical data and medical literature.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Research prototype: This system provides evidence-grounded "
    "clinical decision support. It does not provide an autonomous "
    "diagnosis or replace assessment by a qualified healthcare professional."
)


# ============================================================
# 1. PATIENT & DEMOGRAPHIC INFORMATION
# ============================================================

st.markdown(
    '<div class="section-title">👤 1. Patient & Demographic Information</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Basic demographic and background information'
    '</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=45,
        step=1,
    )

with col2:
    sex = st.selectbox(
        "Sex",
        ["Female", "Male", "Other", "Prefer not to say"],
    )

with col3:
    marital_status = st.selectbox(
        "Marital Status",
        [
            "Single",
            "Married",
            "Divorced",
            "Widowed",
            "Separated",
            "Prefer not to say",
        ],
    )

with col4:
    residence = st.selectbox(
        "Residence",
        [
            "Urban",
            "Rural",
            "Semi-urban",
        ],
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    occupation = st.text_input(
        "Occupation",
        placeholder="e.g. Student, Teacher, IT Professional",
    )

with col2:
    work_type = st.selectbox(
        "Nature of Work",
        [
            "Mostly sedentary",
            "Mixed activity",
            "Physically active",
            "Heavy physical work",
            "Not applicable",
        ],
    )

with col3:
    family_history = st.selectbox(
        "Family History of Diabetes",
        [
            "Yes",
            "No",
            "Unknown",
        ],
    )

with col4:
    family_history_cvd = st.selectbox(
        "Family History of Cardiovascular Disease",
        [
            "Yes",
            "No",
            "Unknown",
        ],
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    previous_prediabetes = st.selectbox(
        "Previous Prediabetes",
        [
            "Yes",
            "No",
            "Unknown",
        ],
    )

with col2:
    gestational_diabetes = st.selectbox(
        "History of Gestational Diabetes",
        [
            "Yes",
            "No",
            "Not applicable",
            "Unknown",
        ],
    )

with col3:
    pcos_history = st.selectbox(
        "PCOS History",
        [
            "Yes",
            "No",
            "Unknown",
            "Not applicable",
        ],
    )

with col4:
    residence_extra = st.selectbox(
        "Healthcare Access",
        [
            "Good",
            "Moderate",
            "Limited",
            "Unknown",
        ],
    )


# ============================================================
# 2. ANTHROPOMETRIC MEASUREMENTS
# ============================================================

st.markdown(
    '<div class="section-title">📏 2. Anthropometric Measurements</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    weight = st.number_input(
        "Weight (kg)",
        min_value=1.0,
        max_value=300.0,
        value=60.0,
        step=0.1,
    )

with col2:
    height = st.number_input(
        "Height (cm)",
        min_value=50.0,
        max_value=250.0,
        value=157.5,
        step=0.1,
    )

with col3:
    waist_circumference = st.number_input(
        "Waist Circumference (cm)",
        min_value=30.0,
        max_value=250.0,
        value=80.0,
        step=0.1,
    )

if height > 0:
    calculated_bmi = weight / ((height / 100) ** 2)
else:
    calculated_bmi = 0

st.metric(
    "Calculated BMI",
    f"{calculated_bmi:.1f} kg/m²",
)


# ============================================================
# 3. LABORATORY MEASUREMENTS
# ============================================================

st.markdown(
    '<div class="section-title">🧪 3. Laboratory Measurements</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    fasting_glucose = st.number_input(
        "Fasting Blood Glucose (mg/dL)",
        min_value=0.0,
        max_value=600.0,
        value=100.0,
        step=0.1,
    )

with col2:
    hba1c = st.number_input(
        "HbA1c (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.7,
        step=0.1,
    )

with col3:
    total_cholesterol = st.number_input(
        "Total Cholesterol (mg/dL)",
        min_value=0.0,
        max_value=1000.0,
        value=180.0,
        step=0.1,
    )

with col4:
    hdl = st.number_input(
        "HDL (mg/dL)",
        min_value=0.0,
        max_value=500.0,
        value=50.0,
        step=0.1,
    )

col1, col2 = st.columns(2)

with col1:
    ldl = st.number_input(
        "LDL (mg/dL)",
        min_value=0.0,
        max_value=1000.0,
        value=100.0,
        step=0.1,
    )

with col2:
    triglycerides = st.number_input(
        "Triglycerides (mg/dL)",
        min_value=0.0,
        max_value=2000.0,
        value=130.0,
        step=0.1,
    )


# ============================================================
# 4. VITAL SIGNS
# ============================================================

st.markdown(
    '<div class="section-title">❤️ 4. Vital Signs</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    systolic_bp = st.number_input(
        "Systolic Blood Pressure (mmHg)",
        min_value=50.0,
        max_value=300.0,
        value=120.0,
        step=1.0,
    )

with col2:
    diastolic_bp = st.number_input(
        "Diastolic Blood Pressure (mmHg)",
        min_value=30.0,
        max_value=200.0,
        value=80.0,
        step=1.0,
    )


# ============================================================
# 5. LIFESTYLE & PHYSICAL ACTIVITY
# ============================================================

st.markdown(
    '<div class="section-title">🏃 5. Lifestyle & Physical Activity</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    physical_activity = st.selectbox(
        "Physical Activity Frequency",
        [
            "Daily",
            "4–6 days/week",
            "2–3 days/week",
            "Less than once/week",
            "Never",
            "Unknown",
        ],
    )

with col2:
    activity_duration = st.number_input(
        "Exercise Duration (minutes/session)",
        min_value=0.0,
        max_value=600.0,
        value=30.0,
        step=5.0,
    )

with col3:
    sedentary_hours = st.number_input(
        "Sedentary Time (hours/day)",
        min_value=0.0,
        max_value=24.0,
        value=6.0,
        step=0.5,
    )

col1, col2, col3 = st.columns(3)

with col1:
    sleep_duration = st.number_input(
        "Sleep Duration (hours/day)",
        min_value=0.0,
        max_value=24.0,
        value=7.0,
        step=0.5,
    )

with col2:
    smoking = st.selectbox(
        "Smoking Status",
        [
            "Never",
            "Former smoker",
            "Current smoker",
            "Unknown",
        ],
    )

with col3:
    alcohol = st.selectbox(
        "Alcohol Consumption",
        [
            "Never",
            "Occasional",
            "Regular",
            "Unknown",
        ],
    )


# ============================================================
# 6. DIETARY & FOOD INFORMATION
# ============================================================

st.markdown(
    '<div class="section-title">🍎 6. Dietary & Food Information</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Dietary information used as part of the multimodal clinical context'
    '</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    fruit_vegetable_intake = st.selectbox(
        "Fruit & Vegetable Intake",
        [
            "≥5 servings/day",
            "3–4 servings/day",
            "1–2 servings/day",
            "Rarely",
            "Unknown",
        ],
    )

with col2:
    whole_grain_intake = st.selectbox(
        "Whole Grain Intake",
        [
            "Daily",
            "Several times/week",
            "Occasionally",
            "Rarely",
            "Never",
            "Unknown",
        ],
    )

with col3:
    sugary_drinks = st.selectbox(
        "Sugary Beverage Consumption",
        [
            "None",
            "Less than once/week",
            "1–3 times/week",
            "4–6 times/week",
            "Daily",
            "Multiple times/day",
        ],
    )

col1, col2, col3 = st.columns(3)

with col1:
    sweets_added_sugar = st.selectbox(
        "Sweets / Added Sugar",
        [
            "None",
            "Rarely",
            "1–3 times/week",
            "4–6 times/week",
            "Daily",
        ],
    )

with col2:
    fried_food = st.selectbox(
        "Fried / High-Fat Food",
        [
            "None",
            "Rarely",
            "1–3 times/week",
            "4–6 times/week",
            "Daily",
        ],
    )

with col3:
    processed_food = st.selectbox(
        "Processed / Packaged Food",
        [
            "None",
            "Rarely",
            "1–3 times/week",
            "4–6 times/week",
            "Daily",
        ],
    )

dietary_notes = st.text_area(
    "Additional Dietary Notes",
    placeholder="Optional: meal pattern, special diet, food restrictions, etc.",
)


# ============================================================
# 7. MEDICAL HISTORY & MEDICATIONS
# ============================================================

st.markdown(
    '<div class="section-title">🏥 7. Medical History & Medications</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    hypertension = st.selectbox(
        "Hypertension",
        [
            "Diagnosed",
            "Not diagnosed",
            "Unknown",
        ],
    )

with col2:
    dyslipidemia = st.selectbox(
        "Dyslipidemia",
        [
            "Diagnosed",
            "Not diagnosed",
            "Unknown",
        ],
    )

with col3:
    cardiovascular_disease = st.selectbox(
        "Cardiovascular Disease",
        [
            "Yes",
            "No",
            "Unknown",
        ],
    )

col1, col2, col3 = st.columns(3)

with col1:
    kidney_disease = st.selectbox(
        "Kidney Disease",
        [
            "Yes",
            "No",
            "Unknown",
        ],
    )

with col2:
    liver_disease = st.selectbox(
        "Liver Disease",
        [
            "Yes",
            "No",
            "Unknown",
        ],
    )

with col3:
    other_conditions = st.selectbox(
        "Other Chronic Conditions",
        [
            "Yes",
            "No",
            "Unknown",
        ],
    )

medical_history = st.text_area(
    "Additional Medical History",
    placeholder="Enter relevant medical conditions, symptoms, previous diagnoses, etc.",
)

medications = st.text_area(
    "Current Medications",
    placeholder="Enter current medications, supplements, or therapies.",
)

recent_medication = st.text_input(
    "Recently Added Medication",
    placeholder="Optional",
)

new_medication_details = st.text_area(
    "New Medication Details",
    placeholder="Optional: reason for addition, duration, etc.",
)


# ============================================================
# 8. CLINICAL DOCUMENT UPLOAD
# ============================================================

st.markdown(
    '<div class="section-title">📄 8. Clinical Document Upload</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Upload clinical reports, laboratory reports, prescriptions, '
    'or other supporting documents.'
    '</div>',
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "📎 Upload Clinical Reports",
    type=[
        "pdf",
        "docx",
        "txt",
        "jpg",
        "jpeg",
    ],
    accept_multiple_files=True,
    help="Supported formats: PDF, DOCX, TXT, JPG and JPEG",
)

uploaded_reports = []

if uploaded_files:

    for uploaded_file in uploaded_files:

        uploaded_reports.append(
            {
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "size": uploaded_file.size,
            }
        )

    st.markdown("### 📎 Uploaded Documents")

    document_rows = []

    for report in uploaded_reports:

        document_rows.append(
            {
                "File": report["name"],
                "Type": report["type"],
                "Size": f'{report["size"] / 1024:.1f} KB',
                "Status": "Uploaded",
            }
        )

    st.table(document_rows)

else:

    st.info(
        "No clinical document uploaded yet. "
        "You may continue with structured patient information."
    )


# ============================================================
# ADDITIONAL NOTES
# ============================================================

additional_notes = st.text_area(
    "📝 Additional Clinical Notes",
    placeholder=(
        "Enter any additional clinical information, symptoms, "
        "observations, or questions for the evidence assessment."
    ),
)


# ============================================================
# PATIENT DATA OBJECT
# ============================================================

patient_data = {
    "age": age,
    "sex": sex,
    "marital_status": marital_status,
    "occupation": occupation,
    "residence": residence,
    "work_type": work_type,

    "family_history": family_history,
    "family_history_cvd": family_history_cvd,
    "previous_prediabetes": previous_prediabetes,
    "gestational_diabetes": gestational_diabetes,
    "pcos_history": pcos_history,

    "weight": weight,
    "height": height,
    "waist_circumference": waist_circumference,

    "fasting_glucose": fasting_glucose,
    "hba1c": hba1c,
    "total_cholesterol": total_cholesterol,
    "hdl": hdl,
    "ldl": ldl,
    "triglycerides": triglycerides,

    "systolic_bp": systolic_bp,
    "diastolic_bp": diastolic_bp,

    "physical_activity": physical_activity,
    "activity_duration": activity_duration,
    "sedentary_hours": sedentary_hours,
    "sleep_duration": sleep_duration,
    "smoking": smoking,
    "alcohol": alcohol,

    "fruit_vegetable_intake": fruit_vegetable_intake,
    "whole_grain_intake": whole_grain_intake,
    "sugary_drinks": sugary_drinks,
    "sweets_added_sugar": sweets_added_sugar,
    "fried_food": fried_food,
    "processed_food": processed_food,
    "dietary_notes": dietary_notes,

    "hypertension": hypertension,
    "dyslipidemia": dyslipidemia,
    "cardiovascular_disease": cardiovascular_disease,
    "kidney_disease": kidney_disease,
    "liver_disease": liver_disease,
    "other_conditions": other_conditions,

    "medical_history": medical_history,
    "medications": medications,
    "recent_medication": recent_medication,
    "new_medication_details": new_medication_details,

    "additional_notes": additional_notes,

    "uploaded_reports": uploaded_reports,
}


# ============================================================
# CLINICAL DATA SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">📋 Clinical Data Summary</div>',
    unsafe_allow_html=True,
)

summary_rows = [
    {
        "Clinical Parameter": "Age",
        "Patient Information": f"{age} years",
    },
    {
        "Clinical Parameter": "Sex",
        "Patient Information": sex,
    },
    {
        "Clinical Parameter": "BMI",
        "Patient Information": f"{calculated_bmi:.1f} kg/m²",
    },
    {
        "Clinical Parameter": "Fasting glucose",
        "Patient Information": f"{fasting_glucose:.1f} mg/dL",
    },
    {
        "Clinical Parameter": "HbA1c",
        "Patient Information": f"{hba1c:.1f}%",
    },
    {
        "Clinical Parameter": "Blood pressure",
        "Patient Information": (
            f"{systolic_bp:.0f}/{diastolic_bp:.0f} mmHg"
        ),
    },
    {
        "Clinical Parameter": "Family history",
        "Patient Information": family_history,
    },
    {
        "Clinical Parameter": "Physical activity",
        "Patient Information": physical_activity,
    },
    {
        "Clinical Parameter": "Fruit & vegetables",
        "Patient Information": fruit_vegetable_intake,
    },
    {
        "Clinical Parameter": "Whole grains",
        "Patient Information": whole_grain_intake,
    },
    {
        "Clinical Parameter": "Sugary drinks",
        "Patient Information": sugary_drinks,
    },
    {
        "Clinical Parameter": "Processed foods",
        "Patient Information": processed_food,
    },
    {
        "Clinical Parameter": "Smoking",
        "Patient Information": smoking,
    },
    {
        "Clinical Parameter": "Alcohol",
        "Patient Information": alcohol,
    },
]

st.table(summary_rows)


# ============================================================
# 9. CLINICAL DATA VALIDATION
# ============================================================

st.markdown(
    '<div class="section-title">✅ 9. Clinical Data Validation</div>',
    unsafe_allow_html=True,
)

validation_result = validate_patient_data(patient_data)

if validation_result["is_valid"]:

    st.success(
        "Patient data validation completed successfully."
    )

else:

    st.error(
        "Please correct the following clinical data errors:"
    )

    for error in validation_result["errors"]:
        st.error(error)


if validation_result["warnings"]:

    st.warning("### Validation Warnings")

    for warning in validation_result["warnings"]:
        st.write(f"• {warning}")


validated_bmi = validation_result.get(
    "calculated_bmi"
)

if validated_bmi is not None:

    st.metric(
        "Validated BMI",
        f"{validated_bmi:.1f} kg/m²",
    )


# ============================================================
# 10. EVIDENCE-GROUNDED AI ASSESSMENT
# ============================================================

st.markdown(
    '<div class="section-title">🤖 10. Evidence-Grounded AI Assessment</div>',
    unsafe_allow_html=True,
)

if st.button(
    "🔬 Generate Evidence-Grounded AI Assessment",
    type="primary",
    use_container_width=True,
):

    if not validation_result["is_valid"]:

        st.error(
            "Assessment cannot be generated until "
            "the clinical data errors are corrected."
        )

    else:

        with st.spinner(
            "Retrieving medical evidence and generating assessment..."
        ):

            try:

                result = generate_risk_assessment(
                    patient_data,
                    top_k=3,
                )

                if result.get("success"):

                    st.markdown(
                        '<div class="ai-box">',
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        "### 📊 AI Clinical Assessment"
                    )

                    st.markdown(
                        result["assessment"]
                    )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True,
                    )

                    # ====================================================
                    # SUPPORTING EVIDENCE
                    # ====================================================

                    evidence = result.get(
                        "evidence",
                        []
                    )

                    st.markdown(
                        "### 📚 Supporting Medical Evidence"
                    )

                    if evidence:

                        st.write(
                            f"{len(evidence)} supporting "
                            "evidence items retrieved."
                        )

                        evidence_table = []

                        for item in evidence:

                            evidence_table.append(
                                {
                                    "Evidence": item.get(
                                        "evidence_number",
                                        ""
                                    ),
                                    "Article ID": item.get(
                                        "article_id",
                                        ""
                                    ),
                                    "Source": item.get(
                                        "source",
                                        ""
                                    ),
                                    "Year": item.get(
                                        "year",
                                        ""
                                    ),
                                    "PMID": item.get(
                                        "pmid",
                                        ""
                                    ),
                                }
                            )

                        st.table(
                            evidence_table
                        )

                        for item in evidence:

                            with st.expander(
                                f"Evidence {item.get('evidence_number')} — "
                                f"{item.get('article_id', 'Unknown')}"
                            ):

                                st.write(
                                    item.get(
                                        "title",
                                        "No title available."
                                    )
                                )

                                st.write(
                                    item.get(
                                        "text",
                                        item.get(
                                            "document",
                                            "No evidence text available."
                                        )
                                    )
                                )

                    else:

                        st.warning(
                            "No supporting evidence was retrieved."
                        )


                    # ====================================================
                    # EVIDENCE VERIFICATION
                    # ====================================================

                    st.markdown(
                        "### 🔎 Evidence Verification"
                    )

                    verification = verify_assessment(
                        result["assessment"],
                        evidence,
                    )

                    status = verification.get(
                        "status",
                        "UNKNOWN"
                    )

                    if status == "VERIFIED":

                        st.success(
                            "✅ All explicit evidence references "
                            "matched the retrieved evidence."
                        )

                    elif status == "REVIEW REQUIRED":

                        st.warning(
                            "⚠️ Evidence verification requires review."
                        )

                    else:

                        st.error(
                            "❌ Evidence verification failed."
                        )

                    verification_table = [
                        {
                            "Measure": "References found",
                            "Result": verification.get(
                                "total_references_found",
                                0
                            ),
                        },
                        {
                            "Measure": "Verified",
                            "Result": verification.get(
                                "total_verified",
                                0
                            ),
                        },
                        {
                            "Measure": "Unverified",
                            "Result": verification.get(
                                "total_unverified",
                                0
                            ),
                        },
                    ]

                    st.table(
                        verification_table
                    )

                    st.info(
                        verification.get(
                            "message",
                            ""
                        )
                    )

                else:

                    st.error(
                        "The assessment could not be generated."
                    )

                    st.error(
                        result.get(
                            "assessment",
                            "Unknown error."
                        )
                    )

            except Exception as e:

                st.error(
                    "An unexpected error occurred "
                    "while generating the assessment."
                )

                st.exception(e)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        T2D-EviGuide | MSc Health Informatics / Data Analytics
        Research Prototype
        <br><br>
        Experimental evidence-support system.
        It does not constitute clinical validation,
        autonomous diagnosis, or medication prescribing.
    </div>
    """,
    unsafe_allow_html=True,
)

