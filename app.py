import streamlit as st
import pandas as pd

from clinical_validation import validate_patient_data
from clinical_assessment import run_clinical_assessment
from evidence_verifier import verify_assessment
from uploaded_file_processor import extract_patient_data


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
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    .section-card {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        background-color: rgba(255,255,255,0.02);
    }

    .status-card {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        text-align: center;
    }

    .small-note {
        color: #6b7280;
        font-size: 0.85rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "uploaded_file_name": None,
    "uploaded_patient_data": None,
    "file_extracted_text": None,
    "file_applied": False,
    "validation_result": None,
    "assessment_result": None,
    "verification_result": None,
    "patient_data": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🩺 T2D-EviGuide</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Evidence-Grounded AI for Early Risk Assessment of
    Type 2 Diabetes Using Multimodal Clinical Data
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    """
    **Research prototype:** T2D-EviGuide combines structured
    clinical information, retrieved medical evidence, and
    language-model synthesis to support early Type 2 diabetes
    risk interpretation. It does not provide an autonomous
    diagnosis and does not replace assessment by a qualified
    healthcare professional.
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🧭 Workflow")

    st.markdown(
        """
        **1. Import data**  
        Upload an optional clinical file.

        **2. Review & edit**  
        Extracted information is placed into the same
        clinical form for human review.

        **3. Validate**  
        Check completeness and data quality.

        **4. Assess**  
        Retrieve supporting medical evidence and
        generate an evidence-grounded interpretation.

        **5. Verify**  
        Check important generated claims against
        the retrieved evidence.
        """
    )

    st.divider()

    st.caption(
        "T2D-EviGuide\n"
        "MSc Health Informatics / Data Analytics"
    )


# ============================================================
# 1. OPTIONAL FILE IMPORT
# ============================================================

st.header("1. Import Clinical Data")

st.write(
    "Optionally upload a clinical document or structured "
    "clinical-data file. Extracted values will be used to "
    "pre-fill the clinical form below."
)

uploaded_file = st.file_uploader(
    "Upload Clinical File",
    type=["pdf", "txt", "csv", "xlsx"],
    help=(
        "Supported formats: PDF, TXT, CSV and XLSX. "
        "Extracted values must be reviewed before assessment."
    ),
)


# ============================================================
# PROCESS NEW FILE
# ============================================================

if uploaded_file is not None:

    new_file = (
        st.session_state.uploaded_file_name
        != uploaded_file.name
    )

    if new_file:

        try:

            with st.spinner(
                "Extracting clinical information..."
            ):

                (
                    extracted_patient_data,
                    extracted_text,
                ) = extract_patient_data(
                    uploaded_file
                )

            st.session_state.uploaded_file_name = (
                uploaded_file.name
            )

            st.session_state.uploaded_patient_data = (
                extracted_patient_data
            )

            st.session_state.file_extracted_text = (
                extracted_text
            )

            st.session_state.file_applied = False

            st.session_state.validation_result = None
            st.session_state.assessment_result = None
            st.session_state.verification_result = None

            st.success(
                "Clinical information extracted successfully."
            )

        except Exception as error:

            st.error(
                "The uploaded clinical file could not be processed."
            )

            st.exception(error)


# ============================================================
# EXTRACTED DATA PREVIEW
# ============================================================

if st.session_state.uploaded_patient_data is not None:

    extracted_data = (
        st.session_state.uploaded_patient_data
    )

    st.subheader("📄 Extracted Information")

    st.warning(
        "Review the extracted information against the original "
        "clinical document. Extraction may contain errors or "
        "may leave some fields unavailable."
    )

    st.caption(
        f"Uploaded file: "
        f"{st.session_state.uploaded_file_name}"
    )

    preview_rows = []

    for field, value in extracted_data.items():

        if field == "dietary_intake":
            continue

        preview_rows.append(
            {
                "Clinical Field": field.replace(
                    "_",
                    " "
                ).title(),
                "Extracted Value": (
                    "Not available"
                    if value is None
                    else str(value)
                ),
            }
        )

    if preview_rows:

        st.dataframe(
            pd.DataFrame(preview_rows),
            use_container_width=True,
            hide_index=True,
        )

    if st.button(
        "⬇️ Apply Extracted Values to Clinical Form",
        type="primary",
        key="apply_extracted_values",
    ):

        st.session_state.file_applied = True

        st.success(
            "Extracted values have been applied to the "
            "clinical form. Please review and edit them below."
        )

    with st.expander("View Original Extracted Text"):

        st.text(
            st.session_state.file_extracted_text
            or "No text was extracted."
        )


# ============================================================
# HELPER: GET EXTRACTED VALUE
# ============================================================

def extracted_value(field, default=None):

    if (
        st.session_state.file_applied
        and st.session_state.uploaded_patient_data
        is not None
    ):

        value = st.session_state.uploaded_patient_data.get(
            field
        )

        if value is not None:
            return value

    return default


# ============================================================
# 2. PATIENT INFORMATION
# ============================================================

st.header("2. Patient Information")

with st.container(border=True):

    col1, col2, col3 = st.columns(3)

    with col1:

        default_age = extracted_value(
            "age",
            45,
        )

        age = st.number_input(
            "Age (years)",
            min_value=1,
            max_value=120,
            value=int(default_age),
            step=1,
            key="form_age",
        )

    with col2:

        sex_options = [
            "Female",
            "Male",
            "Other",
            "Unknown",
        ]

        default_sex = extracted_value(
            "sex",
            "Unknown",
        )

        if default_sex not in sex_options:
            default_sex = "Unknown"

        sex = st.selectbox(
            "Sex",
            sex_options,
            index=sex_options.index(
                default_sex
            ),
            key="form_sex",
        )

    with col3:

        family_options = [
            "Yes",
            "No",
            "Unknown",
        ]

        default_family = extracted_value(
            "family_history",
            "Unknown",
        )

        if default_family not in family_options:
            default_family = "Unknown"

        family_history = st.selectbox(
            "Family history of diabetes",
            family_options,
            index=family_options.index(
                default_family
            ),
            key="form_family_history",
        )


# ============================================================
# 3. ANTHROPOMETRIC MEASUREMENTS
# ============================================================

st.header("3. Anthropometric Measurements")

with st.container(border=True):

    col1, col2, col3 = st.columns(3)

    with col1:

        default_weight = extracted_value(
            "weight",
            62.0,
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=1.0,
            max_value=300.0,
            value=float(default_weight),
            step=0.1,
            key="form_weight",
        )

    with col2:

        default_height = extracted_value(
            "height",
            160.0,
        )

        height = st.number_input(
            "Height (cm)",
            min_value=50.0,
            max_value=250.0,
            value=float(default_height),
            step=0.1,
            key="form_height",
        )

    with col3:

        if height > 0:

            bmi = round(
                weight /
                ((height / 100) ** 2),
                1,
            )

        else:

            bmi = 0.0

        st.metric(
            "Calculated BMI",
            f"{bmi:.1f} kg/m²",
        )


# ============================================================
# 4. LABORATORY MEASUREMENTS
# ============================================================

st.header("4. Laboratory Measurements")

with st.container(border=True):

    col1, col2, col3 = st.columns(3)

    with col1:

        default_glucose = extracted_value(
            "blood_glucose",
            None,
        )

        blood_glucose = st.number_input(
            "Blood Glucose (mg/dL)",
            min_value=0.0,
            max_value=600.0,
            value=(
                float(default_glucose)
                if default_glucose is not None
                else 0.0
            ),
            step=0.1,
            key="form_blood_glucose",
        )

    with col2:

        fasting_options = [
            "Fasting",
            "Random",
            "Non-fasting",
            "2-hour OGTT",
            "Unknown",
        ]

        default_fasting = extracted_value(
            "fasting_status",
            "Unknown",
        )

        if default_fasting not in fasting_options:
            default_fasting = "Unknown"

        fasting_status = st.selectbox(
            "Glucose Measurement Status",
            fasting_options,
            index=fasting_options.index(
                default_fasting
            ),
            key="form_fasting_status",
        )

    with col3:

        default_hba1c = extracted_value(
            "hba1c",
            None,
        )

        hba1c = st.number_input(
            "HbA1c (%)",
            min_value=0.0,
            max_value=20.0,
            value=(
                float(default_hba1c)
                if default_hba1c is not None
                else 0.0
            ),
            step=0.1,
            key="form_hba1c",
        )

    default_cholesterol = extracted_value(
        "total_cholesterol",
        None,
    )

    total_cholesterol = st.number_input(
        "Total Cholesterol (mg/dL)",
        min_value=0.0,
        max_value=1000.0,
        value=(
            float(default_cholesterol)
            if default_cholesterol is not None
            else 0.0
        ),
        step=1.0,
        key="form_total_cholesterol",
    )

    st.caption(
        "Measurement status is retained because fasting glucose, "
        "random glucose and 2-hour OGTT glucose are distinct "
        "clinical measurements."
    )


# ============================================================
# 5. VITAL SIGNS
# ============================================================

st.header("5. Vital Signs")

with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1:

        default_sbp = extracted_value(
            "systolic_bp",
            120.0,
        )

        systolic_bp = st.number_input(
            "Systolic Blood Pressure (mmHg)",
            min_value=50.0,
            max_value=300.0,
            value=float(default_sbp),
            step=1.0,
            key="form_systolic_bp",
        )

    with col2:

        default_dbp = extracted_value(
            "diastolic_bp",
            80.0,
        )

        diastolic_bp = st.number_input(
            "Diastolic Blood Pressure (mmHg)",
            min_value=30.0,
            max_value=200.0,
            value=float(default_dbp),
            step=1.0,
            key="form_diastolic_bp",
        )


# ============================================================
# 6. LIFESTYLE
# ============================================================

st.header("6. Lifestyle Information")

with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1:

        activity_options = [
            "Low",
            "Moderate",
            "High",
            "Unknown",
        ]

        default_activity = extracted_value(
            "physical_activity",
            "Unknown",
        )

        if default_activity not in activity_options:
            default_activity = "Unknown"

        physical_activity = st.selectbox(
            "Physical Activity",
            activity_options,
            index=activity_options.index(
                default_activity
            ),
            key="form_physical_activity",
        )

    with col2:

        smoking_options = [
            "Never",
            "Former",
            "Current",
            "Unknown",
        ]

        default_smoking = extracted_value(
            "smoking",
            "Unknown",
        )

        if default_smoking not in smoking_options:
            default_smoking = "Unknown"

        smoking = st.selectbox(
            "Smoking Status",
            smoking_options,
            index=smoking_options.index(
                default_smoking
            ),
            key="form_smoking",
        )


# ============================================================
# 7. DIETARY INTAKE
# ============================================================

st.header("7. Dietary Intake")

existing_diet = {}

if (
    st.session_state.file_applied
    and st.session_state.uploaded_patient_data
    is not None
):

    existing_diet = (
        st.session_state.uploaded_patient_data.get(
            "dietary_intake",
            {}
        )
        or {}
    )

with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1:

        meal_options = [
            "Regular",
            "Irregular",
            "Unknown",
        ]

        default_meal = existing_diet.get(
            "meal_pattern",
            "Unknown",
        )

        if default_meal not in meal_options:
            default_meal = "Unknown"

        meal_pattern = st.selectbox(
            "Meal Pattern",
            meal_options,
            index=meal_options.index(
                default_meal
            ),
            key="form_meal_pattern",
        )

    with col2:

        intake_options = [
            "Low",
            "Moderate",
            "High",
            "Unknown",
        ]

        default_fruit = existing_diet.get(
            "fruit_vegetable_intake",
            "Unknown",
        )

        if default_fruit not in intake_options:
            default_fruit = "Unknown"

        fruit_vegetable_intake = st.selectbox(
            "Fruit & Vegetable Intake",
            intake_options,
            index=intake_options.index(
                default_fruit
            ),
            key="form_fruit_vegetable",
        )

    col1, col2 = st.columns(2)

    with col1:

        default_whole_grain = existing_diet.get(
            "whole_grain_intake",
            "Unknown",
        )

        if default_whole_grain not in intake_options:
            default_whole_grain = "Unknown"

        whole_grain_intake = st.selectbox(
            "Whole-Grain Intake",
            intake_options,
            index=intake_options.index(
                default_whole_grain
            ),
            key="form_whole_grain",
        )

    with col2:

        default_sugary = existing_diet.get(
            "sugary_beverage_intake",
            "Unknown",
        )

        if default_sugary not in intake_options:
            default_sugary = "Unknown"

        sugary_beverage_intake = st.selectbox(
            "Sugary Beverage Intake",
            intake_options,
            index=intake_options.index(
                default_sugary
            ),
            key="form_sugary_beverages",
        )

    col1, col2 = st.columns(2)

    with col1:

        default_processed = existing_diet.get(
            "processed_food_intake",
            "Unknown",
        )

        if default_processed not in intake_options:
            default_processed = "Unknown"

        processed_food_intake = st.selectbox(
            "Processed Food Intake",
            intake_options,
            index=intake_options.index(
                default_processed
            ),
            key="form_processed_food",
        )

    with col2:

        default_added_sugar = existing_diet.get(
            "added_sugar_intake",
            "Unknown",
        )

        if default_added_sugar not in intake_options:
            default_added_sugar = "Unknown"

        added_sugar_intake = st.selectbox(
            "Added Sugar Intake",
            intake_options,
            index=intake_options.index(
                default_added_sugar
            ),
            key="form_added_sugar",
        )

    dietary_pattern = st.text_input(
        "Dietary Pattern",
        value=existing_diet.get(
            "dietary_pattern",
            "",
        ),
        placeholder=(
            "Example: Mixed diet with moderate "
            "intake of sugary beverages"
        ),
        key="form_dietary_pattern",
    )

    dietary_other_information = st.text_area(
        "Other Dietary Information",
        value=existing_diet.get(
            "other_information",
            "",
        ),
        placeholder=(
            "Optional additional dietary information."
        ),
        height=80,
        key="form_dietary_other",
    )


# ============================================================
# 8. MEDICAL HISTORY
# ============================================================

st.header("8. Medical History")

with st.container(border=True):

    medical_history = st.text_area(
        "Previous Medical Conditions",
        value=extracted_value(
            "medical_history",
            "",
        ),
        placeholder=(
            "Example: Hypertension, dyslipidemia, "
            "cardiovascular disease..."
        ),
        height=100,
        key="form_medical_history",
    )

    medications = st.text_area(
        "Current Medications",
        value=extracted_value(
            "medications",
            "",
        ),
        placeholder="Example: No medications",
        height=100,
        key="form_medications",
    )


# ============================================================
# BUILD PATIENT DATA
# ============================================================

active_patient_data = {

    "age": age,

    "sex": sex,

    "weight": weight,

    "height": height,

    "bmi": bmi,

    "blood_glucose": (
        None
        if blood_glucose == 0
        else blood_glucose
    ),

    "fasting_status": fasting_status,

    "hba1c": (
        None
        if hba1c == 0
        else hba1c
    ),

    "total_cholesterol": (
        None
        if total_cholesterol == 0
        else total_cholesterol
    ),

    "systolic_bp": systolic_bp,

    "diastolic_bp": diastolic_bp,

    "family_history": family_history,

    "physical_activity": physical_activity,

    "smoking": smoking,

    "medical_history": medical_history,

    "medications": medications,

    "dietary_intake": {

        "meal_pattern": meal_pattern,

        "fruit_vegetable_intake": (
            fruit_vegetable_intake
        ),

        "whole_grain_intake": (
            whole_grain_intake
        ),

        "sugary_beverage_intake": (
            sugary_beverage_intake
        ),

        "processed_food_intake": (
            processed_food_intake
        ),

        "added_sugar_intake": (
            added_sugar_intake
        ),

        "dietary_pattern": dietary_pattern,

        "other_information": (
            dietary_other_information
        ),
    },
}


st.session_state.patient_data = active_patient_data


# ============================================================
# PATIENT DATA SUMMARY
# ============================================================

with st.expander("📋 Review Structured Patient Data"):

    summary_rows = [

        ("Age", f"{age} years"),

        ("Sex", sex),

        ("Weight", f"{weight:.1f} kg"),

        ("Height", f"{height:.1f} cm"),

        ("BMI", f"{bmi:.1f} kg/m²"),

        (
            "Blood Glucose",
            (
                "Not available"
                if blood_glucose is None
                else f"{blood_glucose:.1f} mg/dL"
            ),
        ),

        ("Glucose Status", fasting_status),

        (
            "HbA1c",
            (
                "Not available"
                if hba1c is None
                else f"{hba1c:.1f}%"
            ),
        ),

        (
            "Total Cholesterol",
            (
                "Not available"
                if total_cholesterol is None
                else f"{total_cholesterol:.0f} mg/dL"
            ),
        ),

        (
            "Blood Pressure",
            f"{systolic_bp:.0f}/{diastolic_bp:.0f} mmHg",
        ),

        (
            "Family History",
            family_history,
        ),

        (
            "Physical Activity",
            physical_activity,
        ),

        ("Smoking", smoking),

        ("Meal Pattern", meal_pattern),

        (
            "Fruit & Vegetables",
            fruit_vegetable_intake,
        ),

        (
            "Whole Grains",
            whole_grain_intake,
        ),

        (
            "Sugary Beverages",
            sugary_beverage_intake,
        ),

        (
            "Processed Foods",
            processed_food_intake,
        ),

        (
            "Added Sugar",
            added_sugar_intake,
        ),
    ]

    st.dataframe(
        pd.DataFrame(
            summary_rows,
            columns=[
                "Clinical Variable",
                "Current Value",
            ],
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 9. DATA VALIDATION
# ============================================================

st.header("9. Clinical Data Quality")

if st.button(
    "🔍 Validate Clinical Data",
    type="secondary",
    use_container_width=True,
):

    with st.spinner(
        "Checking clinical data quality..."
    ):

        validation_result = validate_patient_data(
            active_patient_data
        )

    st.session_state.validation_result = (
        validation_result
    )

    st.session_state.assessment_result = None
    st.session_state.verification_result = None


validation_result = (
    st.session_state.validation_result
)


if validation_result is not None:

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        if validation_result["is_valid"]:

            st.metric(
                "Validation Status",
                "Valid",
            )

        else:

            st.metric(
                "Validation Status",
                "Review Required",
            )

    with col2:

        missing_count = len(
            validation_result.get(
                "missing_fields",
                []
            )
        )

        st.metric(
            "Missing Fields",
            missing_count,
        )

    with col3:

        warning_count = len(
            validation_result.get(
                "warnings",
                []
            )
        )

        st.metric(
            "Warnings",
            warning_count,
        )

    if validation_result.get("errors"):

        st.error("### Validation Errors")

        for error in validation_result["errors"]:

            st.error(error)

    if validation_result.get("warnings"):

        st.warning("### Validation Warnings")

        for warning in validation_result["warnings"]:

            st.warning(warning)

    if validation_result.get("missing_fields"):

        st.info("### Missing Information")

        for field in validation_result["missing_fields"]:

            st.write(f"• {field}")

    calculated_bmi = validation_result.get(
        "calculated_bmi"
    )

    if calculated_bmi is not None:

        st.metric(
            "Validated BMI",
            f"{calculated_bmi:.1f} kg/m²",
        )


# ============================================================
# 10. EVIDENCE-GROUNDED ASSESSMENT
# ============================================================

if (
    validation_result is not None
    and validation_result["is_valid"]
):

    st.header(
        "10. Evidence-Grounded Clinical Assessment"
    )

    st.write(
        "The system retrieves relevant medical evidence and "
        "uses it to generate an evidence-grounded clinical "
        "interpretation."
    )

    if st.button(
        "🤖 Generate Evidence-Grounded Assessment",
        type="primary",
        use_container_width=True,
    ):

        with st.spinner(
            "Retrieving evidence and generating assessment..."
        ):

            try:

                assessment_result = (
                    run_clinical_assessment(
                        active_patient_data,
                        top_k=3,
                    )
                )

                st.session_state.assessment_result = (
                    assessment_result
                )

                st.session_state.verification_result = None

            except Exception as error:

                st.session_state.assessment_result = {

                    "success": False,

                    "assessment": (
                        f"Assessment failed: {error}"
                    ),

                    "evidence": [],
                }


# ============================================================
# DISPLAY ASSESSMENT
# ============================================================

assessment_result = (
    st.session_state.assessment_result
)


if assessment_result is not None:

    st.divider()

    if assessment_result.get(
        "success",
        False,
    ):

        st.subheader(
            "📋 Evidence-Grounded Assessment"
        )

        assessment_text = (
            assessment_result.get(
                "assessment",
                "",
            )
        )

        if assessment_text:

            st.markdown(
                assessment_text
            )

        else:

            st.warning(
                "No assessment text was returned."
            )

        # ====================================================
        # EVIDENCE
        # ====================================================

        st.divider()

        st.subheader(
            "📚 Supporting Medical Evidence"
        )

        evidence = (
            assessment_result.get(
                "evidence",
                [],
            )
        )

        if evidence:

            st.success(
                f"{len(evidence)} evidence items retrieved."
            )

            evidence_rows = []

            for index, item in enumerate(evidence):

                evidence_number = item.get(
                    "evidence_number",
                    index + 1,
                )

                evidence_rows.append(
                    {
                        "Evidence": (
                            f"E{evidence_number}"
                        ),
                        "Source": item.get(
                            "source",
                            "N/A",
                        ),
                        "Year": item.get(
                            "year",
                            "N/A",
                        ),
                        "Category": item.get(
                            "category",
                            "N/A",
                        ),
                        "PMID": item.get(
                            "pmid",
                            "N/A",
                        ),
                        "Article ID": item.get(
                            "article_id",
                            "N/A",
                        ),
                    }
                )

            st.dataframe(
                pd.DataFrame(evidence_rows),
                use_container_width=True,
                hide_index=True,
            )

            for index, item in enumerate(evidence):

                evidence_number = item.get(
                    "evidence_number",
                    index + 1,
                )

                title = item.get(
                    "title",
                    "Medical Evidence",
                )

                with st.expander(
                    f"E{evidence_number} — {title}"
                ):

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            "**Article ID:**",
                            item.get(
                                "article_id",
                                "N/A",
                            ),
                        )

                        st.write(
                            "**Source:**",
                            item.get(
                                "source",
                                "N/A",
                            ),
                        )

                        st.write(
                            "**Year:**",
                            item.get(
                                "year",
                                "N/A",
                            ),
                        )

                        st.write(
                            "**Category:**",
                            item.get(
                                "category",
                                "N/A",
                            ),
                        )

                    with col2:

                        st.write(
                            "**PMID:**",
                            item.get(
                                "pmid",
                                "N/A",
                            ),
                        )

                        st.write(
                            "**DOI:**",
                            item.get(
                                "doi",
                                "N/A",
                            ),
                        )

                        if item.get("pmc_id"):

                            st.write(
                                "**PMC ID:**",
                                item.get(
                                    "pmc_id"
                                ),
                            )

                    if item.get("section"):

                        st.write(
                            "**Evidence Type:**",
                            item.get(
                                "section"
                            ),
                        )

                    if item.get("distance") is not None:

                        st.write(
                            "**Retrieval Distance:**",
                            item.get(
                                "distance"
                            ),
                        )

                    if item.get("relevance_score") is not None:

                        st.write(
                            "**Evidence Relevance Score:**",
                            item.get(
                                "relevance_score"
                            ),
                        )

                    st.markdown(
                        "**Retrieved Passage**"
                    )

                    st.write(
                        item.get(
                            "text",
                            item.get(
                                "document",
                                "",
                            ),
                        )
                    )

        else:

            st.warning(
                "No supporting evidence was returned."
            )

        # ====================================================
        # VERIFICATION
        # ====================================================

        st.divider()

        st.subheader(
            "🔎 Evidence Verification"
        )

        st.write(
            "Verification checks whether important claims "
            "in the generated assessment are supported by "
            "the retrieved evidence."
        )

        if evidence:

            if st.button(
                "Verify Assessment Against Evidence",
                type="secondary",
                key="verify_assessment_button",
            ):

                with st.spinner(
                    "Checking assessment against retrieved evidence..."
                ):

                    try:

                        verification = (
                            verify_assessment(
                                assessment_result.get(
                                    "assessment",
                                    "",
                                ),
                                evidence,
                            )
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
                    str,
                ):

                    st.markdown(
                        verification_result
                    )

                else:

                    st.write(
                        verification_result
                    )

                st.info(
                    "Verification is an experimental "
                    "evidence-support check for this research "
                    "prototype. It does not constitute clinical "
                    "validation."
                )

            else:

                st.caption(
                    "Run verification after reviewing the "
                    "generated assessment and retrieved evidence."
                )

        # ====================================================
        # LIMITATIONS
        # ====================================================

        st.divider()

        st.info(
            """
            **Prototype limitation:** Retrieved evidence,
            generated interpretation and verification output
            are research artifacts. They should not be treated
            as an autonomous diagnostic or treatment system.
            """
        )

    else:

        st.error(
            "The assessment could not be generated."
        )

        st.write(
            assessment_result.get(
                "assessment",
                "Unknown error.",
            )
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "T2D-EviGuide | Evidence-Grounded AI for Early "
    "Type 2 Diabetes Risk Assessment"
)

st.caption(
    "MSc Health Informatics / Data Analytics Research Prototype"
)