from backend.rag_engine import build_evidence_package
from backend.ai_engine import ask_llm
from clinical_guardrails_v2 import check_clinical_guardrails_v2


# ============================================================
# HELPER: FORMAT MISSING VALUES
# ============================================================

def display_value(value):

    if value is None or value == "":
        return "Not provided"

    return str(value)


# ============================================================
# PATIENT SUMMARY
# ============================================================

def build_patient_summary(patient_data):

    p = patient_data or {}
    clinical_notes = p.get("clinical_notes", "")

    if clinical_notes:
        clinical_notes_section = f"""
CLINICAL NOTES PROVIDED BY USER:
{clinical_notes}
"""
    else:
        clinical_notes_section = "No additional clinical notes provided."

    summary = f"""
PATIENT & DEMOGRAPHIC INFORMATION

Age: {display_value(p.get('age'))}
Sex: {display_value(p.get('sex'))}
Marital status: {display_value(p.get('marital_status'))}
Occupation: {display_value(p.get('occupation'))}
Nature of work: {display_value(p.get('work_activity'))}
Residence: {display_value(p.get('residence'))}

Family history of diabetes: {display_value(p.get('family_history'))}
Family history of cardiovascular disease: {display_value(p.get('family_history_cvd'))}
Previous prediabetes: {display_value(p.get('previous_prediabetes'))}
Gestational diabetes history: {display_value(p.get('gestational_diabetes'))}


ANTHROPOMETRIC MEASUREMENTS

Weight: {display_value(p.get('weight'))} kg
Height: {display_value(p.get('height'))} cm
BMI: {display_value(p.get('bmi'))} kg/m²
Waist circumference: {display_value(p.get('waist_circumference'))} cm


LABORATORY MEASUREMENTS

Fasting blood glucose: {display_value(p.get('fasting_glucose'))} mg/dL
HbA1c: {display_value(p.get('hba1c'))} %

Total cholesterol: {display_value(p.get('total_cholesterol'))} mg/dL
HDL cholesterol: {display_value(p.get('hdl'))} mg/dL
LDL cholesterol: {display_value(p.get('ldl'))} mg/dL
Triglycerides: {display_value(p.get('triglycerides'))} mg/dL


VITAL SIGNS

Systolic blood pressure: {display_value(p.get('systolic_bp'))} mmHg
Diastolic blood pressure: {display_value(p.get('diastolic_bp'))} mmHg


PHYSICAL ACTIVITY & LIFESTYLE

Physical activity frequency: {display_value(p.get('physical_activity'))}
Activity duration per session: {display_value(p.get('activity_duration'))} minutes
Sedentary time: {display_value(p.get('sedentary_hours'))} hours/day
Sleep duration: {display_value(p.get('sleep_duration'))} hours/day

Smoking: {display_value(p.get('smoking'))}
Alcohol consumption: {display_value(p.get('alcohol'))}


DIETARY INFORMATION

Fruit and vegetable intake: {display_value(p.get('fruit_vegetable_intake'))}
Whole grain intake: {display_value(p.get('whole_grain_intake'))}
Sugary beverage consumption: {display_value(p.get('sugary_drinks'))}
Sweets/added sugar consumption: {display_value(p.get('sweets_added_sugar'))}
Fried/high-fat food consumption: {display_value(p.get('fried_food'))}
Processed/packaged food consumption: {display_value(p.get('processed_food'))}

Additional dietary information:
{display_value(p.get('dietary_notes'))}


MEDICAL HISTORY

Hypertension: {display_value(p.get('hypertension'))}
Dyslipidemia: {display_value(p.get('dyslipidemia'))}
Cardiovascular disease: {display_value(p.get('cardiovascular_disease'))}
Kidney disease: {display_value(p.get('kidney_disease'))}
Liver disease: {display_value(p.get('liver_disease'))}
PCOS: {display_value(p.get('pcos'))}

Other medical history:
{display_value(p.get('medical_history'))}


MEDICATION INFORMATION

Current medications:
{display_value(p.get('medications'))}

Recently added medication:
{display_value(p.get('recent_medication'))}

New medication details:
{display_value(p.get('new_medication'))}


ADDITIONAL CLINICAL INFORMATION

Additional clinical notes:
{display_value(p.get('additional_notes'))}

Uploaded clinical reports:
{display_value(p.get('uploaded_reports'))}
"""
    return summary.strip()


# ============================================================
# EVIDENCE FORMATTING
# ============================================================

def format_evidence_for_llm(evidence):

    if not evidence:
        return "No evidence was retrieved."

    formatted = []

    for item in evidence:

        evidence_number = item.get("evidence_number", "N/A")
        article_id = item.get("article_id", "N/A")
        title = item.get("title", "N/A")
        source = item.get("source", "N/A")
        year = item.get("year", item.get("publication_year", "Not available"))
        pmid = item.get("pmid", "Not available")
        doi = item.get("doi", "Not available")
        language = item.get("language") or "unknown"

        text = item.get(
            "text",
            item.get("document", "")
        )

        formatted.append(
            f"""
[Evidence {evidence_number} | {article_id}]

Title: {title}
Source: {source}
Publication year: {year}
PMID: {pmid}
DOI: {doi}
Language: {language}

Evidence:
{text}
"""
        )

    return "\n".join(formatted)


# ============================================================
# CLINICAL QUESTION
# ============================================================

def create_clinical_question(patient_data):

    p = patient_data or {}

    patient_measurements = []

    relevant_fields = {
        "BMI": "bmi",
        "HbA1c": "hba1c",
        "Fasting glucose": "fasting_glucose",
        "Waist circumference": "waist_circumference",
        "Systolic blood pressure": "systolic_bp",
        "Diastolic blood pressure": "diastolic_bp",
        "Family history of diabetes": "family_history",
        "Previous prediabetes": "previous_prediabetes",
        "Gestational diabetes": "gestational_diabetes",
    }

    for label, key in relevant_fields.items():

        value = p.get(key)

        if value is not None and value != "":

            patient_measurements.append(
                f"{label}: {value}"
            )

    measurement_context = "\n".join(patient_measurements)

    return f"""
Assess the evidence relevant to early Type 2 Diabetes
risk indicators using the available patient information.

PATIENT MEASUREMENTS AND HISTORY

{measurement_context}

Focus evidence retrieval on:

1. Fasting blood glucose and HbA1c interpretation.
2. Established Type 2 Diabetes risk factors.
3. BMI and waist circumference.
4. Physical activity and sedentary behaviour.
5. Dietary factors.
6. Blood pressure and lipid-related risk factors.
7. Family history of diabetes.
8. Previous prediabetes and gestational diabetes.
9. Screening and early risk-assessment considerations.

Retrieve evidence relevant to the available patient information.

Do not assume that missing measurements or medical
conditions are present.

The purpose is evidence-grounded clinical decision support,
not independent diagnosis.
"""


# ============================================================
# CLINICAL ASSESSMENT
# ============================================================

def generate_risk_assessment(patient_data, top_k=3):

    patient_data = patient_data or {}

    patient_summary = build_patient_summary(patient_data)

    clinical_question = create_clinical_question(patient_data)

    # --------------------------------------------------------
    # EVIDENCE RETRIEVAL
    # --------------------------------------------------------

    try:

        evidence = build_evidence_package(
            clinical_question,
            top_k=top_k
        )

    except Exception:

        return {
            "success": False,
            "assessment": (
                "Evidence retrieval could not be completed. "
                "Please review the system and try again."
            ),
            "evidence": [],
            "patient_summary": patient_summary,
            "clinical_question": clinical_question,
            "guardrail_flags": {},
            "guardrail_status": "NOT PERFORMED",
        }

    if not evidence:

        return {
            "success": False,
            "assessment": (
                "Insufficient relevant evidence was retrieved. "
                "A reliable evidence-grounded assessment "
                "cannot currently be generated."
            ),
            "evidence": [],
            "patient_summary": patient_summary,
            "clinical_question": clinical_question,
            "guardrail_flags": {},
            "guardrail_status": "NOT PERFORMED",
        }

    evidence_text = format_evidence_for_llm(evidence)

    print("DEBUG - Patient summary length:", len(patient_summary))
    print("DEBUG - Clinical question length:", len(clinical_question))
    print("DEBUG - Evidence length:", len(evidence_text))

    # --------------------------------------------------------
    # LLM PROMPT
    # --------------------------------------------------------

    llm_question = f"""
You are supporting a healthcare research prototype
called T2D-EviGuide.

The system supports evidence-grounded early risk assessment
for Type 2 Diabetes.

PATIENT INFORMATION

{patient_summary}

CLINICAL QUESTION

{clinical_question}

RETRIEVED EVIDENCE

{evidence_text}


ASSESSMENT FORMAT

1. Overall Risk Assessment
2. Key Risk Indicators
3. Relevant Clinical Measurements
4. Protective or Lower-Risk Factors
5. Missing or Uncertain Information
6. Evidence-Based Interpretation
7. Important Limitations


EVIDENCE CITATION RULES

Every medical interpretation based on retrieved literature
must include a citation in this exact format:

[Evidence N | ARTICLE_ID]

Use only evidence numbers and article IDs supplied above.

Never invent citations or article identifiers.

Do not cite unrelated evidence.
EVIDENCE LANGUAGE SAFETY RULES

Check the language label provided for every evidence source.

1. Prefer English-language evidence when answering English clinical questions.
2. Do not present German or Spanish source text as English.
3. Do not claim that a source has been translated unless a verified translation is available.
4. Clearly identify non-English sources when citing them.
5. If non-English evidence is important to the assessment, state that human translation and verification are required.
6. Do not silently exclude relevant evidence or misrepresent its meaning.
7. Do not use unverified non-English evidence as the sole basis
   for a clinical conclusion. Clearly flag it for translation
   and human verification.

PATIENT DATA RULES

Use only the patient information supplied above.

Do not invent:

- Medical conditions
- Symptoms
- Laboratory values
- Family history
- Medication use
- Previous diagnoses

Clearly distinguish missing information from negative findings.

Do not assume that a condition is absent simply because
it was not reported.


BMI RULE

Use the BMI value supplied in the patient information.

Do not calculate or introduce another BMI value.


CLINICAL SAFETY RULES

- Do not diagnose the patient.
- Do not provide a numerical probability.
- Do not prescribe medication.
- Do not recommend medication changes or dosages.
- Do not claim that the patient has diabetes.
- Distinguish patient measurements from medical interpretation.
- Mention missing and uncertain information.
- Do not make unsupported medical claims.
- State clearly when evidence is insufficient.

This is a research prototype, not a substitute for
professional clinical assessment.
"""

    # --------------------------------------------------------
    # LLM GENERATION
    # --------------------------------------------------------
    try:

        print("DEBUG - Full LLM prompt length:", len(llm_question))

        answer = ask_llm(
            llm_question,
            []
        )

        answer = str(answer).strip()

        if not answer:
            raise ValueError("The AI returned an empty assessment.")

    except Exception as error:

     return {
            "success": False,
            "assessment": (
                f"AI generation failed: {type(error).__name__}: {error}"
            ),
            "evidence": evidence,
            "patient_summary": patient_summary,
            "clinical_question": clinical_question,
            "guardrail_flags": {},
            "guardrail_status": "NOT PERFORMED",
        }
    # --------------------------------------------------------
    # CLINICAL SAFETY GUARDRAILS
    # --------------------------------------------------------

    try:

        guardrail_flags = check_clinical_guardrails_v2(
            answer,
            patient_data
        )

        triggered_flags = [
            name
            for name, triggered in guardrail_flags.items()
            if triggered
        ]

        if triggered_flags:

            guardrail_status = "REVIEW REQUIRED"

            safety_notice = """

IMPORTANT — CLINICAL SAFETY REVIEW REQUIRED

The automated clinical terminology checks identified
potential issues requiring human review.

Flagged checks:
""" + "\n".join(
                f"- {flag}" for flag in triggered_flags
            ) + """

Do not treat this assessment as clinically cleared.
Review the relevant measurements and interpretation.
"""

            answer = answer + "\n\n" + safety_notice

        else:

            guardrail_status = "NO FLAGS DETECTED"

    except Exception:

        guardrail_flags = {}

        guardrail_status = "GUARDRAIL CHECK FAILED"

        answer += """

IMPORTANT — SAFETY CHECK NOT COMPLETED

The automated clinical safety check could not be completed.
This assessment requires manual review and must not be
treated as safety-verified.
"""

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {
        "success": True,
        "assessment": answer,
        "evidence": evidence,
        "patient_summary": patient_summary,
        "clinical_question": clinical_question,
        "guardrail_flags": guardrail_flags,
        "guardrail_status": guardrail_status,
    }