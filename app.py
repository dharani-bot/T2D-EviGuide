import streamlit as st
import matplotlib.pyplot as plt

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
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* GLOBAL BACKGROUND AND TEXT */

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #F0F5FA !important;
    color: #172B4D !important;
}

html, body, [class*="css"] {
    color: #172B4D;
}

[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"] {
    color: #263B53 !important;
}

/* MAIN LAYOUT */

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* HEADINGS */

h1, h2, h3, h4, h5 {
    color: #17365D !important;
    font-weight: 750 !important;
}

/* INPUT LABELS */

label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    color: #17365D !important;
    font-weight: 600 !important;
}

/* INPUT BOXES */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
    -webkit-text-fill-color: #172B4D !important;
    border: 1px solid #B8C9DC !important;
}

input::placeholder,
textarea::placeholder {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
    opacity: 1 !important;
}

/* DROPDOWNS */

div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
    border-color: #B8C9DC !important;
}

div[data-baseweb="select"] span {
    color: #172B4D !important;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background-color: #E5EDF7 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #17365D !important;
}

/* SECTION HEADINGS */

.section-title {
    background-color: #DCEAF8;
    color: #17365D !important;
    padding: 12px 16px;
    border-left: 5px solid #1976D2;
    border-radius: 8px;
    font-size: 19px;
    font-weight: 750;
    margin-top: 22px;
    margin-bottom: 14px;
}

/* BUTTONS */

.stButton button {
    border-radius: 8px;
    font-weight: 650;
}

/* TABLES */

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background-color: #FFFFFF !important;
}

/* ALERTS AND INFO BOXES */

[data-testid="stAlert"] {
    color: #17365D !important;
}

/* FOOTER */

.footer {
    background-color: #DCEAF8;
    border-top: 3px solid #1976D2;
    padding: 16px;
    border-radius: 8px;
    text-align: center;
    color: #17365D !important;
    font-size: 13px;
    margin-top: 30px;
}
/* REMOVE DARK TOP HEADER */

header[data-testid="stHeader"] {
    background: #F0F5FA !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

[data-testid="stDecoration"] {
    background: #1976D2 !important;
}

[data-testid="stAppViewContainer"] {
    background: #F0F5FA !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LEFT SIDEBAR
# ============================================================

uploaded_reports = []

with st.sidebar:

    st.title("📁 Clinical Workspace")

    st.caption("Patient documents and medication information")

    st.markdown("### 📄 Clinical Documents")

    uploaded_files = st.file_uploader(
        "Upload reports",
        type=["pdf", "docx", "txt", "csv", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="sidebar_clinical_upload",
    )

    if uploaded_files:

        for uploaded_file in uploaded_files:

            uploaded_reports.append({
                "filename": uploaded_file.name,
                "file_type": uploaded_file.type,
                "file_size": uploaded_file.size,
            })

        st.success(f"{len(uploaded_files)} document(s) added.")

        for uploaded_file in uploaded_files:
            st.caption(f"📎 {uploaded_file.name}")

    st.divider()

    st.markdown("### 📝 Clinical Notes")

    clinical_notes = st.text_area(
        "Patient observations",
        placeholder=(
            "Symptoms, clinical observations, "
            "previous diagnoses..."
        ),
        height=100,
        key="sidebar_clinical_notes",
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### 💊 Medication Information")

    medications = st.text_area(
        "Current medications",
        placeholder="Enter current medicines...",
        height=75,
        key="sidebar_current_medications",
        label_visibility="visible",
    )

    recent_medication = st.text_area(
        "Previous medications",
        placeholder="Enter previously used medicines...",
        height=75,
        key="sidebar_previous_medications",
        label_visibility="visible",
    )

    st.caption(
        "Medication information is collected for clinical review. "
        "This prototype does not independently confirm drug interactions."
    )


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div style="
    background: linear-gradient(135deg, #0D47A1, #1976D2);
    padding: 28px;
    border-radius: 14px;
    color: white;
    margin-bottom: 20px;
">
    <h1 style="color:white; margin:0;">
        🩺 T2D-EviGuide
    </h1>
    <h3 style="color:white;">
        AI-Based Early Risk Assessment of Type 2 Diabetes
    </h3>
    <p style="color:white; font-size:16px;">
        Evidence-grounded clinical decision-support prototype
        using multimodal clinical data and medical literature.
    </p>
    <p style="color:#E3F2FD; font-size:13px;">
        Research Prototype | Type 2 Diabetes | Agentic AI + RAG + Medical Evidence
    </p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Research Prototype | Type 2 Diabetes | "
    "Agentic AI + Retrieval-Augmented Generation (RAG) + Medical Evidence"
)


# ============================================================
# SECTION HEADING HELPER
# ============================================================

def section_heading(title):

    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# 1. PATIENT & DEMOGRAPHIC INFORMATION
# ============================================================

section_heading("👤 1. Patient & Demographic Information")

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
        ["Urban", "Rural", "Semi-urban"],
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    occupation = st.text_input(
        "Occupation",
        placeholder="e.g. Student, Teacher",
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
        ["Yes", "No", "Unknown"],
    )

with col4:
    family_history_cvd = st.selectbox(
        "Family History of Cardiovascular Disease",
        ["Yes", "No", "Unknown"],
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    previous_prediabetes = st.selectbox(
        "Previous Prediabetes",
        ["Yes", "No", "Unknown"],
    )

with col2:
    gestational_diabetes = st.selectbox(
        "History of Gestational Diabetes",
        ["Yes", "No", "Not applicable", "Unknown"],
    )

with col3:
    pcos_history = st.selectbox(
        "PCOS History",
        ["Yes", "No", "Unknown", "Not applicable"],
    )

with col4:
    residence_extra = st.selectbox(
        "Healthcare Access",
        ["Good", "Moderate", "Limited", "Unknown"],
    )


# ============================================================
# 2. ANTHROPOMETRIC MEASUREMENTS
# ============================================================

section_heading("⚖️ 2. Anthropometric Measurements")

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

calculated_bmi = round(
    weight / ((height / 100) ** 2),
    2,
)

st.metric(
    "Calculated BMI",
    f"{calculated_bmi:.1f} kg/m²",
)


# ============================================================
# 3. LABORATORY MEASUREMENTS
# ============================================================

section_heading("🧪 3. Laboratory Measurements")

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

section_heading("❤️ 4. Vital Signs")

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

section_heading("🏃 5. Lifestyle & Physical Activity")

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

section_heading("🥗 6. Dietary & Food Information")

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
    placeholder="Meal pattern, special diet, food restrictions...",
    height=75,
)


# ============================================================
# 7. MEDICAL HISTORY
# ============================================================

section_heading("💊 7. Medical History")

col1, col2, col3 = st.columns(3)

with col1:
    hypertension = st.selectbox(
        "Hypertension",
        ["Diagnosed", "Not diagnosed", "Unknown"],
    )

with col2:
    dyslipidemia = st.selectbox(
        "Dyslipidemia",
        ["Diagnosed", "Not diagnosed", "Unknown"],
    )

with col3:
    cardiovascular_disease = st.selectbox(
        "Cardiovascular Disease",
        ["Yes", "No", "Unknown"],
    )

col1, col2, col3 = st.columns(3)

with col1:
    kidney_disease = st.selectbox(
        "Kidney Disease",
        ["Yes", "No", "Unknown"],
    )

with col2:
    liver_disease = st.selectbox(
        "Liver Disease",
        ["Yes", "No", "Unknown"],
    )

with col3:
    other_conditions = st.selectbox(
        "Other Chronic Conditions",
        ["Yes", "No", "Unknown"],
    )

medical_history = st.text_area(
    "Additional Medical History",
    placeholder="Other relevant medical conditions or diagnoses...",
    height=75,
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

    "clinical_notes": clinical_notes,

    "healthcare_access": residence_extra,

    "family_history": family_history,
    "family_history_cvd": family_history_cvd,
    "previous_prediabetes": previous_prediabetes,
    "gestational_diabetes": gestational_diabetes,
    "pcos_history": pcos_history,

    "weight": weight,
    "height": height,
    "bmi": calculated_bmi,
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

    "uploaded_reports": uploaded_reports,
}


# ============================================================
# 8. CLINICAL DATA SUMMARY
# ============================================================

section_heading("📊 8. Clinical Data Summary")

summary_rows = [
    {"Clinical Parameter": "Age", "Patient Information": f"{age} years"},
    {"Clinical Parameter": "Sex", "Patient Information": sex},
    {"Clinical Parameter": "BMI", "Patient Information": f"{calculated_bmi:.1f} kg/m²"},
    {"Clinical Parameter": "Fasting glucose", "Patient Information": f"{fasting_glucose:.1f} mg/dL"},
    {"Clinical Parameter": "HbA1c", "Patient Information": f"{hba1c:.1f}%"},
    {"Clinical Parameter": "Blood pressure", "Patient Information": f"{systolic_bp:.0f}/{diastolic_bp:.0f} mmHg"},
    {"Clinical Parameter": "Family history", "Patient Information": family_history},
    {"Clinical Parameter": "Healthcare access", "Patient Information": residence_extra},
    {"Clinical Parameter": "Physical activity", "Patient Information": physical_activity},
    {"Clinical Parameter": "Fruit & vegetables", "Patient Information": fruit_vegetable_intake},
    {"Clinical Parameter": "Whole grains", "Patient Information": whole_grain_intake},
    {"Clinical Parameter": "Sugary drinks", "Patient Information": sugary_drinks},
    {"Clinical Parameter": "Processed foods", "Patient Information": processed_food},
    {"Clinical Parameter": "Smoking", "Patient Information": smoking},
    {"Clinical Parameter": "Alcohol", "Patient Information": alcohol},
]

st.dataframe(
    summary_rows,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# 9. VISUAL CLINICAL INDICATOR OVERVIEW
# ============================================================

section_heading("📈 9. Visual Clinical Indicator Overview")

st.caption(
    "Patient measurements compared with commonly used clinical "
    "reference thresholds. This is not an individual diabetes "
    "risk probability or validated prediction score."
)

fig, axes = plt.subplots(1, 3, figsize=(14, 3.8))

indicators = [
    ("BMI", calculated_bmi, 23, 25, "kg/m²", 40),
    ("Fasting Glucose", fasting_glucose, 100, 126, "mg/dL", 250),
    ("HbA1c", hba1c, 5.7, 6.5, "%", 12),
]

for ax, (name, value, lower, upper, unit, maximum) in zip(
    axes,
    indicators,
):

    ax.barh(
        [name],
        [value],
    )

    ax.axvline(
        lower,
        linestyle="--",
        label=f"First threshold: {lower}",
    )

    ax.axvline(
        upper,
        linestyle=":",
        label=f"Second threshold: {upper}",
    )

    ax.set_xlim(0, maximum)
    ax.set_title(f"{name}: {value:.1f} {unit}")
    ax.set_xlabel("Measured value")
    ax.legend(fontsize=7)

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)



# ============================================================
# 10. CLINICAL DATA VALIDATION
# ============================================================

section_heading("✅ 10. Clinical Data Validation")

validation_result = validate_patient_data(patient_data)

if validation_result.get("is_valid", False):

    st.success(
        "Patient data validation completed successfully."
    )

else:

    st.error(
        "Please correct the following clinical data errors:"
    )

    for error in validation_result.get("errors", []):
        st.error(error)

if validation_result.get("warnings"):

    st.warning("Validation Warnings")

    for warning in validation_result.get("warnings", []):
        st.write(f"• {warning}")

validated_bmi = validation_result.get("calculated_bmi")

if validated_bmi is not None:

    st.metric(
        "Validated BMI",
        f"{validated_bmi:.1f} kg/m²",
    )


# ============================================================
# 11. EVIDENCE-GROUNDED AI ASSESSMENT
# ============================================================

section_heading("🧠 11. Evidence-Grounded AI Assessment")

if st.button(
    "Generate Evidence-Grounded AI Assessment",
    type="primary",
    use_container_width=True,
):

    if not validation_result.get("is_valid", False):

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

                if not isinstance(result, dict):

                    st.error(
                        "The assessment module returned an unexpected result."
                    )

                elif result.get("success"):

                    assessment_text = result.get(
                        "assessment",
                        "No assessment text was returned.",
                    )

                    # --------------------------------------------
                    # AI INTERPRETATION
                    # --------------------------------------------

                    st.markdown("### 🧠 AI Clinical Interpretation")

                    with st.container(border=True):
                        st.markdown(assessment_text)

                    # --------------------------------------------
                    # GRAPHICAL CLINICAL PROFILE
                    # --------------------------------------------

                    st.markdown("### 📊 Clinical Indicator Profile")

                    st.caption(
                        "Patient values compared with clinical "
                        "reference thresholds. These charts do not "
                        "represent a calculated risk score."
                    )

                    fig, axes = plt.subplots(
                        1,
                        3,
                        figsize=(14, 4),
                    )

                    chart_data = [
                        ("BMI", calculated_bmi, 23, 25, 40, "kg/m²"),
                        ("Fasting Glucose", fasting_glucose, 100, 126, 250, "mg/dL"),
                        ("HbA1c", hba1c, 5.7, 6.5, 12, "%"),
                    ]

                    for ax, (
                        name,
                        value,
                        lower,
                        upper,
                        maximum,
                        unit,
                    ) in zip(axes, chart_data):

                        ax.barh(
                            [name],
                            [value],
                        )

                        ax.axvline(
                            lower,
                            linestyle="--",
                            label=f"Reference: {lower}",
                        )

                        ax.axvline(
                            upper,
                            linestyle=":",
                            label=f"Reference: {upper}",
                        )

                        ax.set_xlim(0, maximum)
                        ax.set_title(f"{value:.1f} {unit}")
                        ax.legend(fontsize=7)

                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)

                                       # --------------------------------------------
                    # CLINICAL RISK INDICATORS
                    # --------------------------------------------

                    st.markdown("### **Clinical Risk Indicators**")

                    risk_rows = []

                    # BMI interpretation
                    if calculated_bmi >= 25:
                        bmi_interpretation = "Obesity range (Asian Indian classification)"
                        bmi_attention = "High attention"
                    elif calculated_bmi >= 23:
                        bmi_interpretation = "Increased-risk range"
                        bmi_attention = "Review"
                    else:
                        bmi_interpretation = "Below increased-risk threshold"
                        bmi_attention = "No flag"

                    risk_rows.append({
                        "Clinical Indicator": "BMI",
                        "Patient Finding": f"{calculated_bmi:.1f} kg/m²",
                        "Interpretation": bmi_interpretation,
                        "Attention": bmi_attention
                    })

                    # Fasting glucose interpretation
                    if fasting_glucose >= 126:
                        glucose_interpretation = "Diabetes threshold reached; confirmation required"
                        glucose_attention = "High attention"
                    elif fasting_glucose >= 100:
                        glucose_interpretation = "Impaired fasting glucose range"
                        glucose_attention = "Review"
                    else:
                        glucose_interpretation = "Below impaired fasting glucose threshold"
                        glucose_attention = "No flag"

                    risk_rows.append({
                        "Clinical Indicator": "Fasting glucose",
                        "Patient Finding": f"{fasting_glucose:.1f} mg/dL",
                        "Interpretation": glucose_interpretation,
                        "Attention": glucose_attention
                    })

                    # HbA1c interpretation
                    if hba1c >= 6.5:
                        hba1c_interpretation = "Diabetes threshold reached; confirmation required"
                        hba1c_attention = "High attention"
                    elif hba1c >= 5.7:
                        hba1c_interpretation = "Prediabetes range"
                        hba1c_attention = "Review"
                    else:
                        hba1c_interpretation = "Below prediabetes threshold"
                        hba1c_attention = "No flag"

                    risk_rows.append({
                        "Clinical Indicator": "HbA1c",
                        "Patient Finding": f"{hba1c:.1f}%",
                        "Interpretation": hba1c_interpretation,
                        "Attention": hba1c_attention
                    })

                    # Additional clinical risk factors
                    additional_factors = [
                        ("Family history of diabetes", family_history),
                        ("Previous prediabetes", previous_prediabetes),
                        ("Gestational diabetes history", gestational_diabetes),
                        ("PCOS history", pcos_history),
                        ("Hypertension", hypertension),
                        ("Dyslipidemia", dyslipidemia),
                    ]

                    for factor, value in additional_factors:

                        if value in ["Yes", "Diagnosed"]:
                            interpretation = "Relevant clinical risk factor present"
                            attention = "Review"

                        elif value in ["No", "Not diagnosed", "Not applicable"]:
                            interpretation = "Not reported"
                            attention = "No flag"

                        else:
                            interpretation = "Status unknown"
                            attention = "Information needed"

                        risk_rows.append({
                            "Clinical Indicator": factor,
                            "Patient Finding": value,
                            "Interpretation": interpretation,
                            "Attention": attention
                        })

                    st.dataframe(
                        risk_rows,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.caption(
                        "Clinical thresholds are reference points, not an "
                        "individual diabetes risk score. Laboratory findings "
                        "require appropriate clinical interpretation and "
                        "confirmatory testing where indicated."
                    )

                                       # --------------------------------------------
                    # CLINICAL SAFETY REVIEW
                    # --------------------------------------------

                    st.markdown("### **Clinical Safety Review**")

                    guardrail_status = result.get(
                        "guardrail_status",
                        "NOT AVAILABLE"
                    )

                    guardrail_flags = result.get(
                        "guardrail_flags",
                        []
                    )

                    if isinstance(guardrail_flags, dict):
                        technical_flags = guardrail_flags
                    else:
                        technical_flags = {}

                        for flag in guardrail_flags:
                            if isinstance(flag, str) and ":" in flag:
                                key, value = flag.split(":", 1)
                                technical_flags[key.strip()] = value.strip()
                            else:
                                technical_flags[str(flag)] = True

                    if guardrail_status in [
                        "PASSED",
                        "NO FLAGS DETECTED"
                    ]:
                        st.success(
                            "Safety checks completed: No heuristic "
                            "safety flags detected."
                        )

                    elif technical_flags:
                        st.warning(
                            "Some safety checks require additional review."
                        )

                    else:
                        st.info(
                            "Safety verification status is unavailable. "
                            "Manual clinical review is required."
                        )

                    with st.expander("Technical Validation Details"):

                        if technical_flags:
                            st.dataframe(
                                [
                                    {
                                        "Safety Check": key.replace("_", " ").title(),
                                        "Flag Status": str(value)
                                    }
                                    for key, value in technical_flags.items()
                                ],
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.write(
                                "No individual technical flag details "
                                "were returned."
                            )

                    st.caption(
                        "These rule-based checks are preliminary safeguards. "
                        "They do not establish medical accuracy or clinical "
                        "validation."
                    )

                    # --------------------------------------------
                    # SUPPORTING MEDICAL EVIDENCE
                    # --------------------------------------------

                    evidence = result.get("evidence", [])

                    if not isinstance(evidence, list):
                        evidence = []

                    numbered_evidence = []

                    for index, item in enumerate(evidence, start=1):

                        if isinstance(item, dict):

                            numbered_item = dict(item)

                            numbered_item["evidence_number"] = (
                                item.get("evidence_number") or index
                            )

                            numbered_evidence.append(numbered_item)

                    st.markdown("### 📚 Supporting Medical Evidence")

                    if numbered_evidence:

                        st.success(
                            f"{len(numbered_evidence)} supporting "
                            "evidence item(s) retrieved."
                        )

                        evidence_table = []

                        for item in numbered_evidence:

                            evidence_table.append({
                                "Evidence": item.get("evidence_number", ""),
                                "Article Title": item.get(
                                    "title",
                                    "Title unavailable",
                                ),
                                "Article ID": item.get("article_id", ""),
                                "Source": item.get("source", ""),
                                "Year": item.get(
                                    "year",
                                    item.get("publication_year", ""),
                                ),
                                "PMID": item.get("pmid", ""),
                            })

                        st.dataframe(
                            evidence_table,
                            use_container_width=True,
                            hide_index=True,
                        )

                        for item in numbered_evidence:

                            evidence_number = item.get(
                                "evidence_number",
                                "",
                            )

                            article_id = item.get(
                                "article_id",
                                "Unknown",
                            )

                            with st.expander(
                                f"Evidence {evidence_number} — {article_id}"
                            ):

                                st.write(
                                    item.get(
                                        "title",
                                        "No title available.",
                                    )
                                )

                                st.write(
                                    item.get(
                                        "text",
                                        item.get(
                                            "document",
                                            "No evidence text available.",
                                        ),
                                    )
                                )

                                publication_year = item.get(
                                    "year",
                                    item.get("publication_year", ""),
                                )

                                if publication_year:
                                    st.caption(
                                        f"Publication year: {publication_year}"
                                    )

                                if item.get("pmid"):
                                    st.caption(
                                        f"PMID: {item['pmid']}"
                                    )

                                if item.get("doi"):
                                    st.caption(
                                        f"DOI: {item['doi']}"
                                    )

                    else:

                        st.warning(
                            "No supporting medical evidence was retrieved. "
                            "The assessment should not be treated as "
                            "evidence-supported."
                        )

                    # --------------------------------------------
                    # EVIDENCE VERIFICATION
                    # --------------------------------------------

                    st.markdown("### 🔍 Evidence Verification")

                    verification = verify_assessment(
                        assessment_text,
                        numbered_evidence,
                    )

                    status = verification.get(
                        "status",
                        "UNKNOWN",
                    )

                    references_found = verification.get(
                        "total_references_found",
                        verification.get(
                            "evidence_references_found",
                            0,
                        ),
                    )

                    verified_count = verification.get(
                        "total_verified",
                        verification.get(
                            "verified_references",
                            0,
                        ),
                    )

                    unverified_count = verification.get(
                        "total_unverified",
                        verification.get(
                            "unverified_references",
                            0,
                        ),
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "References Found",
                        references_found,
                    )

                    col2.metric(
                        "Verified",
                        verified_count,
                    )

                    col3.metric(
                        "Needs Review",
                        unverified_count,
                    )

                    if status == "VERIFIED":

                        st.success(
                            "All explicit evidence references matched "
                            "the retrieved evidence items."
                        )

                    elif status == "REVIEW REQUIRED":

                        st.warning(
                            "Evidence verification requires manual review."
                        )

                    else:

                        st.error(
                            "Evidence verification could not confirm "
                            "all references."
                        )

                    st.info(
                        verification.get(
                            "message",
                            "Evidence verification completed.",
                        )
                    )

                    st.caption(
                        "Reference matching confirms that cited evidence "
                        "identifiers correspond to retrieved evidence items. "
                        "It does not prove that a source supports every "
                        "claim or that the clinical interpretation is correct."
                    )

                else:

                    st.error(
                        "The assessment could not be generated."
                    )

                    st.warning(
                        result.get(
                            "assessment",
                            "Check API configuration, evidence retrieval "
                            "and the application terminal for details.",
                        )
                    )

            except Exception as error:

                st.error(
                    "An unexpected error occurred while generating "
                    "the assessment."
                )

                st.exception(error)


# ============================================================
# 12. MEDICATION INTERVENTION & MONITORING
# ============================================================

section_heading("💉 12. Medication Intervention & Monitoring")

medication_names = []

for medication_text in [medications, recent_medication]:

    if isinstance(medication_text, str):

        medication_names.extend([
            med.strip()
            for med in medication_text.replace("\n", ",").split(",")
            if med.strip()
        ])

# Remove duplicates while preserving order.
medication_names = list(dict.fromkeys(medication_names))

if medication_names:

    medication_status = []

    for medication in medication_names:

        if medication_text == recent_medication:
            status = "Previous medication"
        else:
            status = "Medication entered for review"

        medication_status.append({
            "Medication": medication,
            "Review Status": status,
        })

    st.dataframe(
        medication_status,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Medication information is displayed for clinical review. "
        "A verified interaction assessment requires dedicated "
        "drug-interaction evidence and patient-specific review."
    )

else:

    st.info(
        "No medication information was entered in the sidebar."
    )

st.caption(
    "This research prototype does not confirm drug interactions, "
    "recommend medication changes or provide prescribing instructions."
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        <strong>T2D-EviGuide</strong>
        <br>
        MSc Healthcare Informatics and Data Analytics
        <br><br>

        Experimental evidence-support research prototype.
        <br>
        Not clinically validated. Does not provide autonomous
        diagnosis or medication prescribing.

    </div>
    """,
    unsafe_allow_html=True,
)