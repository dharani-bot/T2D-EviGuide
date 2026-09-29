import os
import requests
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# OPENROUTER CONFIGURATION
# ============================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

MODEL_NAME = "openrouter/free"


# ============================================================
# DEBUG
# ============================================================

DEBUG_LLM = os.getenv(
    "DEBUG_LLM",
    "false"
).strip().lower() == "true"


# ============================================================
# LLM REQUEST
# ============================================================

def ask_llm(
    question,
    evidence
):
    """
    Send the clinical question and retrieved evidence
    to OpenRouter.

    The function returns only the generated clinical
    assessment text.
    """

    # --------------------------------------------------------
    # API key
    # --------------------------------------------------------

    if not OPENROUTER_API_KEY:

        raise ValueError(
            "OPENROUTER_API_KEY is not configured. "
            "Check your .env file."
        )

    # --------------------------------------------------------
    # Build evidence context
    # --------------------------------------------------------

    if not evidence:

        evidence_text = (
            "No sufficiently relevant evidence was retrieved."
        )

    else:

        evidence_blocks = []

        for item in evidence:

            evidence_blocks.append(
                f"""
==============================
Evidence {item.get('evidence_number', '')}
==============================

Article ID:
{item.get('article_id', '')}

Title:
{item.get('title', '')}

Source:
{item.get('source', '')}

Year:
{item.get('year', '')}

Category:
{item.get('category', '')}

PMID:
{item.get('pmid', '')}

DOI:
{item.get('doi', '')}

Evidence section:
{item.get('section', '')}

Evidence text:
{item.get('text', '')}
"""
            )

        evidence_text = "\n".join(
            evidence_blocks
        )

    # --------------------------------------------------------
    # System prompt
    # --------------------------------------------------------

    system_prompt = """
You are an evidence-grounded clinical information assistant
for the academic healthcare informatics prototype
T2D-EviGuide.

Your task is to produce a clinician-review summary of early
Type 2 Diabetes risk using ONLY the supplied patient
information and retrieved evidence.

This is a research prototype.

It is NOT a validated diagnostic system.

============================================================
CORE RULES
============================================================

1. Do not invent medical facts.

2. Do not invent citations, studies, PMIDs, DOIs,
   thresholds, or evidence.

3. Use only the retrieved evidence supplied in the request.

4. If the evidence does not support a claim, explicitly say:

"The retrieved evidence does not establish this."

5. Distinguish early risk assessment from diagnosis.

6. Do not state that the patient has diabetes unless the
   supplied patient information and evidence explicitly
   establish that conclusion.

7. Do not prescribe medications.

8. Do not recommend starting, stopping, or changing medication.

9. Do not provide dosage instructions.

10. Do not provide treatment prescriptions.

11. Do not provide a numerical diabetes risk score.

12. Do not infer unavailable patient characteristics.

13. Clearly identify missing and uncertain information.

14. Important clinical claims must include an evidence citation
    such as [Evidence 1].

============================================================
GLUCOSE MEASUREMENT SAFETY
============================================================

Keep these measurement types completely distinct:

- random glucose
- fasting plasma glucose
- 2-hour OGTT glucose
- HbA1c

Never apply a threshold belonging to one measurement type
to another.

If fasting status is UNKNOWN:

- Do not assume the glucose was fasting.
- Do not apply a fasting glucose threshold.
- Do not call the glucose measurement impaired fasting
  glucose.
- Do not call the glucose measurement impaired glucose
  tolerance.
- Do not treat it as a 2-hour OGTT result.

Use wording such as:

"The fasting status is unknown, so fasting-glucose
classification cannot be established from this measurement."

A 2-hour OGTT threshold can only be applied when the
patient data explicitly identify a 2-hour OGTT measurement.

============================================================
HbA1c SAFETY
============================================================

Keep HbA1c thresholds separate from glucose thresholds.

When supported by the evidence, distinguish:

"The HbA1c value falls within the retrieved source-defined
range..."

from:

"The patient has prediabetes."

Do not automatically convert a laboratory range into a
definitive diagnosis.

============================================================
DIAGNOSIS SAFETY
============================================================

A single laboratory result does not automatically establish
a diagnosis when the supplied evidence states that confirmation
or repeat testing is required.

Clearly state this limitation.

============================================================
RISK-FACTOR LANGUAGE
============================================================

Do not automatically call normal findings "protective factors."

For example, do not automatically describe:

- normal BMI
- normal blood pressure
- no family history
- never smoking

as protective factors unless the retrieved evidence explicitly
supports that characterization.

Prefer neutral wording:

"No abnormal finding was identified in the supplied value."

============================================================
MISSING DATA
============================================================

Never infer:

- fasting status
- symptoms
- repeat measurements
- previous laboratory results
- disease duration
- medication adherence
- unavailable family history
- unavailable clinical characteristics

============================================================
CLINICAL RECOMMENDATIONS
============================================================

Do not prescribe or recommend treatment.

Do not recommend medication.

Do not recommend medication changes.

Do not give dosage instructions.

Do not prescribe specific lifestyle interventions.

You may state that further clinical evaluation or confirmation
may be relevant when directly supported by the supplied evidence.

============================================================
EVIDENCE TRACEABILITY
============================================================

Every important clinical threshold or interpretation should
have an evidence citation.

Example:

"The HbA1c value falls within the retrieved source-defined
range [Evidence 2]."

Never invent an evidence number.

============================================================
UNCERTAINTY
============================================================

If the evidence is incomplete, ambiguous, contradictory,
or does not apply to the measurement type, state the
uncertainty explicitly.

Do not silently resolve uncertainty.

============================================================
OUTPUT
============================================================

Produce exactly these sections:

# Evidence-Grounded Assessment of Early Type 2 Diabetes Risk

## 1. Overall Evidence-Supported Interpretation

## 2. Key Risk Indicators

## 3. Relevant Clinical Measurements

Use:

| Measurement | Value | Evidence-Supported Interpretation |

## 4. Lower-Risk or Unremarkable Findings

Use neutral language.

## 5. Missing or Uncertain Information

## 6. Evidence-Based Interpretation

## 7. Important Limitations

Do not add a treatment plan.

Do not add medication recommendations.

Do not provide a numerical risk score.

============================================================
FINAL CHECK
============================================================

Before returning the answer, verify:

[ ] Fasting status was not assumed.
[ ] Random glucose was not treated as fasting glucose.
[ ] Random glucose was not treated as 2-hour OGTT glucose.
[ ] HbA1c and glucose thresholds were kept separate.
[ ] Unsupported diagnosis was not made.
[ ] Normal findings were not automatically called protective.
[ ] No treatment recommendation was made.
[ ] No medication recommendation was made.
[ ] No numerical risk score was produced.
[ ] Missing information was acknowledged.
[ ] Important clinical claims have evidence citations.
"""

    # --------------------------------------------------------
    # User prompt
    # --------------------------------------------------------

    user_prompt = f"""
PATIENT / CLINICAL QUESTION

{question}


RETRIEVED MEDICAL EVIDENCE

{evidence_text}


TASK

Using ONLY the patient information and retrieved evidence,
produce the requested clinician-review assessment.

Important:

The fasting status of the blood glucose measurement must
remain UNKNOWN unless explicitly supplied.

Do not assume that 100 mg/dL is a fasting glucose result.

Do not classify it as impaired fasting glucose.

Do not classify it as impaired glucose tolerance.

Do not classify it as a 2-hour OGTT result.

Interpret HbA1c separately.

If the evidence supports that the HbA1c value falls within
a source-defined prediabetes/increased-risk range, describe
the laboratory finding accurately while distinguishing it
from a definitive diagnosis.

Return only the clinical assessment.
"""

    # --------------------------------------------------------
    # Debug prompt
    # --------------------------------------------------------

    if DEBUG_LLM:

        print()
        print(
            "===== LLM DEBUG: MODEL ====="
        )
        print(
            MODEL_NAME
        )

        print()
        print(
            "===== LLM DEBUG: USER PROMPT ====="
        )
        print(
            user_prompt
        )

        print()
        print(
            "=================================="
        )
        print()

    # --------------------------------------------------------
    # OpenRouter API request
    # --------------------------------------------------------

    try:

        response = requests.post(
            OPENROUTER_URL,

            headers={
                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                    "application/json",
            },

            json={
                "model":
                    MODEL_NAME,

                "messages": [
                    {
                        "role":
                            "system",

                        "content":
                            system_prompt,
                    },
                    {
                        "role":
                            "user",

                        "content":
                            user_prompt,
                    },
                ],

                "temperature":
                    0.1,
            },

            timeout=60,
        )

    except requests.exceptions.RequestException as error:

        raise RuntimeError(
            f"Could not connect to OpenRouter: "
            f"{error}"
        ) from error

    # --------------------------------------------------------
    # API error
    # --------------------------------------------------------

    if not response.ok:

        print()
        print(
            "===== OPENROUTER ERROR ====="
        )

        print(
            "Status code:",
            response.status_code
        )

        print(
            "Response:",
            response.text
        )

        print(
            "============================"
        )

        print()

        response.raise_for_status()

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        result = response.json()

    except ValueError as error:

        raise RuntimeError(
            "OpenRouter returned invalid JSON."
        ) from error

    # --------------------------------------------------------
    # Debug raw response
    # --------------------------------------------------------

    if DEBUG_LLM:

        print()
        print(
            "===== RAW LLM RESPONSE ====="
        )

        print(
            result
        )

        print(
            "============================"
        )

        print()

    # --------------------------------------------------------
    # Validate choices
    # --------------------------------------------------------

    if (
        "choices" not in result
        or not result["choices"]
    ):

        raise RuntimeError(
            "OpenRouter response did not contain a valid "
            f"choice: {result}"
        )

    choice = result[
        "choices"
    ][0]

    # --------------------------------------------------------
    # Extract message
    # --------------------------------------------------------

    message = choice.get(
        "message",
        {}
    )

    # --------------------------------------------------------
    # Some models/providers may return refusal
    # --------------------------------------------------------

    refusal = message.get(
        "refusal"
    )

    if refusal:

        raise RuntimeError(
            "The selected model refused the request: "
            f"{refusal}"
        )

    # --------------------------------------------------------
    # Extract content
    # --------------------------------------------------------

    answer = message.get(
        "content"
    )

    # --------------------------------------------------------
    # Handle unusual response format
    # --------------------------------------------------------

    if isinstance(
        answer,
        list
    ):

        text_parts = []

        for part in answer:

            if isinstance(
                part,
                dict
            ):

                text_value = part.get(
                    "text"
                )

                if text_value:

                    text_parts.append(
                        text_value
                    )

            elif isinstance(
                part,
                str
            ):

                text_parts.append(
                    part
                )

        answer = "\n".join(
            text_parts
        )

    # --------------------------------------------------------
    # Validate answer
    # --------------------------------------------------------

    if not answer:

        raise RuntimeError(
            "OpenRouter returned no usable text content."
        )

    answer = str(
        answer
    ).strip()

    # --------------------------------------------------------
    # Guard against a non-assessment response
    # --------------------------------------------------------

    if answer.lower() in {
        "safe",
        "unsafe",
        "user safety: safe",
        "user safety: unsafe",
    }:

        raise RuntimeError(
            "The selected model returned a safety-classification "
            "response instead of the requested clinical assessment."
        )

    return answer