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
    layout="wide"
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

st.title("🩺 T2D-EviGuide")

st.subheader(
    "AI-Based Early Risk Assessment of Type 2 Diabetes"
)

st.write(
    "Evidence-grounded clinical decision-support prototype "
    "using multimodal clinical data and medical literature."
)

st.info(
    "This prototype provides evidence-grounded clinical "
    "interpretation for research purposes. It does not "
    "provide a diagnosis or replace assessment by a "
    "qualified healthcare professional."
)


# ============================================================
# PATIENT INFORMATION
# ============================================================

st.header("1. Patient Information")

col1, col2, col3 = st.columns(3)


with col1:

    age = st.number_input(
        "Age (years)",
        min_value=1,
        max_value=120,
        value=45,
        step=1
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

    family_history = st.selectbox(
        "Family history of diabetes",
        [
            "Yes",
            "No",
            "Unknown"
        ]
    )


# ============================================================
# ANTHROPOMETRIC DATA
# ============================================================

st.header("2. Anthropometric Measurements")

col1, col2, col3 = st.columns(3)


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

    if height > 0:

        bmi = weight / ((height / 100) ** 2)

    else:

        bmi = 0.0

    st.metric(
        "Calculated BMI",
        f"{bmi:.1f} kg/m²"
    )


# ============================================================
# LABORATORY DATA
# ============================================================

st.header("3. Laboratory Measurements")

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


# ============================================================
# VITAL SIGNS
# ============================================================

st.header("4. Vital Signs")

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


# ============================================================
# LIFESTYLE
# ============================================================

st.header("5. Lifestyle Information")

col1, col2 = st.columns(2)


with col1:

    physical_activity = st.selectbox(
        "Physical Activity",
        [
            "Low",
            "Moderate",
            "High",
            "Unknown"
        ]
    )


with col2:

    smoking = st.selectbox(
        "Smoking Status",
        [
            "Never",
            "Former",
            "Current",
            "Unknown"
        ]
    )


# ============================================================
# MEDICAL HISTORY
# ============================================================

st.header("6. Medical History")

medical_history = st.text_area(
    "Previous Medical Conditions",
    placeholder=(
        "Example: Hypertension, dyslipidemia, "
        "cardiovascular disease..."
    ),
    height=100
)


medications = st.text_area(
    "Current Medications",
    placeholder="Example: No medications",
    height=100
)


# ============================================================
# BUILD PATIENT DATA
# ============================================================

patient_data = {

    "age": age,

    "sex": sex,

    "weight": weight,

    "height": height,

    "bmi": bmi,

    "fasting_glucose": fasting_glucose,

    "hba1c": hba1c,

    "total_cholesterol": total_cholesterol,

    "systolic_bp": systolic_bp,

    "diastolic_bp": diastolic_bp,

    "family_history": family_history,

    "physical_activity": physical_activity,

    "smoking": smoking,

    "medical_history": medical_history,

    "medications": medications
}


# ============================================================
# VALIDATION
# ============================================================

st.header("7. Clinical Data Validation")


if st.button(
    "Validate Patient Data",
    type="secondary"
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

    # Clear old results because the patient data
    # may have changed.

    st.session_state.assessment_result = None

    st.session_state.verification_result = None


# ============================================================
# DISPLAY VALIDATION
# ============================================================

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


    # --------------------------------------------------------
    # Validation errors
    # --------------------------------------------------------

    if validation_result["errors"]:

        st.subheader(
            "Validation Errors"
        )

        for error in validation_result["errors"]:

            st.error(error)


    # --------------------------------------------------------
    # Validation warnings
    # --------------------------------------------------------

    if validation_result["warnings"]:

        st.subheader(
            "Validation Warnings"
        )

        for warning in validation_result["warnings"]:

            st.warning(warning)


    # --------------------------------------------------------
    # Validated BMI
    # --------------------------------------------------------

    if validation_result["calculated_bmi"] is not None:

        st.metric(
            "Validated BMI",
            f"{validation_result['calculated_bmi']:.1f} kg/m²"
        )


# ============================================================
# AI RISK ASSESSMENT
# ============================================================

st.header(
    "8. Evidence-Grounded Risk Assessment"
)


if (
    validation_result is not None
    and validation_result["is_valid"]
):

    if st.button(
        "Generate Evidence-Grounded Assessment",
        type="primary"
    ):

        with st.spinner(
            "Retrieving medical evidence and "
            "generating assessment..."
        ):

            try:

                # IMPORTANT:
                # generate_risk_assessment now returns
                # a dictionary containing both the
                # assessment and retrieved evidence.

                assessment_result = (
                    generate_risk_assessment(
                        patient_data,
                        top_k=3
                    )
                )

                st.session_state.assessment_result = (
                    assessment_result
                )

                # Clear previous verification because
                # the assessment has changed.

                st.session_state.verification_result = None


            except Exception as error:

                st.session_state.assessment_result = {

                    "success": False,

                    "assessment": str(error),

                    "evidence": []

                }

                st.session_state.verification_result = None


# ============================================================
# DISPLAY ASSESSMENT
# ============================================================

assessment_result = (
    st.session_state.assessment_result
)


if assessment_result is not None:

    st.divider()


    # ========================================================
    # SUCCESS
    # ========================================================

    if assessment_result.get(
        "success",
        False
    ):

        st.subheader(
            "📋 Evidence-Grounded Clinical Assessment"
        )


        assessment_text = (
            assessment_result.get(
                "assessment",
                ""
            )
        )


        if assessment_text:

            st.markdown(
                assessment_text
            )

        else:

            st.warning(
                "The assessment returned no text."
            )


        # ====================================================
        # SUPPORTING MEDICAL EVIDENCE
        # ====================================================

        st.divider()

        st.subheader(
            "📚 Supporting Medical Evidence"
        )


        evidence = (
            assessment_result.get(
                "evidence",
                []
            )
        )


        if evidence:

            st.success(
                f"{len(evidence)} supporting evidence "
                f"items retrieved."
            )


            for index, item in enumerate(
                evidence
            ):

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

                    source = item.get(
                        "source",
                        "Not available"
                    )

                    year = item.get(
                        "year",
                        "Not available"
                    )

                    category = item.get(
                        "category",
                        "Not available"
                    )

                    pmid = item.get(
                        "pmid",
                        "Not available"
                    )

                    doi = item.get(
                        "doi",
                        "Not available"
                    )

                    article_id = item.get(
                        "article_id",
                        "Not available"
                    )

                    pmc_id = item.get(
                        "pmc_id",
                        ""
                    )

                    section = item.get(
                        "section",
                        ""
                    )

                    distance = item.get(
                        "distance",
                        None
                    )

                    evidence_text = item.get(
                        "text",
                        item.get(
                            "document",
                            ""
                        )
                    )


                    st.write(
                        f"**Stable Evidence ID:** "
                        f"{article_id}"
                    )

                    st.write(
                        f"**Source:** {source}"
                    )

                    st.write(
                        f"**Year:** {year}"
                    )

                    st.write(
                        f"**Category:** {category}"
                    )

                    st.write(
                        f"**PMID:** {pmid}"
                    )

                    st.write(
                        f"**DOI:** {doi}"
                    )


                    if pmc_id:

                        st.write(
                            f"**PMC ID:** {pmc_id}"
                        )


                    if section:

                        st.write(
                            f"**Evidence Type:** "
                            f"{section}"
                        )


                    if distance is not None:

                        try:

                            st.write(
                                "**Retrieval distance:** "
                                f"{float(distance):.4f}"
                            )

                        except (
                            TypeError,
                            ValueError
                        ):

                            st.write(
                                "**Retrieval distance:** "
                                f"{distance}"
                            )


                    st.markdown(
                        "**Retrieved Evidence:**"
                    )

                    st.write(
                        evidence_text
                    )


        else:

            st.warning(
                "No supporting evidence was returned "
                "by the assessment pipeline."
            )


        # ====================================================
        # EVIDENCE VERIFICATION
        # ====================================================

        st.divider()

        st.subheader(
            "🔎 Evidence Verification"
        )

        st.write(
            "The verifier checks whether important claims "
            "in the generated assessment are supported "
            "by the retrieved evidence."
        )


        if evidence:

            if st.button(
                "Verify Assessment Against Evidence",
                type="secondary"
            ):

                with st.spinner(
                    "Checking assessment claims "
                    "against retrieved evidence..."
                ):

                    try:

                        verification = (
                            verify_assessment(
                                assessment_result[
                                    "assessment"
                                ],
                                evidence
                            )
                        )

                        st.session_state.verification_result = (
                            verification
                        )

                    except Exception as error:

                        st.session_state.verification_result = (
                            f"Verification failed: {error}"
                        )


            # ------------------------------------------------
            # Display verification result
            # ------------------------------------------------

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

                    st.markdown(
                        verification_result
                    )

                else:

                    st.write(
                        verification_result
                    )


                st.info(
                    "Verification is an experimental "
                    "evidence-support check for this "
                    "research prototype. It does not "
                    "constitute clinical validation."
                )


            else:

                st.caption(
                    "Click 'Verify Assessment Against "
                    "Evidence' to run the evidence-support "
                    "check."
                )


        else:

            st.info(
                "Evidence verification is unavailable "
                "because no evidence objects were returned."
            )


        # ====================================================
        # CLINICAL DISCLAIMER
        # ====================================================

        st.divider()

        st.info(
            "This prototype provides evidence-grounded "
            "clinical decision support for research and "
            "educational purposes. It does not provide "
            "an autonomous diagnosis or replace assessment "
            "by a qualified healthcare professional."
        )


    # ========================================================
    # ASSESSMENT FAILED
    # ========================================================

    else:

        st.error(
            "The assessment could not be generated."
        )


        error_message = (
            assessment_result.get(
                "assessment",
                "Unknown error."
            )
        )


        st.write(
            error_message
        )


        # ----------------------------------------------------
        # Show evidence even if LLM generation failed
        # ----------------------------------------------------

        failed_evidence = (
            assessment_result.get(
                "evidence",
                []
            )
        )


        if failed_evidence:

            st.divider()

            st.subheader(
                "📚 Evidence Retrieved Before Generation Failed"
            )


            st.info(
                f"{len(failed_evidence)} evidence items "
                "were successfully retrieved."
            )


            for index, item in enumerate(
                failed_evidence
            ):

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
                        f"**PMID:** "
                        f"{item.get('pmid', 'N/A')}"
                    )

                    st.write(
                        f"**DOI:** "
                        f"{item.get('doi', 'N/A')}"
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


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "T2D-EviGuide | MSc Health Informatics / "
    "Data Analytics Research Prototype"
)

# Updated by charanya