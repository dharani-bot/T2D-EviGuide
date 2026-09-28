from llm_client import ask_llm


def verify_assessment(assessment, evidence):
    """
    Verify whether important claims in a generated clinical
    assessment are supported by the retrieved evidence.

    Classifications:

        SUPPORTED
        PARTIALLY SUPPORTED
        NOT ESTABLISHED
        CONTRADICTED

    The verifier is deliberately conservative. In particular,
    it does not treat absence of evidence as evidence.
    """

    # =========================================================
    # BUILD EVIDENCE TEXT
    # =========================================================

    evidence_text = ""

    for item in evidence:

        evidence_text += f"""
Evidence {item['evidence_number']}

Stable Evidence ID:
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

PMC ID:
{item.get('pmc_id', '')}

Evidence Type:
{item.get('section', '')}

Retrieved text:
{item.get('text', '')}

------------------------------------------------------------
"""

    # =========================================================
    # VERIFICATION PROMPT
    # =========================================================

    verification_question = f"""
You are an evidence verification component for a clinical
decision-support research prototype.

Your task is to audit the generated clinical assessment against
ONLY the patient information contained in the assessment and
the retrieved medical evidence supplied below.

The verifier must be conservative.

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

Use exactly ONE classification for every important claim.

------------------------------------------------------------
SUPPORTED
------------------------------------------------------------

Use SUPPORTED only when:

1. The claim is explicitly stated or directly established by
   the supplied evidence; OR

2. The claim is a direct factual statement about patient data
   explicitly contained in the generated assessment.

Examples:

"The patient's HbA1c is 5.7%."

SUPPORTED as a patient-data statement.

"An HbA1c of 5.7% falls within the 5.7%–6.4% range described
as prediabetes in Evidence 3."

SUPPORTED if Evidence 3 explicitly states that range.


------------------------------------------------------------
PARTIALLY SUPPORTED
------------------------------------------------------------

Use PARTIALLY SUPPORTED when only part of the claim is
supported.

Example:

"The patient meets the screening criteria because of age and
BMI."

If the evidence supports the age component but does not support
the BMI component:

PARTIALLY SUPPORTED


------------------------------------------------------------
NOT ESTABLISHED
------------------------------------------------------------

Use NOT ESTABLISHED when:

- the evidence is silent;
- the evidence is insufficient;
- the claim requires an inference not explicitly supported;
- the evidence is incomplete;
- the claim depends on absence of evidence;
- a clinical category or threshold was inferred from outside
  medical knowledge;
- a factor is called protective without explicit supporting
  evidence;
- a factor is called a risk factor without explicit supporting
  evidence.

Examples:

"The patient's BMI is normal."

If the retrieved evidence does not provide the relevant BMI
classification threshold:

NOT ESTABLISHED

"Never smoking is protective."

If the evidence does not explicitly establish this:

NOT ESTABLISHED

"Absence of family history is protective."

If the evidence only mentions family history as a risk factor
but does not explicitly establish absence of family history as
protective:

NOT ESTABLISHED


------------------------------------------------------------
CONTRADICTED
------------------------------------------------------------

Use CONTRADICTED only when the supplied evidence directly
conflicts with the claim.

Do NOT use CONTRADICTED merely because evidence is missing.


============================================================
CRITICAL RULE: ABSENCE OF EVIDENCE
============================================================

Never reason:

"The article does not mention X, therefore X is false."

Never reason:

"The retrieved evidence does not mention X, therefore X is
not a risk factor."

Never reason:

"No evidence of X was retrieved, therefore X is protective."

Statements based on absence of information should normally be
classified as NOT ESTABLISHED.


============================================================
PATIENT DATA VS CLINICAL INTERPRETATION
============================================================

Separate factual patient data from clinical interpretation.

The following can be SUPPORTED as patient-data statements if
they match the generated assessment:

- age
- sex
- weight
- height
- BMI value
- fasting glucose value
- HbA1c value
- blood pressure value
- family-history entry
- physical-activity entry
- smoking entry
- medical-history entry
- medication entry

However, the following require medical evidence:

"The patient's BMI is normal."

"The patient's blood pressure is normal."

"The patient's HbA1c indicates prediabetes."

"The patient's age increases diabetes risk."

"Hypertension is a Type 2 Diabetes risk factor."

"Low physical activity is a Type 2 Diabetes risk factor."

"No family history is protective."

"Never smoking is protective."


============================================================
CLINICAL THRESHOLD RULE
============================================================

A clinical threshold can be classified as SUPPORTED only if
the supplied evidence explicitly contains the relevant
threshold.

For example:

If evidence states:

"HbA1c 5.7% to 6.4%"

then a claim about that range may be SUPPORTED.

If evidence merely says:

"HbA1c is useful for diagnosis"

then a numerical threshold must be NOT ESTABLISHED.

Do not infer thresholds from general medical knowledge.


============================================================
RISK FACTOR RULE
============================================================

A factor is a supported Type 2 Diabetes risk factor only if
the supplied evidence explicitly establishes that relationship.

Do NOT classify a factor as a risk factor simply because:

- it appears in a patient history;
- it is mentioned as a comorbidity;
- it occurs in a guideline;
- it is medically plausible;
- it appears near diabetes-related information.


============================================================
PROTECTIVE FACTOR RULE
============================================================

A factor may be called protective, lower-risk, or risk-reducing
only when the supplied evidence explicitly supports that
interpretation.

Do NOT infer protection from:

- absence of a risk factor;
- a value that appears low or normal;
- lack of medication;
- lack of symptoms;
- lack of family history;
- absence of smoking;
- absence of obesity.

If the evidence does not explicitly support protection:

NOT ESTABLISHED


============================================================
SCREENING VS DIAGNOSIS
============================================================

Do not confuse:

- screening eligibility,
- risk-factor assessment,
- prediabetes classification,
- diabetes diagnosis,
- treatment eligibility.

If evidence supports screening for a population, that does not
automatically establish that the patient has the disease.

If evidence supports a prediabetes range, do not automatically
call it a diabetes diagnosis.

If evidence describes established Type 2 Diabetes management,
do not assume it applies to an undiagnosed screening patient.


============================================================
SOURCE RELEVANCE RULE
============================================================

Consider whether the cited evidence is actually relevant to the
claim.

For example, evidence describing difficult-to-control Type 2
Diabetes in patients receiving multiple medications should not
be used as primary support for an initial screening conclusion
unless the claim is directly supported.

An article can be scientifically valid but still be irrelevant
to a particular claim.


============================================================
EVIDENCE CITATION RULE
============================================================

The generated assessment may cite evidence using:

[Evidence N | ARTICLE_ID]

Verify BOTH:

1. The evidence number exists.
2. The ARTICLE_ID matches the supplied evidence.

If the citation refers to a nonexistent evidence item or
incorrect article ID, the claim cannot be considered fully
supported by that citation.


============================================================
"DOES NOT ESTABLISH" CLAIMS
============================================================

Some generated claims may state:

"The retrieved evidence does not establish X."

Do not automatically classify these as SUPPORTED.

Classify such a statement as SUPPORTED only when the supplied
retrieved material is sufficient to determine that the required
information is genuinely absent or insufficient.

If the retrieved material is incomplete or the claim concerns
information outside the retrieved passages:

NOT ESTABLISHED

The verifier must not pretend to know what an entire article
contains when only a retrieved passage was supplied.


============================================================
CLAIM DECOMPOSITION
============================================================

Break compound statements into separate claims when necessary.

Example:

"The patient has normal BMI and normal blood pressure."

This contains at least two clinical claims:

1. BMI is normal.
2. Blood pressure is normal.

Evaluate them independently.

Similarly:

"The patient has increased risk because of age, hypertension,
and low physical activity."

Evaluate the evidence for each factor separately.


============================================================
IMPORTANT RULES
============================================================

1. Use ONLY the supplied evidence and patient information.

2. Do NOT use outside medical knowledge.

3. Do NOT add new clinical facts.

4. Do NOT assume a medically plausible statement is supported.

5. Do NOT infer a risk factor from a comorbidity.

6. Do NOT infer a protective factor from absence of a risk
   factor.

7. Do NOT infer diagnostic thresholds.

8. Do NOT infer the contents of an algorithm merely because the
   article mentions that algorithm.

9. Do NOT treat evidence silence as positive evidence.

10. Do NOT classify an entire paragraph as supported because
    one sentence is supported.

11. Evaluate important clinical claims independently.

12. Be conservative.

13. If uncertain between SUPPORTED and NOT ESTABLISHED,
    choose NOT ESTABLISHED.

14. If uncertain between SUPPORTED and PARTIALLY SUPPORTED,
    choose PARTIALLY SUPPORTED when a meaningful part of the
    claim is supported but another part is not.

15. Do not provide a diagnosis.

16. Do not provide treatment recommendations.

17. Do not recommend starting, stopping, or changing medication.

18. Do not provide medication doses.

============================================================
OUTPUT FORMAT
============================================================

Use exactly this structure:

Claim 1:
[claim]

Evidence:
[Evidence N | ARTICLE_ID, patient data, or None]

Classification:
SUPPORTED / PARTIALLY SUPPORTED /
NOT ESTABLISHED / CONTRADICTED

Explanation:
[brief explanation]

---

Claim 2:
[claim]

Evidence:
[Evidence N | ARTICLE_ID, patient data, or None]

Classification:
SUPPORTED / PARTIALLY SUPPORTED /
NOT ESTABLISHED / CONTRADICTED

Explanation:
[brief explanation]

---

Continue for the important clinical claims.

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

    # =========================================================
    # CALL LLM
    # =========================================================

    verification = ask_llm(
        verification_question,
        evidence
    )

    return verification


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    from clinical_assessment import generate_risk_assessment

    # ---------------------------------------------------------
    # Synthetic test patient
    # ---------------------------------------------------------

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
    print("=" * 50)
    print("T2D-EviGuide Evidence Verification")
    print("=" * 50)
    print()

    # ---------------------------------------------------------
    # Generate assessment
    # ---------------------------------------------------------

    result = generate_risk_assessment(
        test_patient,
        top_k=3
    )

    if not result["success"]:

        print(
            "Assessment generation failed."
        )

        print()

        print(
            result["assessment"]
        )

    else:

        # -----------------------------------------------------
        # Show original assessment
        # -----------------------------------------------------

        print(
            "===== ORIGINAL ASSESSMENT ====="
        )

        print()

        print(
            result["assessment"]
        )

        # -----------------------------------------------------
        # Run verifier
        # -----------------------------------------------------

        print()

        print(
            "=" * 50
        )

        print(
            "===== EVIDENCE VERIFICATION ====="
        )

        print(
            "=" * 50
        )

        print()

        try:

            verification = verify_assessment(
                result["assessment"],
                result["evidence"]
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