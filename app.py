
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
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM STYLE
# ============================================================

st.markdown(
    """
    <style>
    /* ================================
   FIX ALL FORM TEXT VISIBILITY
   ================================ */

/* Field labels */
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

/* All normal text inside the app */
.stApp,
.stApp p,
.stApp span,
.stApp div,
.stApp label {
    color: #16324f;
}

/* Dropdown selected text */
div[data-baseweb="select"] {
    color: #16324f !important;
}

div[data-baseweb="select"] > div {
    background-color: #f8fbff !important;
}

div[data-baseweb="select"] span {
    color: #16324f !important;
}

/* Number inputs */
.stNumberInput input {
    color: #16324f !important;
    background-color: #f8fbff !important;
}

/* Text inputs */
.stTextInput input {
    color: #16324f !important;
    background-color: #f8fbff !important;
}

/* Text areas */
.stTextArea textarea {
    color: #16324f !important;
    background-color: #f8fbff !important;
}

/* Placeholder text */
input::placeholder,
textarea::placeholder {
    color: #607080 !important;
    opacity: 1 !important;
}

/* Help text */
.stSelectbox small,
.stNumberInput small,
.stTextInput small,
.stTextArea small {
    color: #526575 !important;
}

/* Markdown headings */
.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4 {
    color: #123b5d !important;
}

/* Tables */
.stDataFrame,
[data-testid="stTable"] {
    color: #16324f !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    color: #16324f !important;
    background-color: #f8fbff !important;
}

[data-testid="stFileUploader"] * {
    color: #16324f !important;
}

/* Buttons */
.stButton button {
    color: white !important;
}

/* Captions */
.stCaption,
[data-testid="stCaptionContainer"] {
    color: #526575 !important;
}

    .stApp {
        background-color: #f4f7fb;
    }

    .block-container {
        max-width: 1350px;
        padding-top: 1rem;
    }

    /* ========================================================
       MAIN HEADER
       ======================================================== */

    .main-banner {
        background: linear-gradient(
            90deg,
            #1565c0,
            #5e35b1
        );
        padding: 24px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.10);
    }

    .main-banner h1 {
        margin: 0;
        font-size: 32px;
    }

    .main-banner p {
        margin-top: 7px;
        font-size: 15px;
    }

    /* ========================================================
       SECTION BOX
       ======================================================== */

    .section-box {
        background: #ffffff;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #d9e3ee;
        margin-bottom: 20px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    }

    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #123b5d !important;
        background: #eaf4fb;
        padding: 10px 14px;
        border-radius: 9px;
        margin-bottom: 14px;
        border-left: 5px solid #1565c0;
    }

    .section-subtitle {
        color: #607080 !important;
        font-size: 13px;
        margin-bottom: 12px;
    }

    /* ========================================================
       CLINICAL TABLE
       ======================================================== */

    .clinical-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }

    .clinical-table th {
        background-color: #eaf2f8;
        color: #16324f !important;
        padding: 10px;
        text-align: left;
        border: 1px solid #d6e1eb;
    }

    .clinical-table td {
        padding: 10px;
        border: 1px solid #d6e1eb;
        background-color: white;
        color: #16324f !important;
    }

    /* ========================================================
       RESULT BOXES
       ======================================================== */

    .risk-box {
        background: #f8fbff;
        border-left: 5px solid #1565c0;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
    }

    .evidence-box {
        background: #f7f5ff;
        border-left: 5px solid #5e35b1;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
    }

    .upload-box {
        background: #f0f8ff;
        border: 1px dashed #4a90c2;
        padding: 15px;
        border-radius: 10px;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
        min-height: 42px;
    }

    /* ========================================================
       STREAMLIT INPUT LABELS
       ======================================================== */

    label,
    .stSelectbox label,
    .stNumberInput label,
    .stTextInput label,
    .stTextArea label,
    .stFileUploader label {
        color: #16324f !important;
        font-weight: 600 !important;
    }

    /* ========================================================
       DROPDOWN TEXT
       ======================================================== */

    .stSelectbox div[data-baseweb="select"] {
        color: #16324f !important;
    }

    div[data-baseweb="select"] * {
        color: #16324f !important;
    }

    /* ========================================================
       INPUT TEXT
       ======================================================== */

    .stNumberInput input,
    .stTextInput input,
    .stTextArea textarea {
        color: #16324f !important;
    }

    /* ========================================================
       PLACEHOLDER TEXT
       ======================================================== */

    input::placeholder,
    textarea::placeholder {
        color: #607080 !important;
    }

    /* ========================================================
       INPUT BACKGROUNDS
       ======================================================== */

    div[data-baseweb="select"] > div {
        background-color: #f8fbff !important;
        border-radius: 8px !important;
    }

    .stNumberInput input,
    .stTextInput input,
    .stTextArea textarea {
        background-color: #f8fbff !important;
        border-radius: 8px !important;
    }

    /* ========================================================
       METRICS
       ======================================================== */

    div[data-testid="stMetric"] {
        background-color: #f4f8fc;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #d9e3ee;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "validation_result" not in st.session_state:
    st.session_state.validation_result = None

if "assessment_result" not in st.session_state:
    st.session_state.assessment_result = None

if "verification_result" not in st.session_state:
    st.session_state.verification_result = None

if "patient_data" not in st.session_state:
    st.session_state.patient_data = None


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-banner">
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
    unsafe_allow_html=True
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
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">👤 1. Patient & Demographic Information</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Basic demographic and background information'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    age = st.number_input(
        "Age (years)",
        min_value=1,
        max_value=120,
        value=45
    )

with col2:
    sex = st.selectbox(
        "Sex",
        [
            "Female",
            "Male",
            "Other",
            "Unknown"
        ]
    )

with col3:
    marital_status = st.selectbox(
        "Marital Status",
        [
            "Single",
            "Married",
            "Widowed",
            "Divorced",
            "Other",
            "Unknown"
        ]
    )

with col4:
    residence = st.selectbox(
        "Residence",
        [
            "Urban",
            "Rural",
            "Semi-urban",
            "Unknown"
        ]
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    occupation = st.text_input(
        "Occupation",
        placeholder="Example: Student, Teacher, Software Engineer"
    )

with col2:
    nature_of_work = st.selectbox(
        "Nature of Work",
        [
            "Mostly sedentary",
            "Light physical activity",
            "Moderate physical activity",
            "Heavy physical activity",
            "Unknown"
        ]
    )

with col3:
    family_history = st.selectbox(
        "Family History of Diabetes",
        [
            "Yes",
            "No",
            "Unknown"
        ]
    )

with col4:
    family_history_cvd = st.selectbox(
        "Family History of CVD",
        [
            "Yes",
            "No",
            "Unknown"
        ]
    )

col1, col2 = st.columns(2)

with col1:
    previous_prediabetes = st.selectbox(
        "Previous Prediabetes",
        [
            "Yes",
            "No",
            "Unknown"
        ]
    )

with col2:
    gestational_diabetes = st.selectbox(
        "History of Gestational Diabetes",
        [
            "Yes",
            "No",
            "Not applicable",
            "Unknown"
        ]
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# 2. ANTHROPOMETRIC MEASUREMENTS
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">📏 2. Anthropometric Measurements</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    weight = st.number_input(
        "Weight (kg)",
        min_value=1.0,
        max_value=300.0,
        value=62.0,
        step=0.1
    )

with col2:
    height = st.number_input(
        "Height (cm)",
        min_value=50.0,
        max_value=250.0,
        value=160.0,
        step=0.1
    )

with col3:
    waist_circumference = st.number_input(
        "Waist Circumference (cm)",
        min_value=30.0,
        max_value=250.0,
        value=80.0,
        step=0.5
    )

with col4:
    if height > 0:
        bmi = weight / ((height / 100) ** 2)
    else:
        bmi = 0

    st.metric(
        "Calculated BMI",
        f"{bmi:.1f} kg/m²"
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# 3. LABORATORY MEASUREMENTS
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">🧪 3. Laboratory Measurements</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    fasting_glucose = st.number_input(
        "Fasting Blood Glucose (mg/dL)",
        min_value=0.0,
        max_value=600.0,
        value=100.0,
        step=0.1
    )

with col2:
    hba1c = st.number_input(
        "HbA1c (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.7,
        step=0.1
    )

with col3:
    total_cholesterol = st.number_input(
        "Total Cholesterol (mg/dL)",
        min_value=0.0,
        max_value=1000.0,
        value=180.0,
        step=1.0
    )

col1, col2, col3 = st.columns(3)

with col1:
    hdl = st.number_input(
        "HDL Cholesterol (mg/dL)",
        min_value=0.0,
        max_value=500.0,
        value=50.0,
        step=1.0
    )

with col2:
    ldl = st.number_input(
        "LDL Cholesterol (mg/dL)",
        min_value=0.0,
        max_value=1000.0,
        value=100.0,
        step=1.0
    )

with col3:
    triglycerides = st.number_input(
        "Triglycerides (mg/dL)",
        min_value=0.0,
        max_value=2000.0,
        value=130.0,
        step=1.0
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# 4. VITAL SIGNS
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">❤️ 4. Vital Signs</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    systolic_bp = st.number_input(
        "Systolic Blood Pressure (mmHg)",
        min_value=50.0,
        max_value=300.0,
        value=120.0,
        step=1.0
    )

with col2:
    diastolic_bp = st.number_input(
        "Diastolic Blood Pressure (mmHg)",
        min_value=30.0,
        max_value=200.0,
        value=80.0,
        step=1.0
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# 5. LIFESTYLE & PHYSICAL ACTIVITY
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">🏃 5. Lifestyle & Physical Activity</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    physical_activity = st.selectbox(
        "Physical Activity Frequency",
        [
            "Daily",
            "4–6 days/week",
            "2–3 days/week",
            "Once/week",
            "Rarely",
            "Never",
            "Unknown"
        ]
    )

with col2:
    activity_duration = st.number_input(
        "Activity Duration / Session (minutes)",
        min_value=0.0,
        max_value=600.0,
        value=30.0,
        step=5.0
    )

with col3:
    sedentary_hours = st.number_input(
        "Sedentary Time (hours/day)",
        min_value=0.0,
        max_value=24.0,
        value=6.0,
        step=0.5
    )

col1, col2, col3 = st.columns(3)

with col1:
    sleep_duration = st.number_input(
        "Sleep Duration (hours/day)",
        min_value=0.0,
        max_value=24.0,
        value=7.0,
        step=0.5
    )

with col2:
    smoking = st.selectbox(
        "Smoking Status",
        [
            "Never",
            "Former",
            "Current daily",
            "Current occasional",
            "Unknown"
        ]
    )

with col3:
    alcohol = st.selectbox(
        "Alcohol Consumption",
        [
            "Never",
            "Former",
            "Occasional",
            "Weekly",
            "Several times/week",
            "Daily",
            "Unknown"
        ]
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# 6. DIETARY INFORMATION
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">🍎 6. Dietary & Food Information</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Dietary information used as part of the multimodal clinical context'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    fruit_vegetable_intake = st.selectbox(
        "🍎 Fruit & Vegetable Intake",
        [
            "≥5 servings/day",
            "3–4 servings/day",
            "1–2 servings/day",
            "Rarely",
            "Unknown"
        ]
    )

with col2:
    whole_grain_intake = st.selectbox(
        "🌾 Whole Grain Intake",
        [
            "Daily",
            "4–6 days/week",
            "2–3 days/week",
            "Rarely",
            "Never",
            "Unknown"
        ]
    )

col1, col2 = st.columns(2)

with col1:
    sugary_drinks = st.selectbox(
        "🥤 Sugary Beverage Consumption",
        [
            "None",
            "<1/week",
            "1–3/week",
            "4–6/week",
            "Daily",
            "Multiple/day",
            "Unknown"
        ]
    )

with col2:
    sweets_added_sugar = st.selectbox(
        "🍬 Sweets & Added Sugar",
        [
            "Rarely",
            "1–2/week",
            "3–6/week",
            "Daily",
            "Multiple/day",
            "Unknown"
        ]
    )

col1, col2 = st.columns(2)

with col1:
    fried_food = st.selectbox(
        "🍟 Fried / High-Fat Foods",
        [
            "Rarely",
            "1–2/week",
            "3–6/week",
            "Daily",
            "Multiple/day",
            "Unknown"
        ]
    )

with col2:
    processed_food = st.selectbox(
        "📦 Processed / Packaged Foods",
        [
            "Rarely",
            "Occasionally",
            "Frequently",
            "Daily",
            "Multiple/day",
            "Unknown"
        ]
    )

dietary_notes = st.text_area(
    "📝 Additional Dietary Notes",
    placeholder=(
        "Example: Vegetarian/non-vegetarian, meal pattern, "
        "frequent restaurant food, traditional foods, "
        "special diet, food preferences, etc."
    ),
    height=100
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# 7. MEDICAL HISTORY & MEDICATIONS
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">🏥 7. Medical History & Medications</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    hypertension = st.selectbox(
        "Hypertension",
        [
            "Diagnosed",
            "Not diagnosed",
            "Unknown"
        ]
    )

    dyslipidemia = st.selectbox(
        "Dyslipidemia",
        [
            "Diagnosed",
            "Not diagnosed",
            "Unknown"
        ]
    )

    cardiovascular_disease = st.selectbox(
        "Cardiovascular Disease",
        [
            "Yes",
            "No",
            "Unknown"
        ]
    )

    kidney_disease = st.selectbox(
        "Kidney Disease",
        [
            "Yes",
            "No",
            "Unknown"
        ]
    )

with col2:

    liver_disease = st.selectbox(
        "Liver Disease",
        [
            "Yes",
            "No",
            "Unknown"
        ]
    )

    pcos = st.selectbox(
        "PCOS",
        [
            "Yes",
            "No",
            "Not applicable",
            "Unknown"
        ]
    )

    medical_history = st.text_area(
        "Other Medical History",
        placeholder=(
            "Previous medical conditions, surgeries, "
            "hospitalizations, etc."
        ),
        height=120
    )

    medications = st.text_area(
        "Current Medications",
        placeholder=(
            "Example: List current medicines and recently "
            "added medicines."
        ),
        height=120
    )

recent_medication_added = st.selectbox(
    "Recent Medication Added",
    [
        "Yes",
        "No",
        "Unknown"
    ]
)

new_medication_details = st.text_area(
    "New Medication Details",
    placeholder=(
        "If a new medicine was recently added, "
        "enter the medicine name and relevant details."
    ),
    height=80
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# 8. CLINICAL DOCUMENT UPLOAD
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">📄 8. Clinical Document Upload</div>',
    unsafe_allow_html=True
)

upload_col1, upload_col2 = st.columns([2, 1])

with upload_col1:

    uploaded_reports = st.file_uploader(
        "Upload Medical / Laboratory Reports",
        type=[
            "pdf",
            "docx",
            "txt"
        ],
        accept_multiple_files=True,
        help=(
            "Upload relevant clinical reports or "
            "laboratory documents."
        )
    )

with upload_col2:

    st.info(
        "Supported formats:\n\n"
        "📄 PDF\n\n"
        "📝 DOCX\n\n"
        "📃 TXT\n\n"
        "Multiple documents can be uploaded."
    )

if uploaded_reports:

    st.markdown("### 📎 Uploaded Documents")

    document_rows = []

    for report in uploaded_reports:

        document_rows.append(
            {
                "File": report.name,
                "Type": report.type or "Unknown",
                "Status": "Uploaded"
            }
        )

    st.table(document_rows)

else:

    st.caption(
        "No clinical documents uploaded."
    )

additional_notes = st.text_area(
    "📝 Additional Clinical Notes",
    placeholder=(
        "Enter any additional information relevant "
        "to the clinical assessment."
    ),
    height=100
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# BUILD PATIENT DATA
# ============================================================

patient_data = {

    "age": age,
    "sex": sex,
    "marital_status": marital_status,
    "occupation": occupation,
    "nature_of_work": nature_of_work,
    "residence": residence,

    "family_history": family_history,
    "family_history_cvd": family_history_cvd,
    "previous_prediabetes": previous_prediabetes,
    "gestational_diabetes": gestational_diabetes,

    "weight": weight,
    "height": height,
    "bmi": bmi,
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
    "pcos": pcos,

    "medical_history": medical_history,
    "medications": medications,
    "recent_medication_added": recent_medication_added,
    "new_medication_details": new_medication_details,

    "uploaded_reports": uploaded_reports,
    "additional_notes": additional_notes
}


# ============================================================
# PATIENT DATA SUMMARY TABLE
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">📋 Clinical Data Summary</div>',
    unsafe_allow_html=True
)

summary_rows = [

    ["Age", f"{age} years"],
    ["Sex", sex],
    ["BMI", f"{bmi:.1f} kg/m²"],

    ["Fasting glucose", f"{fasting_glucose} mg/dL"],
    ["HbA1c", f"{hba1c}%"],

    [
        "Blood pressure",
        f"{systolic_bp}/{diastolic_bp} mmHg"
    ],

    ["Family history", family_history],
    ["Physical activity", physical_activity],

    [
        "Fruit & vegetables",
        fruit_vegetable_intake
    ],

    [
        "Whole grains",
        whole_grain_intake
    ],

    [
        "Sugary drinks",
        sugary_drinks
    ],

    [
        "Processed foods",
        processed_food
    ],

    ["Smoking", smoking],
    ["Alcohol", alcohol]

]

st.table(
    {
        "Clinical Parameter": [
            row[0] for row in summary_rows
        ],

        "Patient Information": [
            row[1] for row in summary_rows
        ]
    }
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# 9. CLINICAL DATA VALIDATION
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">✅ 9. Clinical Data Validation</div>',
    unsafe_allow_html=True
)

if st.button(
    "Validate Patient Data",
    type="secondary",
    use_container_width=True
):

    validation_result = validate_patient_data(
        patient_data
    )

    st.session_state.validation_result = (
        validation_result
    )

    st.session_state.patient_data = (
        patient_data
    )

    st.session_state.assessment_result = None
    st.session_state.verification_result = None


validation_result = (
    st.session_state.validation_result
)


if validation_result is not None:

    if validation_result["is_valid"]:

        st.success(
            "Patient data validation completed successfully."
        )

    else:

        st.error(
            "Patient data contains errors. "
            "Please correct them before assessment."
        )

    if validation_result["errors"]:

        st.subheader("Validation Errors")

        for error in validation_result["errors"]:

            st.error(error)

    if validation_result["warnings"]:

        st.subheader("Validation Warnings")

        for warning in validation_result["warnings"]:

            st.warning(warning)

    if validation_result["calculated_bmi"] is not None:

        st.metric(
            "Validated BMI",
            f"{validation_result['calculated_bmi']:.1f} kg/m²"
        )


st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# 10. AI RISK ASSESSMENT
# ============================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">🤖 10. Evidence-Grounded AI Assessment</div>',
    unsafe_allow_html=True
)


if (
    validation_result is not None
    and validation_result["is_valid"]
):

    if st.button(
        "Generate Evidence-Grounded Assessment",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Retrieving medical evidence and generating assessment..."
        ):

            try:

                assessment_result = generate_risk_assessment(
                    patient_data,
                    top_k=3
                )

                st.session_state.assessment_result = (
                    assessment_result
                )

                st.session_state.verification_result = None

            except Exception as error:

                st.session_state.assessment_result = {

                    "success": False,

                    "assessment": str(error),

                    "evidence": []

                }

                st.session_state.verification_result = None

else:

    st.info(
        "Validate the patient data first to enable "
        "the evidence-grounded assessment."
    )


st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# DISPLAY AI ASSESSMENT
# ============================================================

assessment_result = (
    st.session_state.assessment_result
)


if assessment_result is not None:

    st.markdown(
        '<div class="section-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">📊 AI Clinical Assessment</div>',
        unsafe_allow_html=True
    )


    if assessment_result.get(
        "success",
        False
    ):

        assessment_text = assessment_result.get(
            "assessment",
            ""
        )


        if assessment_text:

            st.markdown(
                """
                <div class="risk-box">
                <b>Evidence-Grounded Assessment</b>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                assessment_text
            )

        else:

            st.warning(
                "The assessment returned no text."
            )


        # ====================================================
        # STRUCTURED PATIENT ASSESSMENT TABLE
        # ====================================================

        st.subheader(
            "📋 Patient Clinical Assessment Table"
        )

        assessment_table = {

            "Domain": [

                "Demographics",
                "Anthropometrics",
                "Glycemic measurements",
                "Blood pressure",
                "Lipid profile",
                "Physical activity",
                "Dietary pattern",
                "Smoking",
                "Alcohol",
                "Medical history",
                "Medications",
                "Clinical documents"

            ],

            "Patient Information": [

                f"{age} years | "
                f"{sex} | "
                f"{occupation or 'Not provided'}",

                f"BMI {bmi:.1f} kg/m² | "
                f"Waist {waist_circumference:.1f} cm",

                f"Fasting glucose {fasting_glucose} mg/dL | "
                f"HbA1c {hba1c}%",

                f"{systolic_bp}/{diastolic_bp} mmHg",

                f"TC {total_cholesterol} | "
                f"HDL {hdl} | "
                f"LDL {ldl} | "
                f"TG {triglycerides}",

                f"{physical_activity} | "
                f"{activity_duration} min/session | "
                f"{sedentary_hours} h sedentary/day",

                f"Fruit/vegetables: "
                f"{fruit_vegetable_intake}; "
                f"Whole grains: "
                f"{whole_grain_intake}; "
                f"Sugary drinks: "
                f"{sugary_drinks}; "
                f"Processed food: "
                f"{processed_food}",

                smoking,

                alcohol,

                medical_history or "Not provided",

                medications or "Not provided",

                f"{len(uploaded_reports)} document(s)"

            ]

        }

        st.table(
            assessment_table
        )


        # ====================================================
        # SUPPORTING EVIDENCE
        # ====================================================

        st.divider()

        st.subheader(
            "📚 Supporting Medical Evidence"
        )

        evidence = assessment_result.get(
            "evidence",
            []
        )


        if evidence:

            st.success(
                f"{len(evidence)} supporting evidence "
                f"items retrieved."
            )

            evidence_table = []


            for index, item in enumerate(evidence):

                evidence_table.append(
                    {
                        "Evidence": item.get(
                            "evidence_number",
                            index + 1
                        ),

                        "Article ID": item.get(
                            "article_id",
                            "N/A"
                        ),

                        "Source": item.get(
                            "source",
                            "N/A"
                        ),

                        "Year": item.get(
                            "year",
                            "N/A"
                        ),

                        "PMID": item.get(
                            "pmid",
                            "N/A"
                        )
                    }
                )


            st.table(
                evidence_table
            )


            for index, item in enumerate(evidence):

                evidence_number = item.get(
                    "evidence_number",
                    index + 1
                )

                title = item.get(
                    "title",
                    "Medical Evidence"
                )


                with st.expander(
                    f"Evidence {evidence_number}: {title}"
                ):

                    st.write(
                        f"**Article ID:** "
                        f"{item.get('article_id', 'N/A')}"
                    )

                    st.write(
                        f"**Source:** "
                        f"{item.get('source', 'N/A')}"
                    )

                    st.write(
                        f"**Year:** "
                        f"{item.get('year', 'N/A')}"
                    )

                    st.write(
                        f"**PMID:** "
                        f"{item.get('pmid', 'N/A')}"
                    )

                    st.write(
                        f"**DOI:** "
                        f"{item.get('doi', 'N/A')}"
                    )

                    st.markdown(
                        "**Retrieved Evidence:**"
                    )

                    st.write(
                        item.get(
                            "text",
                            item.get(
                                "document",
                                ""
                            )
                        )
                    )

        else:

            st.warning(
                "No supporting evidence was returned."
            )


        # ====================================================
        # EVIDENCE VERIFICATION
        # ====================================================

        st.divider()

        st.subheader(
            "🔎 Evidence Verification"
        )


        if evidence:

            if st.button(
                "Verify Assessment Against Evidence",
                type="secondary"
            ):

                with st.spinner(
                    "Checking assessment against retrieved evidence..."
                ):

                    try:

                        verification = verify_assessment(
                            assessment_result[
                                "assessment"
                            ],
                            evidence
                        )

                        st.session_state.verification_result = (
                            verification
                        )

                    except Exception as error:

                        st.session_state.verification_result = (
                            f"Verification failed: {error}"
                        )


            verification_result = (
                st.session_state.verification_result
            )


            if verification_result is not None:

                st.markdown(
                    "### Verification Result"
                )


                if isinstance(
                    verification_result,
                    str
                ):

                    st.error(
                        verification_result
                    )

                else:

                    status = verification_result.get(
                        "status",
                        "REVIEW REQUIRED"
                    )


                    if status == "VERIFIED":

                        st.success(
                            "✅ Evidence references verified."
                        )

                    else:

                        st.warning(
                            f"⚠️ {status}"
                        )


                    verification_table = {

                        "Measure": [

                            "References found",
                            "Verified",
                            "Unverified"

                        ],

                        "Result": [

                            verification_result.get(
                                "total_references_found",
                                0
                            ),

                            verification_result.get(
                                "total_verified",
                                0
                            ),

                            verification_result.get(
                                "total_unverified",
                                0
                            )

                        ]

                    }


                    st.table(
                        verification_table
                    )


                    st.write(
                        verification_result.get(
                            "message",
                            ""
                        )
                    )


            else:

                st.caption(
                    "Click the verification button to "
                    "run the evidence-support check."
                )

        else:

            st.info(
                "Evidence verification is unavailable "
                "because no evidence objects were returned."
            )


        # ====================================================
        # DISCLAIMER
        # ====================================================

        st.divider()

        st.info(
            "This is an experimental evidence-support check "
            "for a research prototype. It does not constitute "
            "clinical validation, autonomous diagnosis, "
            "or medication prescribing."
        )


    else:

        st.error(
            "The assessment could not be generated."
        )

        st.write(
            assessment_result.get(
                "assessment",
                "Unknown error."
            )
        )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "T2D-EviGuide | MSc Health Informatics / "
    "Data Analytics Research Prototype"
)
