from evidence_package import build_evidence_package
from llm_client import ask_llm


# ============================================================
# PATIENT SUMMARY
# ============================================================

def build_patient_summary(patient_data):

    summary = f"""
PATIENT & DEMOGRAPHIC INFORMATION

Age: {patient_data.get('age')}
Sex: {patient_data.get('sex')}
Marital status: {patient_data.get('marital_status')}
Occupation: {patient_data.get('occupation')}
Nature of work: {patient_data.get('work_activity')}
Residence: {patient_data.get('residence')}

Family history of diabetes: {patient_data.get('family_history')}
Family history of cardiovascular disease: {patient_data.get('family_history_cvd')}
Previous prediabetes: {patient_data.get('previous_prediabetes')}
Gestational diabetes history: {patient_data.get('gestational_diabetes')}


ANTHROPOMETRIC MEASUREMENTS

Weight: {patient_data.get('weight')} kg
Height: {patient_data.get('height')} cm
BMI: {patient_data.get('bmi')} kg/m²
Waist circumference: {patient_data.get('waist_circumference')} cm


LABORATORY MEASUREMENTS

Fasting blood glucose: {patient_data.get('fasting_glucose')} mg/dL
HbA1c: {patient_data.get('hba1c')} %

Total cholesterol: {patient_data.get('total_cholesterol')} mg/dL
HDL cholesterol: {patient_data.get('hdl')} mg/dL
LDL cholesterol: {patient_data.get('ldl')} mg/dL
Triglycerides: {patient_data.get('triglycerides')} mg/dL


VITAL SIGNS

Systolic blood pressure: {patient_data.get('systolic_bp')} mmHg
Diastolic blood pressure: {patient_data.get('diastolic_bp')} mmHg


PHYSICAL ACTIVITY & LIFESTYLE

Physical activity frequency: {patient_data.get('physical_activity')}
Activity duration per session: {patient_data.get('activity_duration')} minutes
Sedentary time: {patient_data.get('sedentary_hours')} hours/day
Sleep duration: {patient_data.get('sleep_duration')} hours/day

Smoking: {patient_data.get('smoking')}
Alcohol consumption: {patient_data.get('alcohol')}


DIETARY INFORMATION

Fruit and vegetable intake: {patient_data.get('fruit_vegetable_intake')}
Whole grain intake: {patient_data.get('whole_grain_intake')}
Sugary beverage consumption: {patient_data.get('sugary_drinks')}
Sweets/added sugar consumption: {patient_data.get('sweets_added_sugar')}
Fried/high-fat food consumption: {patient_data.get('fried_food')}
Processed/packaged food consumption: {patient_data.get('processed_food')}

Additional dietary information:
{patient_data.get('dietary_notes')}


MEDICAL HISTORY

Hypertension: {patient_data.get('hypertension')}
Dyslipidemia: {patient_data.get('dyslipidemia')}
Cardiovascular disease: {patient_data.get('cardiovascular_disease')}
Kidney disease: {patient_data.get('kidney_disease')}
Liver disease: {patient_data.get('liver_disease')}
PCOS: {patient_data.get('pcos')}

Other medical history:
{patient_data.get('medical_history')}


MEDICATION INFORMATION

Current medications:
{patient_data.get('medications')}

Recently added medication: {patient_data.get('recent_medication_added')}
New medication details:
{patient_data.get('new_medication')}


ADDITIONAL CLINICAL INFORMATION

Additional clinical notes:
{patient_data.get('additional_notes')}

Uploaded clinical reports:
{patient_data.get('uploaded_reports')}
"""

    return summary.strip()


# ============================================================
# CLINICAL QUESTION
# ============================================================

def format_evidence_for_llm(evidence):
    """
    Convert retrieved evidence into a structured text format
    that can be supplied to the LLM.
    """

    if not evidence:
        return "No evidence was retrieved."

    formatted = []

    for item in evidence:

        evidence_number = item.get(
            "evidence_number",
            "N/A"
        )

        article_id = item.get(
            "article_id",
            "N/A"
        )

        title = item.get(
            "title",
            "N/A"
        )

        source = item.get(
            "source",
            "N/A"
        )

        text = item.get(
            "text",
            item.get(
                "document",
                ""
            )
        )

        formatted.append(
            f"""
[Evidence {evidence_number} | {article_id}]

Title: {title}

Source: {source}

Evidence:
{text}
"""
        )

    return "\n".join(formatted)
def create_clinical_question(patient_data):
    """
    Create an evidence-retrieval question from the patient's
    multimodal clinical information.

    The question is used by the RAG system to retrieve
    relevant Type 2 Diabetes evidence from the literature.
    """

    return """
Assess the patient's early risk indicators for Type 2 Diabetes
using the available multimodal clinical information.

Focus the evidence retrieval on:

1. Interpretation of fasting blood glucose and HbA1c
   when supported by the retrieved literature.

2. Established risk factors for Type 2 Diabetes.

3. Body weight, BMI, and waist circumference.

4. Physical activity and sedentary behaviour.

5. Dietary factors including sugary beverages,
   added sugars, whole grains, fruits and vegetables,
   fried/high-fat foods, and processed/packaged foods.

6. Blood pressure and lipid-related cardiovascular
   risk factors.

7. Family history of diabetes and relevant medical history.

8. Previous prediabetes or gestational diabetes when provided.

9. Appropriate screening and early risk-assessment considerations.

Use evidence directly relevant to Type 2 Diabetes.
Avoid unrelated disease-specific evidence.

The goal is to support an evidence-grounded clinical
decision-support assessment, not to independently diagnose
the patient.
"""
def generate_risk_assessment(patient_data, top_k=3):

    patient_summary = build_patient_summary(patient_data)

    clinical_question = create_clinical_question(patient_data)

    evidence = build_evidence_package(
        clinical_question,
        top_k=top_k
    )

    if not evidence:
        return {
            "success": False,
            "assessment": (
                "Insufficient relevant evidence was retrieved "
                "for this assessment."
            ),
            "evidence": [],
            "patient_summary": patient_summary,
            "clinical_question": clinical_question,
        }

    evidence_text = format_evidence_for_llm(evidence)

    llm_question = f"""
You are supporting a healthcare research prototype called
T2D-EviGuide.

The system is performing an evidence-grounded early risk
assessment for Type 2 Diabetes.

PATIENT INFORMATION

{patient_summary}

CLINICAL QUESTION

{clinical_question}

RETRIEVED EVIDENCE

{evidence_text}

Prepare an evidence-grounded clinical assessment using ONLY
the patient information and retrieved evidence provided above.

Use the following sections:

1. Overall Risk Assessment
2. Key Risk Indicators
3. Relevant Clinical Measurements
4. Protective or Lower-Risk Factors
5. Missing or Uncertain Information
6. Evidence-Based Interpretation
7. Important Limitations

IMPORTANT EVIDENCE CITATION RULE:

Every claim that depends on retrieved medical evidence MUST
include an explicit evidence citation.

The citation MUST use EXACTLY this format:

[Evidence N | ARTICLE_ID]

Examples:

[Evidence 1 | AACE_2026_T2D]
[Evidence 2 | T2D_DIAGNOSIS_REVIEW_2026]
[Evidence 3 | USPSTF_2021_SCREENING]

NEVER use:
[Evidence 1]
[Evidence 2]
[Evidence 3]

NEVER omit the ARTICLE_ID.
NEVER invent an ARTICLE_ID.

Use ONLY evidence numbers and ARTICLE_IDs that appear in the
RETRIEVED EVIDENCE section.

IMPORTANT PATIENT DATA RULE:

Use ONLY the patient values explicitly present in PATIENT INFORMATION.

Do NOT assume that a condition exists simply because it is a
common risk factor for Type 2 Diabetes.

Do NOT invent or infer:

- previous prediabetes
- gestational diabetes
- hypertension
- dyslipidemia
- cardiovascular disease
- kidney disease
- liver disease
- PCOS
- medication use
- symptoms
- laboratory values
- family-history details

If a condition is not explicitly present in PATIENT INFORMATION,
do not state that the patient has that condition.

IMPORTANT BMI RULE:

Use the BMI value explicitly provided in PATIENT INFORMATION.

Do NOT recalculate BMI if a calculated BMI is already provided.

Do NOT create a second BMI value.

IMPORTANT EVIDENCE RULE:

Do not use general medical knowledge that is not supported by
the retrieved evidence.

Patient-specific facts should be labelled as patient data and
do not require an evidence citation.

Medical interpretation based on retrieved literature MUST use
the exact evidence citation format.

If evidence is insufficient for a conclusion, state that clearly.

SAFETY RULES:

- Do not diagnose the patient.
- Do not provide a numerical probability.
- Do not prescribe medications.
- Do not recommend medication changes or dosages.
- Do not claim that the patient has a disease unless this is
  explicitly documented in the patient information.
- Clearly distinguish patient-reported measurements from
  evidence-based interpretation.
- Mention missing or uncertain information.
- Do not cite evidence that is unrelated to the clinical claim.
- Do not create citations for unsupported claims.

Before finishing the assessment, check that:

1. Every evidence-based medical claim has [Evidence N | ARTICLE_ID].
2. No citation uses [Evidence N] alone.
3. Every patient condition mentioned actually appears in
   PATIENT INFORMATION.
4. The BMI value is consistent throughout the assessment.
5. No unsupported medical condition has been added.
"""

    try:

        answer = ask_llm(
            llm_question,
            evidence
        )

        return {
            "success": True,
            "assessment": answer,
            "evidence": evidence,
            "patient_summary": patient_summary,
            "clinical_question": clinical_question,
        }

    except Exception as e:

        return {
            "success": False,
            "assessment": (
                f"The AI assessment could not be generated: {e}"
            ),
            "evidence": evidence,
            "patient_summary": patient_summary,
            "clinical_question": clinical_question,
        }
        
        #charanya testing