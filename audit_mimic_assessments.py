import re
import pandas as pd


RESULTS_FILE = "data/real_clinical_data/mimic_evaluation_results.csv"


# ============================================================
# PATTERN DEFINITIONS
# ============================================================

# Potential HbA1c / IGT confusion
HBA1C_IGT_PATTERNS = [
    r"hba1c.*impaired glucose tolerance",
    r"impaired glucose tolerance.*hba1c",
    r"hba1c.*\bIGT\b",
    r"\bIGT\b.*hba1c",
]

# Incorrect fasting interpretation
FASTING_ERROR_PATTERNS = [
    r"fasting blood glucose.*\d",
    r"fasting glucose.*\d",
    r"fasting hyperglycemia",
    r"impaired fasting glucose",
]

# Potential diagnostic overreach
DIAGNOSIS_PATTERNS = [
    r"confirms diabetes",
    r"confirmed diabetes",
    r"patient has diabetes",
    r"patient has prediabetes",
    r"diagnosed with diabetes",
    r"diagnosis of diabetes",
    r"meets.*diagnosis",
]

# Medication action language
MEDICATION_ACTION_PATTERNS = [
    r"start .*medication",
    r"start .*therapy",
    r"initiate .*medication",
    r"initiate .*therapy",
    r"stop .*medication",
    r"discontinue .*medication",
    r"change .*medication",
    r"change .*therapy",
    r"increase .*dose",
    r"decrease .*dose",
    r"adjust .*dose",
    r"prescribe",
]

# Missing information indicators
MISSING_DATA_TERMS = [
    "not available",
    "not provided",
    "unknown",
    "not documented",
    "fasting status",
    "bmi",
    "blood pressure",
    "family history",
    "physical activity",
    "smoking",
]


def contains_pattern(text, patterns):

    text = str(text).lower()

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


def extract_citations(text):

    pattern = r"\[Evidence\s+(\d+)\s*\|\s*([A-Za-z0-9_\-]+)\]"

    return re.findall(
        pattern,
        str(text)
    )


def extract_old_style_citations(text):

    pattern = r"\[Evidence\s+(\d+)\]"

    return re.findall(
        pattern,
        str(text)
    )


def count_missing_data_indicators(text):

    text = str(text).lower()

    return sum(
        term in text
        for term in MISSING_DATA_TERMS
    )


def main():

    df = pd.read_csv(
        RESULTS_FILE
    )

    successful = df[
        df["assessment_success"] == True
    ].copy()

    print("=" * 70)
    print("T2D-EviGuide MIMIC STATIC ASSESSMENT AUDIT")
    print("=" * 70)

    print()
    print(f"Total cases: {len(df)}")
    print(f"Successful assessments: {len(successful)}")
    print(
        f"Failed assessments: "
        f"{len(df) - len(successful)}"
    )

    audit_rows = []

    for _, row in successful.iterrows():

        assessment = str(
            row["assessment"]
        )

        citations = extract_citations(
            assessment
        )

        old_citations = extract_old_style_citations(
            assessment
        )

        # ----------------------------------------------------
        # Known problematic patterns
        # ----------------------------------------------------

        hba1c_igt_error = contains_pattern(
            assessment,
            HBA1C_IGT_PATTERNS
        )

        fasting_error = contains_pattern(
            assessment,
            FASTING_ERROR_PATTERNS
        )

        diagnosis_language = contains_pattern(
            assessment,
            DIAGNOSIS_PATTERNS
        )

        medication_action = contains_pattern(
            assessment,
            MEDICATION_ACTION_PATTERNS
        )

        missing_data_count = count_missing_data_indicators(
            assessment
        )

        # ----------------------------------------------------
        # Citation information
        # ----------------------------------------------------

        has_stable_citation = (
            len(citations) > 0
        )

        has_old_style_citation = (
            len(old_citations) > 0
        )

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        audit_rows.append({

            "evaluation_id":
                row["evaluation_id"],

            "hba1c_mean":
                row.get("hba1c_mean", ""),

            "evaluation_group":
                row.get("evaluation_group", ""),

            "stable_citation_present":
                has_stable_citation,

            "stable_citation_count":
                len(citations),

            "old_style_citation_present":
                has_old_style_citation,

            "hba1c_igt_error":
                hba1c_igt_error,

            "fasting_interpretation_error":
                fasting_error,

            "diagnostic_overreach_language":
                diagnosis_language,

            "medication_action_language":
                medication_action,

            "missing_data_indicator_count":
                missing_data_count,

            "assessment_length":
                len(assessment)
        })

    audit = pd.DataFrame(
        audit_rows
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("--- STATIC AUDIT RESULTS ---")

    if len(audit) > 0:

        print(
            "Stable citation present: "
            f"{audit['stable_citation_present'].mean() * 100:.1f}%"
        )

        print(
            "Old-style citation present: "
            f"{audit['old_style_citation_present'].mean() * 100:.1f}%"
        )

        print(
            "HbA1c/IGT confusion: "
            f"{audit['hba1c_igt_error'].mean() * 100:.1f}%"
        )

        print(
            "Potential fasting interpretation error: "
            f"{audit['fasting_interpretation_error'].mean() * 100:.1f}%"
        )

        print(
            "Potential diagnostic overreach: "
            f"{audit['diagnostic_overreach_language'].mean() * 100:.1f}%"
        )

        print(
            "Potential medication-action language: "
            f"{audit['medication_action_language'].mean() * 100:.1f}%"
        )

        print(
            "Mean missing-data indicators: "
            f"{audit['missing_data_indicator_count'].mean():.2f}"
        )

    # ========================================================
    # PROBLEM CASES
    # ========================================================

    print()
    print("--- POTENTIAL HbA1c / IGT ERRORS ---")

    print(
        audit.loc[
            audit["hba1c_igt_error"],
            [
                "evaluation_id",
                "hba1c_mean",
                "evaluation_group"
            ]
        ].to_string(
            index=False
        )
    )

    print()
    print("--- POTENTIAL FASTING ERRORS ---")

    print(
        audit.loc[
            audit["fasting_interpretation_error"],
            [
                "evaluation_id",
                "hba1c_mean",
                "evaluation_group"
            ]
        ].to_string(
            index=False
        )
    )

    print()
    print("--- POTENTIAL DIAGNOSTIC OVERREACH ---")

    print(
        audit.loc[
            audit["diagnostic_overreach_language"],
            [
                "evaluation_id",
                "hba1c_mean",
                "evaluation_group"
            ]
        ].to_string(
            index=False
        )
    )

    print()
    print("--- POTENTIAL MEDICATION ACTION LANGUAGE ---")

    print(
        audit.loc[
            audit["medication_action_language"],
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

    output_file = (
        "data/real_clinical_data/"
        "mimic_static_audit.csv"
    )

    audit.to_csv(
        output_file,
        index=False
    )

    print()
    print(
        f"Audit saved to: {output_file}"
    )


if __name__ == "__main__":
    main()