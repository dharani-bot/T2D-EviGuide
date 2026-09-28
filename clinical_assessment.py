from evidence_package import build_evidence_package
from llm_client import ask_llm


# ============================================================
# PATIENT SUMMARY
# ============================================================

def build_patient_summary(patient_data):

    summary = f"""
Patient information:

Age: {patient_data.get('age')}
Sex: {patient_data.get('sex')}

Weight: {patient_data.get('weight')} kg
Height: {patient_data.get('height')} cm
BMI: {patient_data.get('bmi')} kg/m²

Fasting blood glucose: {patient_data.get('fasting_glucose')} mg/dL
HbA1c: {patient_data.get('hba1c')} %

Blood pressure:
- Systolic: {patient_data.get('systolic_bp')} mmHg
- Diastolic: {patient_data.get('diastolic_bp')} mmHg

Family history of diabetes:
{patient_data.get('family_history')}

Physical activity:
{patient_data.get('physical_activity')}

Smoking:
{patient_data.get('smoking')}

Medical history:
{patient_data.get('medical_history')}

Current medications:
{patient_data.get('medications')}
"""

    return summary.strip()


# ============================================================
# CLINICAL QUESTION
# ============================================================

def create_clinical_question(patient_data):

    age = patient_data.get("age")
    bmi = patient_data.get("bmi")
    glucose = patient_data.get("fasting_glucose")
    hba1c = patient_data.get("hba1c")
    family_history = patient_data.get("family_history")
    activity = patient_data.get("physical_activity")
    medical_history = patient_data.get("medical_history")

    question = f"""
Type 2 Diabetes early risk assessment for a {age}-year-old
patient with BMI {bmi} kg/m², fasting blood glucose
{glucose} mg/dL, HbA1c {hba1c}%, family history
{family_history}, physical activity level {activity},
and medical history including {medical_history}.

Retrieve evidence addressing:

1. Diagnostic and prediabetes interpretation of fasting
   blood glucose and HbA1c.

2. Established risk factors for Type 2 Diabetes.

3. The relationship between physical activity and Type 2
   Diabetes risk.

4. The relationship between hypertension and Type 2 Diabetes
   risk.

5. The relevance of BMI and body weight to Type 2 Diabetes
   risk.

6. Evidence-based screening or early risk assessment
   considerations.

Prefer evidence directly relevant to Type 2 Diabetes risk
assessment and screening.

Avoid unrelated disease-specific evidence unless it directly
contributes to the assessment.
"""

    return question.strip()


# ============================================================
# FORMAT EVIDENCE FOR LLM
# ============================================================

def format_evidence_for_llm(evidence):

    evidence_text = ""

    for item in evidence:

        evidence_text += f"""
Evidence {item['evidence_number']}

Stable Evidence ID:
{item['article_id']}

Title:
{item['title']}

Source:
{item['source']}

Year:
{item['year']}

Category:
{item['category']}

PMID:
{item['pmid']}

DOI:
{item['doi']}

PMC ID:
{item.get('pmc_id', '')}

Evidence Type:
{item.get('section', '')}

Retrieved Evidence:
{item['text']}

------------------------------------------------------------
"""

    return evidence_text


# ============================================================
# GENERATE RISK ASSESSMENT
# ============================================================

def generate_risk_assessment(
    patient_data,
    top_k=3
):

    # --------------------------------------------------------
    # Build patient summary
    # --------------------------------------------------------

    patient_summary = build_patient_summary(
        patient_data
    )

    # --------------------------------------------------------
    # Build clinical question
    # --------------------------------------------------------

    clinical_question = create_clinical_question(
        patient_data
    )

    # --------------------------------------------------------
    # Retrieve medical evidence
    # --------------------------------------------------------

    evidence = build_evidence_package(
        clinical_question,
        top_k=top_k
    )

    # --------------------------------------------------------
    # No evidence
    # --------------------------------------------------------

    if not evidence:

        return {
            "success": False,

            "assessment": (
                "The retrieved evidence is insufficient "
                "to support an early Type 2 Diabetes "
                "risk assessment."
            ),

            "evidence": [],

            "patient_summary": patient_summary,

            "clinical_question": clinical_question
        }

    # --------------------------------------------------------
    # Format evidence for LLM
    # --------------------------------------------------------

    evidence_text = format_evidence_for_llm(
        evidence
    )

    # ========================================================
    # LLM PROMPT
    # ========================================================

    llm_question = f"""
Assess the following patient's early Type 2 Diabetes risk
indicators using ONLY the retrieved medical evidence.

============================================================
PATIENT INFORMATION
============================================================

{patient_summary}


============================================================
RETRIEVED MEDICAL EVIDENCE
============================================================

{evidence_text}


============================================================
TASK
============================================================

Produce an evidence-grounded clinical interpretation.

Use exactly these sections:

1. Overall Risk Assessment
2. Key Risk Indicators
3. Relevant Clinical Measurements
4. Protective or Lower-Risk Factors
5. Missing or Uncertain Information
6. Evidence-Based Interpretation
7. Important Limitations


============================================================
CITATION FORMAT
============================================================

Every important clinical interpretation must include a
stable evidence citation.

Use this format:

[Evidence N | ARTICLE_ID]

For example:

[Evidence 1 | T2D_DIAGNOSIS_REVIEW_2026]

Do NOT change the ARTICLE_ID.

Do NOT invent an ARTICLE_ID.

If a statement is supported by more than one source, cite
each relevant source.

Example:

[Evidence 1 | T2D_DIAGNOSIS_REVIEW_2026]
[Evidence 2 | USPSTF_2021_SCREENING]


============================================================
STRICT EVIDENCE RULES
============================================================

1. Use ONLY information explicitly supported by the retrieved
   evidence.

2. Patient values themselves may be reported directly from
   the patient data.

3. Clinical interpretation of a patient value must be
   supported by retrieved evidence.

4. Do NOT infer a clinical threshold if the retrieved evidence
   does not explicitly provide that threshold.

5. Do NOT classify fasting glucose or HbA1c unless the
   retrieved evidence explicitly supports that classification.

6. Do NOT call a factor a risk factor merely because an
   article mentions it as a comorbidity.

7. Do NOT call something protective unless the retrieved
   evidence explicitly supports that interpretation.

8. Do NOT assume that a guideline applies to this patient
   unless the patient's characteristics satisfy the criteria
   stated in the retrieved evidence.

9. If a claim cannot be supported by the retrieved evidence,
   write:

   "The retrieved evidence does not establish this."

10. Do NOT use outside medical knowledge.

11. Do NOT provide a numerical probability of developing
    Type 2 Diabetes.

12. Do NOT diagnose the patient.

13. Do NOT prescribe medication.

14. Do NOT recommend starting, stopping, or changing medication.

15. Do NOT provide medication dosage instructions.

16. Do not treat the absence of a statement in an article as
    positive evidence.

17. Clearly separate:

    - Patient data
    - Evidence-supported interpretation
    - Missing information
    - Uncertainty

18. Do not describe an observation as a protective factor
    unless the retrieved evidence explicitly supports that
    interpretation.

19. Do not claim that the patient is at high, moderate, or low
    risk unless the retrieved evidence provides a basis for
    that classification.

20. If evidence is incomplete, acknowledge the limitation
    rather than filling the gap with general medical knowledge.

21. If an article is only indirectly relevant, do not use it
    as the primary support for a clinical conclusion.

22. Never cite an evidence number or article ID that does not
    exist in the supplied evidence.


============================================================
IMPORTANT
============================================================

The goal is evidence-grounded early risk assessment.

This is NOT autonomous diagnosis.

The system should support clinician review by showing:

- what the patient data are,
- what the literature supports,
- what remains uncertain,
- and which source supports each interpretation.

If the retrieved evidence is insufficient to interpret a
clinical value, explicitly say so.
"""

    # ========================================================
    # CALL LLM
    # ========================================================

    try:

        assessment = ask_llm(
            llm_question,
            evidence
        )

    except Exception as error:

        return {
            "success": False,

            "assessment": (
                f"Unable to generate the LLM assessment: "
                f"{error}"
            ),

            # IMPORTANT:
            # Keep retrieved evidence even when
            # the LLM call fails.

            "evidence": evidence,

            "patient_summary": patient_summary,

            "clinical_question": clinical_question
        }

    # ========================================================
    # RETURN STRUCTURED RESULT
    # ========================================================

    return {
        "success": True,

        "assessment": assessment,

        # IMPORTANT:
        # The Streamlit application needs this.
        "evidence": evidence,

        "patient_summary": patient_summary,

        "clinical_question": clinical_question
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    test_patient = {

        "age": 45,

        "sex": "Female",

        "weight": 62,

        "height": 160,

        "bmi": 24.2,

        "fasting_glucose": 100,

        "hba1c": 5.7,

        "systolic_bp": 120,

        "diastolic_bp": 80,

        "family_history": "No",

        "physical_activity": "Low",

        "smoking": "Never",

        "medical_history": "Hypertension",

        "medications": "No medications"
    }

    print()
    print("=" * 60)
    print("T2D-EviGuide Clinical Assessment")
    print("=" * 60)
    print()

    result = generate_risk_assessment(
        test_patient,
        top_k=3
    )

    if result["success"]:

        print("===== ASSESSMENT =====")
        print()

        print(
            result["assessment"]
        )

        print()
        print("=" * 60)
        print("===== SUPPORTING EVIDENCE =====")
        print("=" * 60)
        print()

        for item in result["evidence"]:

            print(
                f"Evidence {item['evidence_number']}: "
                f"{item['title']}"
            )

            print(
                f"Article ID: "
                f"{item['article_id']}"
            )

            print(
                f"Source: "
                f"{item['source']}"
            )

            print(
                f"Year: "
                f"{item['year']}"
            )

            print(
                f"Category: "
                f"{item['category']}"
            )

            print(
                f"PMID: "
                f"{item['pmid']}"
            )

            print(
                f"DOI: "
                f"{item['doi']}"
            )

            print(
                f"PMC ID: "
                f"{item.get('pmc_id', '')}"
            )

            print(
                f"Evidence Type: "
                f"{item.get('section', '')}"
            )

            try:

                print(
                    f"Retrieval distance: "
                    f"{float(item['distance']):.4f}"
                )

            except (
                TypeError,
                ValueError
            ):

                print(
                    f"Retrieval distance: "
                    f"{item.get('distance')}"
                )

            print()
            print("Evidence text:")
            print(
                item["text"]
            )

            print()
            print("-" * 70)
            print()

    else:

        print(
            "===== ASSESSMENT ERROR ====="
        )

        print()

        print(
            result["assessment"]
        )

        if result.get("evidence"):

            print()
            print(
                "Retrieved evidence was available, "
                "but assessment generation failed."
            )