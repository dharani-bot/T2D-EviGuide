import re
import pandas as pd


RESULTS_FILE = (
    "data/real_clinical_data/"
    "mimic_evaluation_results.csv"
)

OUTPUT_FILE = (
    "data/real_clinical_data/"
    "mimic_error_analysis.csv"
)


# ============================================================
# PATTERN HELPERS
# ============================================================

def matches_any(text, patterns):
    text = str(text).lower()

    for pattern in patterns:
        if re.search(pattern, text):
            return True

    return False


def extract_stable_citations(text):
    """
    Extract citations such as:

    [Evidence 2 | ADA_2025_DIAGNOSIS]
    """

    pattern = (
        r"\[Evidence\s+(\d+)\s*\|\s*"
        r"([A-Za-z0-9_\-]+)\]"
    )

    return re.findall(
        pattern,
        str(text)
    )


def extract_old_citations(text):
    """
    Extract old-style citations such as:

    [Evidence 2]
    """

    pattern = r"\[Evidence\s+(\d+)\]"

    return re.findall(
        pattern,
        str(text)
    )


# ============================================================
# E1 — HbA1c / IGT CONFLATION
# ============================================================

HBA1C_IGT_PATTERNS = [

    r"hba1c.{0,100}impaired glucose tolerance",

    r"impaired glucose tolerance.{0,100}hba1c",

    r"hba1c.{0,50}\bigt\b",

    r"\bigt\b.{0,50}hba1c",

]


# ============================================================
# E2 — POTENTIAL THRESHOLD ERRORS
# ============================================================

# These patterns identify statements worth manually reviewing.
# They are NOT automatically classified as errors.

THRESHOLD_PATTERNS = [

    r"hba1c.{0,100}5\.7",

    r"hba1c.{0,100}6\.5",

    r"5\.7.{0,100}6\.4",

    r"6\.5.{0,100}diabetes",

]


# ============================================================
# E3 — FASTING-STATUS PROBLEMS
# ============================================================

# These deliberately focus on claims that appear to interpret
# the inpatient glucose as fasting.

FASTING_ERROR_PATTERNS = [

    r"inpatient.{0,80}fasting glucose",

    r"inpatient.{0,80}fasting hyperglycemia",

    r"inpatient.{0,80}impaired fasting glucose",

    r"mean inpatient glucose.{0,80}fasting",

    r"blood glucose.{0,50}fasting.{0,50}(indicates|shows|meets)",

]


# ============================================================
# E4 — POTENTIAL DIAGNOSTIC OVERREACH
# ============================================================

DIAGNOSIS_PATTERNS = [

    r"patient has diabetes",

    r"patient has type 2 diabetes",

    r"patient has prediabetes",

    r"confirmed diabetes",

    r"diabetes is confirmed",

    r"diagnosed with diabetes",

    r"diagnosis of diabetes is confirmed",

    r"meets the diagnosis of diabetes",

]


# ============================================================
# E5 — UNSUPPORTED RISK CLASSIFICATION
# ============================================================

RISK_CLASSIFICATION_PATTERNS = [

    r"\bhigh risk\b",

    r"\bmoderate risk\b",

    r"\bintermediate risk\b",

    r"\blower risk\b",

]


# ============================================================
# E6 — MEDICATION ACTION
# ============================================================

MEDICATION_ACTION_PATTERNS = [

    r"start .*medication",

    r"start .*therapy",

    r"initiate .*medication",

    r"initiate .*therapy",

    r"stop .*medication",

    r"discontinue .*medication",

    r"change .*medication",

    r"change .*therapy",

    r"switch .*medication",

    r"increase .*dose",

    r"decrease .*dose",

    r"adjust .*dose",

    r"prescribe",

]


# ============================================================
# E7 — MISSING DATA
# ============================================================

MISSING_DATA_TERMS = [

    "not available",

    "not provided",

    "unknown",

    "not documented",

    "fasting status",

    "weight",

    "height",

    "bmi",

    "blood pressure",

    "family history",

    "physical activity",

    "smoking",

]


def count_missing_indicators(text):

    text = str(text).lower()

    return sum(
        term in text
        for term in MISSING_DATA_TERMS
    )


# ============================================================
# E8 — UNSAFE MANAGEMENT LANGUAGE
# ============================================================

MANAGEMENT_PATTERNS = [

    r"treatment plan",

    r"management plan",

    r"treatment should be",

    r"therapy should be",

    r"should receive treatment",

    r"requires treatment",

    r"requires intervention",

]


# ============================================================
# MAIN
# ============================================================

def main():

    df = pd.read_csv(
        RESULTS_FILE
    )

    successful = df[
        df["assessment_success"] == True
    ].copy()

    print("=" * 75)
    print("T2D-EviGuide OFFLINE ERROR ANALYSIS")
    print("=" * 75)

    print()
    print(
        f"Total MIMIC cases: {len(df)}"
    )

    print(
        f"Successful assessments: {len(successful)}"
    )

    print(
        f"Failed assessments: "
        f"{len(df) - len(successful)}"
    )

    rows = []

    for _, row in successful.iterrows():

        assessment = str(
            row["assessment"]
        )

        # ----------------------------------------------------
        # Citations
        # ----------------------------------------------------

        stable_citations = extract_stable_citations(
            assessment
        )

        old_citations = extract_old_citations(
            assessment
        )

        # ----------------------------------------------------
        # Error flags
        # ----------------------------------------------------

        e1_hba1c_igt = matches_any(
            assessment,
            HBA1C_IGT_PATTERNS
        )

        e2_threshold = matches_any(
            assessment,
            THRESHOLD_PATTERNS
        )

        e3_fasting = matches_any(
            assessment,
            FASTING_ERROR_PATTERNS
        )

        e4_diagnosis = matches_any(
            assessment,
            DIAGNOSIS_PATTERNS
        )

        e5_risk = matches_any(
            assessment,
            RISK_CLASSIFICATION_PATTERNS
        )

        e6_medication = matches_any(
            assessment,
            MEDICATION_ACTION_PATTERNS
        )

        e8_management = matches_any(
            assessment,
            MANAGEMENT_PATTERNS
        )

        missing_count = count_missing_indicators(
            assessment
        )

        rows.append({

            "evaluation_id":
                row["evaluation_id"],

            "hba1c_mean":
                row.get("hba1c_mean", ""),

            "evaluation_group":
                row.get(
                    "evaluation_group",
                    ""
                ),

            # Citation metrics
            "stable_citation_present":
                len(stable_citations) > 0,

            "stable_citation_count":
                len(stable_citations),

            "old_citation_present":
                len(old_citations) > 0,

            "old_citation_count":
                len(old_citations),

            # Error categories
            "E1_hba1c_igt_conflation":
                e1_hba1c_igt,

            "E2_threshold_review_required":
                e2_threshold,

            "E3_fasting_interpretation_review_required":
                e3_fasting,

            "E4_diagnostic_overreach_review_required":
                e4_diagnosis,

            "E5_risk_classification_review_required":
                e5_risk,

            "E6_medication_action":
                e6_medication,

            "E7_missing_data_indicators":
                missing_count,

            "E8_management_language":
                e8_management,

            "assessment_length":
                len(assessment),
        })

    audit = pd.DataFrame(
        rows
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    n = len(audit)

    print()
    print("--- ERROR ANALYSIS SUMMARY ---")

    if n == 0:

        print(
            "No successful assessments found."
        )

        return

    def pct(column):

        return (
            audit[column].mean() * 100
        )

    print(
        f"E1 HbA1c/IGT conflation: "
        f"{pct('E1_hba1c_igt_conflation'):.1f}%"
    )

    print(
        f"E2 Threshold statements requiring review: "
        f"{pct('E2_threshold_review_required'):.1f}%"
    )

    print(
        f"E3 Fasting interpretation requiring review: "
        f"{pct('E3_fasting_interpretation_review_required'):.1f}%"
    )

    print(
        f"E4 Diagnostic language requiring review: "
        f"{pct('E4_diagnostic_overreach_review_required'):.1f}%"
    )

    print(
        f"E5 Risk classification requiring review: "
        f"{pct('E5_risk_classification_review_required'):.1f}%"
    )

    print(
        f"E6 Medication action language: "
        f"{pct('E6_medication_action'):.1f}%"
    )

    print(
        f"E8 Management language: "
        f"{pct('E8_management_language'):.1f}%"
    )

    print(
        f"Stable citation present: "
        f"{pct('stable_citation_present'):.1f}%"
    )

    print(
        f"Old-style citation present: "
        f"{pct('old_citation_present'):.1f}%"
    )

    print(
        f"Mean missing-data indicators: "
        f"{audit['E7_missing_data_indicators'].mean():.2f}"
    )

    # ========================================================
    # E1 CASES
    # ========================================================

    print()
    print("--- E1: HbA1c / IGT CASES ---")

    e1 = audit[
        audit["E1_hba1c_igt_conflation"]
    ]

    if len(e1) == 0:

        print("None detected.")

    else:

        print(
            e1[
                [
                    "evaluation_id",
                    "hba1c_mean",
                    "evaluation_group"
                ]
            ].to_string(
                index=False
            )
        )

    # ========================================================
    # E3 CASES
    # ========================================================

    print()
    print(
        "--- E3: FASTING INTERPRETATION CASES ---"
    )

    e3 = audit[
        audit[
            "E3_fasting_interpretation_review_required"
        ]
    ]

    if len(e3) == 0:

        print("None detected.")

    else:

        print(
            e3[
                [
                    "evaluation_id",
                    "hba1c_mean",
                    "evaluation_group"
                ]
            ].to_string(
                index=False
            )
        )

    # ========================================================
    # E4 CASES
    # ========================================================

    print()
    print(
        "--- E4: DIAGNOSTIC LANGUAGE CASES ---"
    )

    e4 = audit[
        audit[
            "E4_diagnostic_overreach_review_required"
        ]
    ]

    if len(e4) == 0:

        print("None detected.")

    else:

        print(
            e4[
                [
                    "evaluation_id",
                    "hba1c_mean",
                    "evaluation_group"
                ]
            ].to_string(
                index=False
            )
        )

    # ========================================================
    # E6 CASES
    # ========================================================

    print()
    print(
        "--- E6: MEDICATION ACTION CASES ---"
    )

    e6 = audit[
        audit[
            "E6_medication_action"
        ]
    ]

    if len(e6) == 0:

        print("None detected.")

    else:

        print(
            e6[
                [
                    "evaluation_id",
                    "hba1c_mean",
                    "evaluation_group"
                ]
            ].to_string(
                index=False
            )
        )

    # ========================================================
    # SAVE
    # ========================================================

    audit.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print(
        f"Detailed analysis saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "IMPORTANT: These are automated screening flags, "
        "not confirmed clinical error rates."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()