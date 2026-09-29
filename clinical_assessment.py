"""
clinical_assessment.py

T2D-EviGuide evidence-grounded clinical assessment pipeline.

Pipeline:

    Patient data
         ↓
    Data completeness
         ↓
    Patient summary
         ↓
    Clinical question
         ↓
    Evidence retrieval
         ↓
    LLM evidence-grounded assessment
         ↓
    Evidence verification

This module does NOT diagnose diabetes and does not calculate
a clinical diabetes-risk score.
"""


from evidence_package import build_evidence_package
from llm_client import ask_llm
from evidence_verifier import verify_assessment


# ============================================================
# MISSING VALUE DETECTION
# ============================================================

def is_missing(value):
    """
    Determine whether a patient value is missing or uncertain.
    """

    if value is None:
        return True

    if isinstance(value, str):

        normalized = value.strip().lower()

        missing_values = {
            "",
            "unknown",
            "not known",
            "not available",
            "n/a",
            "na",
            "none",
            "missing",
            "not reported",
            "not provided",
        }

        return normalized in missing_values

    return False


# ============================================================
# DISPLAY NAMES
# ============================================================

FIELD_DISPLAY_NAMES = {

    "age":
        "Age",

    "sex":
        "Sex",

    "weight":
        "Weight",

    "height":
        "Height",

    "bmi":
        "BMI",

    "blood_glucose":
        "Blood glucose",

    "fasting_status":
        "Glucose measurement status",

    "hba1c":
        "HbA1c",

    "total_cholesterol":
        "Total cholesterol",

    "systolic_bp":
        "Systolic blood pressure",

    "diastolic_bp":
        "Diastolic blood pressure",

    "family_history":
        "Family history",

    "physical_activity":
        "Physical activity",

    "smoking":
        "Smoking",

    "medical_history":
        "Medical history",

    "medications":
        "Medications",

    "dietary_intake":
        "Dietary intake",
}


# ============================================================
# DIETARY FIELD DISPLAY NAMES
# ============================================================

DIETARY_FIELD_DISPLAY_NAMES = {

    "meal_pattern":
        "Meal pattern",

    "fruit_vegetable_intake":
        "Fruit and vegetable intake",

    "whole_grain_intake":
        "Whole-grain intake",

    "sugary_beverage_intake":
        "Sugary beverage intake",

    "processed_food_intake":
        "Processed food intake",

    "added_sugar_intake":
        "Added sugar intake",

    "dietary_pattern":
        "Dietary pattern",

    "other_information":
        "Other dietary information",
}


# ============================================================
# DATA COMPLETENESS
# ============================================================

def assess_data_completeness(patient):
    """
    Calculate completeness for core clinical variables and
    structured dietary variables.

    Fasting status is included because it materially affects
    interpretation of a blood glucose measurement.

    Dietary information is tracked separately but included
    in the overall completeness calculation.
    """

    expected_fields = [

        "age",
        "sex",
        "bmi",
        "blood_glucose",
        "hba1c",
        "systolic_bp",
        "diastolic_bp",
        "family_history",
        "physical_activity",
        "smoking",
        "medical_history",
        "fasting_status",
    ]

    available = []
    missing = []

    for field in expected_fields:

        value = patient.get(
            field
        )

        if is_missing(value):

            missing.append(
                field
            )

        else:

            available.append(
                field
            )


    # --------------------------------------------------------
    # Dietary information
    # --------------------------------------------------------

    dietary_intake = patient.get(
        "dietary_intake",
        {}
    )

    if not isinstance(
        dietary_intake,
        dict
    ):

        dietary_intake = {}


    dietary_fields = [

        "meal_pattern",

        "fruit_vegetable_intake",

        "whole_grain_intake",

        "sugary_beverage_intake",

        "processed_food_intake",

        "added_sugar_intake",

        "dietary_pattern",

        "other_information",
    ]


    dietary_available = []
    dietary_missing = []


    for field in dietary_fields:

        value = dietary_intake.get(
            field
        )

        if is_missing(value):

            dietary_missing.append(
                field
            )

        else:

            dietary_available.append(
                field
            )


    # --------------------------------------------------------
    # Overall completeness
    # --------------------------------------------------------

    total_expected = (
        len(expected_fields)
        + len(dietary_fields)
    )

    total_available = (
        len(available)
        + len(dietary_available)
    )


    if total_expected > 0:

        completeness = (
            total_available
            / total_expected
        ) * 100

    else:

        completeness = 0


    return {

        "completeness_percentage":
            round(
                completeness,
                1
            ),

        "available":
            available,

        "missing":
            missing,

        "dietary_available":
            dietary_available,

        "dietary_missing":
            dietary_missing,

        "dietary_completeness_percentage":
            round(
                (
                    len(dietary_available)
                    / len(dietary_fields)
                ) * 100,
                1
            ),
    }


# ============================================================
# PATIENT SUMMARY
# ============================================================

def build_patient_summary(patient):
    """
    Build a compact structured patient summary.

    Blood glucose and measurement status are explicitly
    separated.

    Dietary information is included only when supplied.
    """

    lines = []


    # --------------------------------------------------------
    # Demographics
    # --------------------------------------------------------

    if not is_missing(
        patient.get("age")
    ):

        lines.append(
            f"Age: {patient['age']}"
        )


    if not is_missing(
        patient.get("sex")
    ):

        lines.append(
            f"Sex: {patient['sex']}"
        )


    # --------------------------------------------------------
    # Anthropometrics
    # --------------------------------------------------------

    if not is_missing(
        patient.get("weight")
    ):

        lines.append(
            f"Weight: {patient['weight']} kg"
        )


    if not is_missing(
        patient.get("height")
    ):

        lines.append(
            f"Height: {patient['height']} cm"
        )


    if not is_missing(
        patient.get("bmi")
    ):

        lines.append(
            f"BMI: {patient['bmi']} kg/m²"
        )


    # --------------------------------------------------------
    # Blood glucose
    # --------------------------------------------------------

    if not is_missing(
        patient.get("blood_glucose")
    ):

        lines.append(
            "Blood glucose: "
            f"{patient['blood_glucose']} mg/dL"
        )


    fasting_status = patient.get(
        "fasting_status",
        "Unknown"
    )


    if is_missing(
        fasting_status
    ):

        fasting_status = "Unknown"


    lines.append(
        "Glucose measurement status: "
        f"{fasting_status}"
    )


    # --------------------------------------------------------
    # HbA1c
    # --------------------------------------------------------

    if not is_missing(
        patient.get("hba1c")
    ):

        lines.append(
            f"HbA1c: {patient['hba1c']} %"
        )


    # --------------------------------------------------------
    # Cholesterol
    # --------------------------------------------------------

    if not is_missing(
        patient.get("total_cholesterol")
    ):

        lines.append(
            "Total cholesterol: "
            f"{patient['total_cholesterol']} mg/dL"
        )


    # --------------------------------------------------------
    # Blood pressure
    # --------------------------------------------------------

    systolic = patient.get(
        "systolic_bp"
    )

    diastolic = patient.get(
        "diastolic_bp"
    )


    if (
        not is_missing(systolic)
        and not is_missing(diastolic)
    ):

        lines.append(
            "Blood pressure: "
            f"{systolic}/{diastolic} mmHg"
        )


    # --------------------------------------------------------
    # Family history
    # --------------------------------------------------------

    if not is_missing(
        patient.get("family_history")
    ):

        lines.append(
            "Family history of diabetes: "
            f"{patient['family_history']}"
        )


    # --------------------------------------------------------
    # Physical activity
    # --------------------------------------------------------

    if not is_missing(
        patient.get("physical_activity")
    ):

        lines.append(
            "Physical activity: "
            f"{patient['physical_activity']}"
        )


    # --------------------------------------------------------
    # Smoking
    # --------------------------------------------------------

    if not is_missing(
        patient.get("smoking")
    ):

        lines.append(
            f"Smoking: {patient['smoking']}"
        )


    # --------------------------------------------------------
    # Medical history
    # --------------------------------------------------------

    if not is_missing(
        patient.get("medical_history")
    ):

        lines.append(
            "Medical history: "
            f"{patient['medical_history']}"
        )


    # --------------------------------------------------------
    # Medications
    # --------------------------------------------------------

    if not is_missing(
        patient.get("medications")
    ):

        lines.append(
            "Medications: "
            f"{patient['medications']}"
        )


    # ========================================================
    # DIETARY INTAKE
    # ========================================================

    dietary_intake = patient.get(
        "dietary_intake",
        {}
    )


    if isinstance(
        dietary_intake,
        dict
    ):

        dietary_lines = []


        if not is_missing(
            dietary_intake.get(
                "meal_pattern"
            )
        ):

            dietary_lines.append(
                "Meal pattern: "
                f"{dietary_intake['meal_pattern']}"
            )


        if not is_missing(
            dietary_intake.get(
                "fruit_vegetable_intake"
            )
        ):

            dietary_lines.append(
                "Fruit and vegetable intake: "
                f"{dietary_intake['fruit_vegetable_intake']}"
            )


        if not is_missing(
            dietary_intake.get(
                "whole_grain_intake"
            )
        ):

            dietary_lines.append(
                "Whole-grain intake: "
                f"{dietary_intake['whole_grain_intake']}"
            )


        if not is_missing(
            dietary_intake.get(
                "sugary_beverage_intake"
            )
        ):

            dietary_lines.append(
                "Sugary beverage intake: "
                f"{dietary_intake['sugary_beverage_intake']}"
            )


        if not is_missing(
            dietary_intake.get(
                "processed_food_intake"
            )
        ):

            dietary_lines.append(
                "Processed food intake: "
                f"{dietary_intake['processed_food_intake']}"
            )


        if not is_missing(
            dietary_intake.get(
                "added_sugar_intake"
            )
        ):

            dietary_lines.append(
                "Added sugar intake: "
                f"{dietary_intake['added_sugar_intake']}"
            )


        if not is_missing(
            dietary_intake.get(
                "dietary_pattern"
            )
        ):

            dietary_lines.append(
                "Dietary pattern: "
                f"{dietary_intake['dietary_pattern']}"
            )


        if not is_missing(
            dietary_intake.get(
                "other_information"
            )
        ):

            dietary_lines.append(
                "Other dietary information: "
                f"{dietary_intake['other_information']}"
            )


        if dietary_lines:

            lines.append(
                "Dietary intake:"
            )

            lines.extend(
                dietary_lines
            )


    return "\n".join(
        lines
    )


# ============================================================
# DIETARY SUMMARY
# ============================================================

def build_dietary_summary(patient):
    """
    Build a separate dietary summary for the retrieval query.
    """

    dietary_intake = patient.get(
        "dietary_intake",
        {}
    )


    if not isinstance(
        dietary_intake,
        dict
    ):

        return "Dietary intake: Not provided."


    lines = []


    field_order = [

        "meal_pattern",

        "fruit_vegetable_intake",

        "whole_grain_intake",

        "sugary_beverage_intake",

        "processed_food_intake",

        "added_sugar_intake",

        "dietary_pattern",

        "other_information",
    ]


    for field in field_order:

        value = dietary_intake.get(
            field
        )

        if not is_missing(value):

            display_name = (
                DIETARY_FIELD_DISPLAY_NAMES.get(
                    field,
                    field
                )
            )

            lines.append(
                f"{display_name}: {value}"
            )


    if not lines:

        return "Dietary intake: Not provided."


    return "\n".join(
        lines
    )


# ============================================================
# CLINICAL QUESTION
# ============================================================

def build_clinical_question(patient):
    """
    Build a targeted evidence-retrieval question.

    The question incorporates:

    - glycemic measurements
    - measurement status
    - BMI
    - age
    - family history
    - physical activity
    - blood pressure
    - medical history
    - dietary intake

    Measurement types remain explicitly separated.
    """

    question_parts = []


    # ========================================================
    # GLYCEMIC MEASUREMENTS
    # ========================================================

    glucose = patient.get(
        "blood_glucose",
        "Not provided"
    )


    fasting_status = patient.get(
        "fasting_status",
        "Unknown"
    )


    if is_missing(
        fasting_status
    ):

        fasting_status = "Unknown"


    hba1c = patient.get(
        "hba1c",
        "Not provided"
    )


    question_parts.append(
        f"""
Clinical measurements:

Blood glucose:
{glucose} mg/dL

Glucose measurement status:
{fasting_status}

HbA1c:
{hba1c} %

Retrieve evidence relevant to interpretation of these
measurements for early Type 2 Diabetes risk assessment,
prediabetes, and screening.

Important:
Do not assume that the blood glucose measurement was
fasting unless fasting status is explicitly provided.
"""
    )


    # ========================================================
    # BMI
    # ========================================================

    bmi = patient.get(
        "bmi"
    )


    if not is_missing(
        bmi
    ):

        question_parts.append(
            f"""
BMI:

{bmi} kg/m²

Retrieve evidence regarding BMI/body weight and
Type 2 Diabetes risk where directly relevant.
"""
        )


    # ========================================================
    # AGE
    # ========================================================

    age = patient.get(
        "age"
    )


    if not is_missing(
        age
    ):

        question_parts.append(
            f"""
Age:

{age}

Retrieve evidence relevant to age as a Type 2 Diabetes
risk or screening consideration where supported.
"""
        )


    # ========================================================
    # FAMILY HISTORY
    # ========================================================

    family_history = patient.get(
        "family_history"
    )


    if not is_missing(
        family_history
    ):

        question_parts.append(
            f"""
Family history:

{family_history}

Retrieve evidence regarding family history and
Type 2 Diabetes risk where relevant.
"""
        )


    # ========================================================
    # PHYSICAL ACTIVITY
    # ========================================================

    physical_activity = patient.get(
        "physical_activity"
    )


    if not is_missing(
        physical_activity
    ):

        question_parts.append(
            f"""
Physical activity:

{physical_activity}

Retrieve evidence regarding physical activity and
Type 2 Diabetes risk or prevention where supported.
"""
        )


    # ========================================================
    # SMOKING
    # ========================================================

    smoking = patient.get(
        "smoking"
    )


    if not is_missing(
        smoking
    ):

        question_parts.append(
            f"""
Smoking:

{smoking}

Retrieve evidence regarding smoking and Type 2 Diabetes
risk only where directly relevant and supported.
"""
        )


    # ========================================================
    # BLOOD PRESSURE
    # ========================================================

    systolic = patient.get(
        "systolic_bp"
    )

    diastolic = patient.get(
        "diastolic_bp"
    )


    if (
        not is_missing(systolic)
        and not is_missing(diastolic)
    ):

        question_parts.append(
            f"""
Blood pressure:

Systolic:
{systolic} mmHg

Diastolic:
{diastolic} mmHg

Retrieve evidence regarding elevated blood pressure or
hypertension as a Type 2 Diabetes risk consideration.
"""
        )


    # ========================================================
    # MEDICAL HISTORY
    # ========================================================

    medical_history = patient.get(
        "medical_history"
    )


    if not is_missing(
        medical_history
    ):

        question_parts.append(
            f"""
Medical history:

{medical_history}

Retrieve evidence regarding medical history that is
directly associated with Type 2 Diabetes risk.
"""
        )


    # ========================================================
    # DIETARY INTAKE
    # ========================================================

    dietary_summary = (
        build_dietary_summary(
            patient
        )
    )


    if dietary_summary != "Dietary intake: Not provided.":

        question_parts.append(
            f"""
Dietary intake:

{dietary_summary}

Retrieve evidence regarding the supplied dietary
characteristics and their relationship to Type 2 Diabetes
risk or prevention, where supported.

Do not assume that a dietary characteristic is harmful or
protective without supporting evidence.
Do not convert dietary information into a numerical risk
score.
"""
        )


    # ========================================================
    # GENERAL RETRIEVAL REQUIREMENTS
    # ========================================================

    question_parts.append(
        """
General evidence retrieval requirements:

1. Prefer evidence directly relevant to Type 2 Diabetes
   early risk assessment, prediabetes, screening, and
   relevant clinical measurements.

2. Prefer clinical guidelines, systematic reviews,
   high-quality reviews, and relevant primary research.

3. Prefer recent evidence where appropriate while retaining
   authoritative guideline evidence.

4. Avoid unrelated disease-specific evidence unless it
   directly contributes to the assessment.

5. Do not assume that a missing patient characteristic
   is present.

6. Do not retrieve evidence for a factor as though it were
   present when that patient information is unavailable.

7. Evidence should be suitable for supporting a clinician-
   review decision-support summary.

8. Keep these measurement types distinct:

   - random glucose
   - fasting plasma glucose
   - 2-hour OGTT glucose
   - HbA1c

9. Do not apply a threshold for one measurement type to
   another measurement type.

10. Dietary information should be interpreted only when
    retrieved evidence directly supports the interpretation.

11. Do not infer causality from an individual patient's
    dietary intake.

12. Do not provide a diagnosis from an isolated measurement.
"""
    )


    return "\n".join(
        question_parts
    )


# ============================================================
# CLINICAL ASSESSMENT
# ============================================================

def run_clinical_assessment(
    patient,
    top_k=3
):
    """
    Complete T2D-EviGuide assessment pipeline.

    Pipeline:

        patient data
             ↓
        data completeness
             ↓
        patient summary
             ↓
        clinical question
             ↓
        evidence retrieval
             ↓
        LLM assessment
             ↓
        evidence verification
    """

    # ========================================================
    # DATA QUALITY
    # ========================================================

    data_quality = (
        assess_data_completeness(
            patient
        )
    )


    # ========================================================
    # PATIENT SUMMARY
    # ========================================================

    patient_summary = (
        build_patient_summary(
            patient
        )
    )


    # ========================================================
    # CLINICAL QUESTION
    # ========================================================

    clinical_question = (
        build_clinical_question(
            patient
        )
    )


    # ========================================================
    # EVIDENCE RETRIEVAL
    # ========================================================

    try:

        evidence = build_evidence_package(
            clinical_question,
            top_k=top_k
        )

    except Exception as error:

        return {

            "success":
                False,

            "patient":
                patient,

            "data_quality":
                data_quality,

            "patient_summary":
                patient_summary,

            "clinical_question":
                clinical_question,

            "evidence":
                [],

            "assessment":
                (
                    "Clinical assessment generation failed.\n\n"
                    "Evidence retrieval failed.\n\n"
                    f"Error: {error}"
                ),

            "verification":
                (
                    "Evidence verification was not performed "
                    "because evidence retrieval failed."
                ),
        }


    # ========================================================
    # ASSESSMENT PROMPT
    # ========================================================

    assessment_question = f"""
Patient information:

{patient_summary}


Clinical question:

{clinical_question}


The retrieved evidence is supplied separately to the LLM.


Clinical interpretation requirements:

- Use only the supplied patient information and retrieved
  evidence.

- Do not invent missing patient information.

- Do not assume fasting status.

- Keep random glucose, fasting glucose, and 2-hour OGTT
  glucose distinct.

- Do not apply fasting thresholds to a glucose measurement
  when fasting status is unknown.

- Do not apply a 2-hour OGTT threshold to another glucose
  measurement type.

- Keep HbA1c interpretation distinct from glucose
  measurement interpretation.

- Distinguish an abnormal laboratory finding from a
  confirmed diagnosis.

- Do not diagnose Type 2 Diabetes.

- Do not provide medication recommendations.

- Do not provide treatment recommendations.

- Do not provide a numerical diabetes risk score.

- Do not call normal findings "protective factors" unless
  the retrieved evidence explicitly supports that wording.

- Do not infer missing symptoms, repeat measurements,
  family history, dietary information, or other unavailable
  patient characteristics.

- Dietary information should only be interpreted when the
  retrieved evidence supports the interpretation.

- Do not assume that a dietary pattern is beneficial or
  harmful without evidence.

- If the retrieved evidence does not establish a claim,
  explicitly state that the supplied retrieved evidence
  does not establish it.

- Clearly distinguish evidence-supported interpretation from
  missing or uncertain information.

- Keep the output suitable for clinician review.


Return the following sections:

# Evidence-Grounded Assessment of Early Type 2 Diabetes Risk

## 1. Overall Evidence-Supported Interpretation

Provide a concise interpretation based only on the patient
information and retrieved evidence.

## 2. Key Risk Indicators

Identify patient characteristics that are relevant according
to the retrieved evidence.

Do not create a numerical risk score.

## 3. Relevant Clinical Measurements

Discuss HbA1c and blood glucose separately.

State the glucose measurement status.

Do not apply a fasting-specific threshold when fasting status
is unknown.

## 4. Lifestyle and Dietary Context

Discuss physical activity, smoking, and dietary information
only when the retrieved evidence supports their relevance.

Do not describe a dietary characteristic as protective or
harmful without supporting evidence.

## 5. Lower-Risk or Unremarkable Findings

Describe findings that are unremarkable only where the
retrieved evidence supports that interpretation.

Do not call these findings "protective factors" unless the
evidence explicitly supports that terminology.

## 6. Missing or Uncertain Information

Clearly identify information that is missing, unknown,
uncertain, or would limit interpretation.

## 7. Evidence-Based Interpretation

Explain how the retrieved evidence relates to the patient
data.

Keep measurement types and evidence-supported thresholds
distinct.

## 8. Important Limitations

State that this is an evidence-grounded research prototype,
not an autonomous diagnostic system or clinically validated
risk-prediction model.
"""


    # ========================================================
    # LLM ASSESSMENT
    # ========================================================

    try:

        assessment = ask_llm(
            assessment_question,
            evidence
        )

        if not assessment:

            raise RuntimeError(
                "The LLM returned an empty assessment."
            )

    except Exception as error:

        return {

            "success":
                False,

            "patient":
                patient,

            "data_quality":
                data_quality,

            "patient_summary":
                patient_summary,

            "clinical_question":
                clinical_question,

            "evidence":
                evidence,

            "assessment":
                (
                    "Clinical assessment generation failed.\n\n"
                    f"Error: {error}"
                ),

            "verification":
                (
                    "Evidence verification was not performed "
                    "because assessment generation failed."
                ),
        }


    # ========================================================
    # EVIDENCE VERIFICATION
    # ========================================================

    try:

        verification = verify_assessment(
            assessment,
            evidence
        )

    except Exception as error:

        verification = (
            "Evidence verification failed.\n\n"
            f"Error: {error}"
        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "success":
            True,

        "patient":
            patient,

        "data_quality":
            data_quality,

        "patient_summary":
            patient_summary,

        "clinical_question":
            clinical_question,

        "evidence":
            evidence,

        "assessment":
            assessment,

        "verification":
            verification,
    }


# ============================================================
# PRINT RESULT
# ============================================================

def print_assessment_result(
    result
):
    """
    Print the complete assessment result.
    """

    print()
    print(
        "=" * 70
    )

    print(
        "T2D-EviGuide Clinical Assessment"
    )

    print(
        "=" * 70
    )


    # ========================================================
    # DATA QUALITY
    # ========================================================

    data_quality = result[
        "data_quality"
    ]

    print()
    print(
        "===== DATA QUALITY ====="
    )

    print()

    print(
        "Overall completeness: "
        f"{data_quality['completeness_percentage']}%"
    )

    print(
        "Dietary completeness: "
        f"{data_quality['dietary_completeness_percentage']}%"
    )


    print()
    print(
        "Available information:"
    )


    for field in data_quality[
        "available"
    ]:

        print(
            f"  ✓ "
            f"{FIELD_DISPLAY_NAMES.get(field, field)}"
        )


    if data_quality.get(
        "dietary_available"
    ):

        print()

        print(
            "Available dietary information:"
        )

        for field in data_quality[
            "dietary_available"
        ]:

            print(
                f"  ✓ "
                f"{DIETARY_FIELD_DISPLAY_NAMES.get(field, field)}"
            )


    print()
    print(
        "Missing / uncertain information:"
    )


    if data_quality[
        "missing"
    ]:

        for field in data_quality[
            "missing"
        ]:

            print(
                f"  ⚠ "
                f"{FIELD_DISPLAY_NAMES.get(field, field)}"
            )

    else:

        print(
            "  None identified"
        )


    if data_quality.get(
        "dietary_missing"
    ):

        print()

        print(
            "Missing / uncertain dietary information:"
        )

        for field in data_quality[
            "dietary_missing"
        ]:

            print(
                f"  ⚠ "
                f"{DIETARY_FIELD_DISPLAY_NAMES.get(field, field)}"
            )


    # ========================================================
    # PATIENT SUMMARY
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        "===== PATIENT SUMMARY ====="
    )

    print(
        "=" * 70
    )

    print()

    print(
        result[
            "patient_summary"
        ]
    )


    # ========================================================
    # CLINICAL QUESTION
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        "===== CLINICAL QUESTION ====="
    )

    print(
        "=" * 70
    )

    print()

    print(
        result[
            "clinical_question"
        ]
    )


    # ========================================================
    # ASSESSMENT
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        "===== ASSESSMENT ====="
    )

    print(
        "=" * 70
    )

    print()

    print(
        result[
            "assessment"
        ]
    )


    # ========================================================
    # VERIFICATION
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        "===== EVIDENCE VERIFICATION ====="
    )

    print(
        "=" * 70
    )

    print()

    print(
        result.get(
            "verification",
            "No verification result available."
        )
    )


    # ========================================================
    # STATUS
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        "===== ASSESSMENT STATUS ====="
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"Success: {result['success']}"
    )

    print(
        "Overall data completeness: "
        f"{data_quality['completeness_percentage']}%"
    )

    print(
        "Dietary data completeness: "
        f"{data_quality['dietary_completeness_percentage']}%"
    )


    # ========================================================
    # SUPPORTING EVIDENCE
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        "===== SUPPORTING EVIDENCE ====="
    )

    print(
        "=" * 70
    )

    print()

    evidence = result[
        "evidence"
    ]


    if not evidence:

        print(
            "No sufficiently relevant evidence retrieved."
        )

        return


    for item in evidence:

        print(
            f"Evidence "
            f"{item['evidence_number']}: "
            f"[{item['title']}]"
        )

        print(
            "Article ID: "
            f"{item['article_id']}"
        )

        print(
            "Source: "
            f"{item['source']}"
        )

        print(
            "Year: "
            f"{item['year']}"
        )

        print(
            "Category: "
            f"{item['category']}"
        )

        print(
            "PMID: "
            f"{item['pmid']}"
        )

        print(
            "DOI: "
            f"{item['doi']}"
        )

        print(
            "PMC ID: "
            f"{item['pmc_id']}"
        )

        print(
            "Evidence Type: "
            f"{item['section']}"
        )

        print(
            "Retrieval distance: "
            f"{item['distance']}"
        )


        if "relevance_score" in item:

            print(
                "Evidence relevance score: "
                f"{item['relevance_score']:.2f}"
            )


        print()

        print(
            "Evidence text:"
        )

        print(
            item["text"]
        )

        print()

        print(
            "-" * 70
        )


# ============================================================
# TEST PATIENT
# ============================================================

test_patient = {

    "age":
        45,

    "sex":
        "Female",

    "weight":
        62,

    "height":
        160,

    "bmi":
        24.2,

    "blood_glucose":
        100,

    "fasting_status":
        "Unknown",

    "hba1c":
        5.7,

    "total_cholesterol":
        180,

    "systolic_bp":
        120,

    "diastolic_bp":
        80,

    "family_history":
        "No",

    "physical_activity":
        "Low",

    "smoking":
        "Never",

    "medical_history":
        "Hypertension",

    "medications":
        "No medications",

    "dietary_intake": {

        "meal_pattern":
            "Regular",

        "fruit_vegetable_intake":
            "Moderate",

        "whole_grain_intake":
            "Low",

        "sugary_beverage_intake":
            "Moderate",

        "processed_food_intake":
            "Moderate",

        "added_sugar_intake":
            "Moderate",

        "dietary_pattern":
            "Mixed diet with moderate intake of sugary beverages",

        "other_information":
            "No other dietary information reported.",
    },
}


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    result = run_clinical_assessment(
        test_patient,
        top_k=3
    )

    print_assessment_result(
        result
    )