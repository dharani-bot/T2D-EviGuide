from llm_client import ask_llm
from evidence_package import build_evidence_package


# ============================================================
# T2D-EviGuide
# Evidence Verification Module
# ============================================================
#
# Purpose:
#   Verify whether important claims in a generated clinical
#   assessment are supported by the retrieved evidence.
#
# Classifications:
#
#   SUPPORTED
#   PARTIALLY SUPPORTED
#   NOT ESTABLISHED
#   CONTRADICTED
#
# The verifier is deliberately conservative.
#
# ============================================================


# ============================================================
# BUILD EVIDENCE TEXT
# ============================================================

def build_evidence_text(evidence):
    """
    Convert the structured evidence package into a stable
    representation for the verification model.
    """

    if not evidence:
        return "NO RETRIEVED EVIDENCE WAS PROVIDED."

    evidence_blocks = []

    for item in evidence:

        block = f"""
============================================================
EVIDENCE {item.get("evidence_number", "")}
============================================================

Stable Evidence ID:
{item.get("article_id", "")}

Title:
{item.get("title", "")}

Source:
{item.get("source", "")}

Year:
{item.get("year", "")}

Category:
{item.get("category", "")}

PMID:
{item.get("pmid", "")}

DOI:
{item.get("doi", "")}

PMC ID:
{item.get("pmc_id", "")}

Evidence Type:
{item.get("section", "")}

Retrieved Evidence Text:
{item.get("text", "")}

============================================================
"""

        evidence_blocks.append(block)

    return "\n".join(evidence_blocks)


# ============================================================
# BUILD VERIFICATION PROMPT
# ============================================================

def build_verification_prompt(
    assessment,
    evidence
):
    """
    Build a conservative evidence-verification prompt.
    """

    evidence_text = build_evidence_text(
        evidence
    )

    return f"""
You are the evidence-verification component of
T2D-EviGuide, an academic research prototype for
evidence-grounded early Type 2 Diabetes risk assessment.

Your task is to audit a generated clinical assessment against
ONLY:

1. Patient information explicitly contained in the assessment.
2. Retrieved medical evidence supplied below.

You MUST NOT use outside medical knowledge.

You are NOT generating a diagnosis.
You are NOT generating treatment advice.
You are NOT deciding what disease the patient has.

Your task is ONLY to determine whether important claims in the
generated assessment are supported by the supplied information.

============================================================
GENERATED ASSESSMENT
============================================================

{assessment}


============================================================
RETRIEVED MEDICAL EVIDENCE
============================================================

{evidence_text}


============================================================
CLASSIFICATIONS
============================================================

Use exactly ONE classification for every important claim:

SUPPORTED

PARTIALLY SUPPORTED

NOT ESTABLISHED

CONTRADICTED


============================================================
SUPPORTED
============================================================

Use SUPPORTED only when the claim is directly established by
the supplied information.

A claim may be SUPPORTED when:

1. It is an explicit patient-data statement and the value is
   explicitly present in the assessment.

OR

2. The retrieved evidence explicitly establishes the clinical
   interpretation.

OR

3. The claim is a direct application of an explicitly stated
   threshold to an explicitly stated patient value.

Example:

Patient data:
HbA1c = 5.7%

Evidence:
HbA1c 5.7%–6.4% is described as an increased-risk range.

Claim:
"The patient's HbA1c of 5.7% falls within the retrieved
5.7%–6.4% range."

Classification:
SUPPORTED


============================================================
PARTIALLY SUPPORTED
============================================================

Use PARTIALLY SUPPORTED when a compound claim contains both
supported and unsupported components.

Example:

"The patient's increased risk is related to age, hypertension,
and low physical activity."

If evidence supports hypertension and physical activity but
does not establish age:

PARTIALLY SUPPORTED


============================================================
NOT ESTABLISHED
============================================================

Use NOT ESTABLISHED when:

- the evidence is silent;
- the retrieved passage is insufficient;
- the claim requires outside medical knowledge;
- a numerical threshold is not present;
- a risk-factor relationship is not explicitly established;
- a protective interpretation is inferred;
- a normal/abnormal classification is inferred without
  supporting evidence;
- the assessment extrapolates beyond the supplied evidence.

Examples:

"The patient's BMI is normal."

If the supplied evidence does not provide the BMI threshold:

NOT ESTABLISHED

"Never smoking is protective."

If the supplied evidence does not explicitly establish this:

NOT ESTABLISHED


============================================================
CONTRADICTED
============================================================

Use CONTRADICTED only when the supplied evidence directly
conflicts with the claim.

Do NOT use CONTRADICTED merely because evidence is missing.

Unsupported does NOT mean contradicted.


============================================================
ABSENCE OF EVIDENCE
============================================================

Never reason:

"The evidence does not mention X, therefore X is false."

Never reason:

"The evidence does not mention X, therefore X is not a risk
factor."

Never reason:

"No evidence of X was retrieved, therefore X is protective."

Such claims should normally be classified:

NOT ESTABLISHED


============================================================
PATIENT DATA VS CLINICAL INTERPRETATION
============================================================

Separate factual patient data from clinical interpretation.

The following may be SUPPORTED as patient-data statements if
explicitly present:

- age
- sex
- weight
- height
- BMI value
- blood glucose value
- fasting status
- HbA1c value
- systolic blood pressure
- diastolic blood pressure
- family history
- physical activity
- smoking
- medical history
- medications

However, these require medical evidence:

"The patient's BMI is normal."

"The patient's blood pressure is normal."

"The patient's HbA1c indicates increased risk."

"The patient's HbA1c indicates prediabetes."

"The patient's age increases Type 2 Diabetes risk."

"Hypertension is a Type 2 Diabetes risk factor."

"Low physical activity is a Type 2 Diabetes risk factor."

"No family history is protective."

"Never smoking is protective."


============================================================
CLINICAL THRESHOLD RULE
============================================================

A clinical threshold can be SUPPORTED only if the supplied
evidence explicitly contains that threshold.

Do NOT infer thresholds from general medical knowledge.

For example:

If evidence explicitly states:

"HbA1c 5.7% to 6.4%"

then a claim using that range may be SUPPORTED.

If evidence merely says:

"HbA1c is useful for diagnosis"

then a numerical threshold is:

NOT ESTABLISHED


============================================================
MEASUREMENT TYPE RULE
============================================================

Keep these measurements distinct:

- fasting glucose
- random glucose
- 2-hour OGTT glucose
- HbA1c

Do NOT convert one measurement type into another.

Example:

Blood glucose = 100 mg/dL
Fasting status = Unknown

The verifier must NOT convert this into:

Fasting glucose = 100 mg/dL

Therefore a claim such as:

"The patient has impaired fasting glucose"

cannot be SUPPORTED unless fasting status is established and
the supplied evidence provides the relevant threshold.


============================================================
RISK FACTOR RULE
============================================================

A factor is a supported Type 2 Diabetes risk factor only if
the supplied evidence explicitly establishes that relationship.

Do NOT infer a risk-factor relationship simply because:

- the factor appears in medical history;
- it appears in a guideline;
- it is medically plausible;
- it occurs as a comorbidity;
- it appears near diabetes information.


============================================================
PROTECTIVE FACTOR RULE
============================================================

Be especially conservative with protective language.

The following require explicit evidence:

- protective
- protective factor
- lower risk
- risk reducing
- risk-reducing
- favorable factor

Do NOT infer protection from:

- no family history;
- never smoking;
- normal BMI;
- normal blood pressure;
- lack of medication;
- lack of symptoms;
- absence of obesity.


============================================================
NORMAL / ABNORMAL RULE
============================================================

Terms such as:

- normal
- abnormal
- elevated
- low
- high
- obese
- overweight
- underweight

may represent clinical classifications.

Do NOT classify such statements as SUPPORTED unless the
supplied evidence establishes the relevant classification
or threshold.


============================================================
SCREENING VS DIAGNOSIS
============================================================

Keep these concepts separate:

- screening
- risk assessment
- increased-risk classification
- prediabetes
- diabetes diagnosis
- treatment

Evidence about screening does not automatically establish
disease.

Evidence about an increased-risk range does not automatically
establish diabetes.

Evidence about established Type 2 Diabetes management does not
automatically apply to an undiagnosed screening patient.


============================================================
SOURCE RELEVANCE RULE
============================================================

The evidence must be relevant to the specific claim.

A scientifically valid article is not automatically support
for every claim.

Evidence about established Type 2 Diabetes treatment should
not automatically support an initial screening conclusion.


============================================================
EVIDENCE CITATION RULE
============================================================

The assessment may cite:

[Evidence N]

or:

[Evidence N | ARTICLE_ID]

For every citation verify:

1. Evidence N exists.
2. ARTICLE_ID matches the supplied evidence when provided.
3. The cited passage actually supports the claim.

If the evidence number does not exist:

NOT ESTABLISHED

If the article ID does not match:

NOT ESTABLISHED

If the citation exists but the passage does not support the
claim:

NOT ESTABLISHED


============================================================
CLAIM DECOMPOSITION
============================================================

Break compound claims into separate claims.

Example:

"The patient's BMI is normal and blood pressure is normal."

Evaluate:

1. BMI classification.
2. Blood-pressure classification.

If one is supported and one is not:

PARTIALLY SUPPORTED


============================================================
IMPORTANT RULES
============================================================

1. Use ONLY supplied patient information and evidence.

2. Do NOT use outside medical knowledge.

3. Do NOT add new clinical facts.

4. Do NOT assume medically plausible statements are supported.

5. Do NOT infer risk factors from comorbidities.

6. Do NOT infer protective factors from absence of risk factors.

7. Do NOT infer diagnostic thresholds.

8. Do NOT infer article contents beyond retrieved passages.

9. Do NOT treat evidence silence as positive evidence.

10. Evaluate important clinical claims independently.

11. Be conservative.

12. If uncertain between SUPPORTED and NOT ESTABLISHED,
    choose NOT ESTABLISHED.

13. If uncertain between SUPPORTED and PARTIALLY SUPPORTED,
    choose PARTIALLY SUPPORTED when appropriate.

14. Do not provide a diagnosis.

15. Do not provide treatment recommendations.

16. Do not recommend starting, stopping, or changing medication.

17. Do not provide medication doses.


============================================================
OUTPUT FORMAT
============================================================

Use exactly:

Claim 1:
[claim]

Evidence:
[Evidence N | ARTICLE_ID / Patient Data / None]

Classification:
SUPPORTED / PARTIALLY SUPPORTED / NOT ESTABLISHED / CONTRADICTED

Explanation:
[brief explanation]

---

Claim 2:
[claim]

Evidence:
[Evidence N | ARTICLE_ID / Patient Data / None]

Classification:
SUPPORTED / PARTIALLY SUPPORTED / NOT ESTABLISHED / CONTRADICTED

Explanation:
[brief explanation]

---

Continue for important clinical claims.

============================================================
SUMMARY
============================================================

At the end provide:

Summary:

- Number of SUPPORTED claims: X
- Number of PARTIALLY SUPPORTED claims: X
- Number of NOT ESTABLISHED claims: X
- Number of CONTRADICTED claims: X

Overall evidence-grounding quality:

[One short explanation.]

Do not provide a diagnosis.

Do not provide treatment recommendations.

Do not recommend starting, stopping, or changing medication.
"""

    return verification_question


# ============================================================
# PUBLIC VERIFICATION FUNCTION
# ============================================================

def verify_assessment(
    assessment,
    evidence
):
    """
    Verify important claims in a generated assessment.

    Parameters
    ----------
    assessment : str
        Generated clinical assessment.

    evidence : list
        Retrieved evidence package.

    Returns
    -------
    str
        Evidence verification report.
    """

    if not assessment:
        return (
            "Evidence verification could not be performed "
            "because no assessment was supplied."
        )

    if evidence is None:
        evidence = []

    prompt = build_verification_prompt(
        assessment=assessment,
        evidence=evidence
    )

    try:

        verification = ask_llm(
            prompt,
            evidence
        )

    except Exception as error:

        return (
            "Evidence verification failed.\n\n"
            f"Error: {error}"
        )

    if not verification:

        return (
            "Evidence verification returned no result."
        )

    return verification


# ============================================================
# TEST QUERY
# ============================================================

TEST_QUERY = """
What evidence-based thresholds and measurement distinctions
are relevant when assessing early Type 2 Diabetes risk using
HbA1c and blood glucose, including fasting glucose, random
glucose, and 2-hour OGTT glucose?
"""


# ============================================================
# SYNTHETIC ASSESSMENT FOR VERIFICATION TEST
# ============================================================

TEST_ASSESSMENT = """
# Evidence-Grounded Assessment of Early Type 2 Diabetes Risk

## 1. Overall Evidence-Supported Interpretation

The patient is a 45-year-old female with an HbA1c of 5.7% and
a blood glucose value of 100 mg/dL. The fasting status of the
blood glucose measurement is unknown.

The retrieved evidence describes HbA1c values in the
5.7%–6.4% range as an increased-risk or prediabetes range.

Because the fasting status of the 100 mg/dL glucose measurement
is unknown, it should not be classified using a fasting-glucose
threshold.

## 2. Key Risk Indicators

- HbA1c: 5.7%
- Blood glucose: 100 mg/dL
- Fasting status: Unknown

The HbA1c value can be interpreted using the retrieved
HbA1c threshold.

The blood glucose value cannot be classified as fasting glucose
because fasting status is unknown.

## 3. Relevant Clinical Measurements

BMI: 24.2 kg/m²
Blood pressure: 120/80 mmHg
Medical history: Hypertension
Physical activity: Low
Smoking: Never
Family history: No

## 4. Lower-Risk or Unremarkable Findings

The patient's BMI of 24.2 kg/m² is normal.

The patient's blood pressure of 120/80 mmHg is normal.

Never smoking and absence of family history are protective
factors.

## 5. Missing or Uncertain Information

Fasting status of the blood glucose measurement is unknown.

## 6. Evidence-Based Interpretation

HbA1c of 5.7% falls within the retrieved 5.7%–6.4%
increased-risk range.

The blood glucose value of 100 mg/dL cannot be classified as
impaired fasting glucose because fasting status is unknown.

## 7. Important Limitations

The available evidence must be applied only to the appropriate
measurement type.
"""


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("T2D-EviGuide Evidence Verification Test")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Retrieve evidence directly.
    #
    # IMPORTANT:
    # We do NOT call run_clinical_assessment() here.
    #
    # This avoids:
    #   - a second assessment-generation LLM call
    #   - OpenRouter/free-model limits
    #   - safety-classification response problems
    # --------------------------------------------------------

    print(
        "Retrieving evidence..."
    )

    evidence = build_evidence_package(
        TEST_QUERY,
        top_k=3
    )

    print(
        f"Retrieved evidence items: {len(evidence)}"
    )

    print()

    if not evidence:

        print(
            "No evidence was retrieved."
        )

        print()
        print(
            "The verifier cannot perform a meaningful "
            "evidence-grounding test without retrieved evidence."
        )

        raise SystemExit(1)

    # --------------------------------------------------------
    # Display evidence
    # --------------------------------------------------------

    print(
        "===== RETRIEVED EVIDENCE ====="
    )

    print()

    for item in evidence:

        print(
            f"Evidence {item.get('evidence_number')}"
        )

        print(
            f"Article ID: "
            f"{item.get('article_id', '')}"
        )

        print(
            f"Title: "
            f"{item.get('title', '')}"
        )

        print(
            f"PMID: "
            f"{item.get('pmid', '')}"
        )

        print(
            f"Relevance score: "
            f"{item.get('relevance_score', 0)}"
        )

        print(
            f"Text: "
            f"{item.get('text', '')[:500]}"
        )

        print()

    # --------------------------------------------------------
    # Display synthetic assessment
    # --------------------------------------------------------

    print(
        "=" * 70
    )

    print(
        "===== TEST ASSESSMENT ====="
    )

    print(
        "=" * 70
    )

    print()

    print(
        TEST_ASSESSMENT
    )

    # --------------------------------------------------------
    # Run verifier
    # --------------------------------------------------------

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

    try:

        verification = verify_assessment(
            TEST_ASSESSMENT,
            evidence
        )

        print(
            verification
        )

    except Exception as error:

        print(
            "Evidence verification failed."
        )

        print()

        print(
            f"Error: {error}"
        )