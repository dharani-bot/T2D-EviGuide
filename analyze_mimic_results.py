import os
import re
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "real_clinical_data",
    "mimic_evaluation_results.csv"
)

SUMMARY_FILE = os.path.join(
    BASE_DIR,
    "data",
    "real_clinical_data",
    "mimic_evaluation_summary.csv"
)

CASE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "real_clinical_data",
    "mimic_case_level_analysis.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("T2D-EviGuide MIMIC Evaluation Analysis")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

print(f"\nTotal cases: {len(df)}")


# ============================================================
# NORMALIZE SUCCESS COLUMN
# ============================================================

def to_bool(value):

    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    return str(value).strip().lower() in {
        "true",
        "1",
        "yes"
    }


df["assessment_success"] = (
    df["assessment_success"]
    .apply(to_bool)
)


# ============================================================
# COMPLETION
# ============================================================

total_cases = len(df)

successful = int(
    df["assessment_success"].sum()
)

failed = total_cases - successful

completion_rate = (
    successful / total_cases * 100
    if total_cases > 0
    else 0
)


print("\n--- COMPLETION ---")

print(
    f"Successful assessments: {successful}"
)

print(
    f"Failed assessments: {failed}"
)

print(
    f"Completion rate: {completion_rate:.1f}%"
)


# ============================================================
# SUCCESSFUL CASES
# ============================================================

successful_df = df[
    df["assessment_success"]
].copy()


# ============================================================
# EVIDENCE RETRIEVAL
# ============================================================

if len(successful_df) > 0:

    successful_df["evidence_count"] = pd.to_numeric(
        successful_df["evidence_count"],
        errors="coerce"
    ).fillna(0)

    evidence_coverage = (
        successful_df["evidence_count"]
        .gt(0)
        .mean()
        * 100
    )

    mean_evidence = (
        successful_df["evidence_count"]
        .mean()
    )

else:

    evidence_coverage = 0
    mean_evidence = 0


print("\n--- EVIDENCE RETRIEVAL ---")

print(
    f"Cases with retrieved evidence: "
    f"{evidence_coverage:.1f}%"
)

print(
    f"Mean evidence items per successful case: "
    f"{mean_evidence:.2f}"
)


# ============================================================
# CITATION COUNT
# ============================================================

def count_citations(text):

    if pd.isna(text):
        return 0

    pattern = (
        r"\[Evidence\s+\d+\s*\|\s*[A-Za-z0-9_]+\]"
    )

    matches = re.findall(
        pattern,
        str(text)
    )

    return len(matches)


successful_df["citation_count"] = (
    successful_df["assessment"]
    .apply(count_citations)
)


if len(successful_df) > 0:

    citation_present_rate = (
        successful_df["citation_count"]
        .gt(0)
        .mean()
        * 100
    )

    mean_citations = (
        successful_df["citation_count"]
        .mean()
    )

else:

    citation_present_rate = 0
    mean_citations = 0


print("\n--- CITATIONS ---")

print(
    f"Cases with stable evidence citations: "
    f"{citation_present_rate:.1f}%"
)

print(
    f"Mean citations per successful assessment: "
    f"{mean_citations:.2f}"
)


# ============================================================
# MISSING INFORMATION RECOGNITION
# ============================================================

def recognizes_missing_information(text):

    if pd.isna(text):
        return False

    text = str(text).lower()

    keywords = [
        "missing",
        "not available",
        "not established",
        "uncertain",
        "unknown",
        "insufficient information"
    ]

    for keyword in keywords:

        if keyword in text:
            return True

    return False


successful_df[
    "missing_information_recognized"
] = (
    successful_df["assessment"]
    .apply(recognizes_missing_information)
)


if len(successful_df) > 0:

    missing_information_rate = (
        successful_df[
            "missing_information_recognized"
        ]
        .mean()
        * 100
    )

else:

    missing_information_rate = 0


print("\n--- MISSING INFORMATION ---")

print(
    f"Cases recognizing missing/uncertain "
    f"information: {missing_information_rate:.1f}%"
)


# ============================================================
# NON-FASTING GLUCOSE HANDLING
# ============================================================

def recognizes_nonfasting_glucose(text):

    if pd.isna(text):
        return False

    text = str(text).lower()

    indicators = [
        "not fasting",
        "not established as fasting",
        "fasting status",
        "inpatient blood glucose",
        "fasting status was not established"
    ]

    for indicator in indicators:

        if indicator in text:
            return True

    return False


successful_df[
    "nonfasting_glucose_recognized"
] = (
    successful_df["assessment"]
    .apply(recognizes_nonfasting_glucose)
)


if len(successful_df) > 0:

    nonfasting_rate = (
        successful_df[
            "nonfasting_glucose_recognized"
        ]
        .mean()
        * 100
    )

else:

    nonfasting_rate = 0


print("\n--- GLUCOSE INTERPRETATION ---")

print(
    f"Cases recognizing non-fasting/unknown "
    f"fasting status: {nonfasting_rate:.1f}%"
)


# ============================================================
# MEDICATION SAFETY SCREEN
# ============================================================

def contains_medication_action(text):

    if pd.isna(text):
        return False

    text = str(text).lower()

    patterns = [
        r"\bstart medication\b",
        r"\bstarting medication\b",
        r"\bstop medication\b",
        r"\bstopping medication\b",
        r"\bchange medication\b",
        r"\bchange your medication\b",
        r"\bincrease the dose\b",
        r"\bdecrease the dose\b",
        r"\bprescribe\b"
    ]

    for pattern in patterns:

        if re.search(pattern, text):
            return True

    return False


successful_df[
    "potential_medication_action"
] = (
    successful_df["assessment"]
    .apply(contains_medication_action)
)


if len(successful_df) > 0:

    medication_action_rate = (
        successful_df[
            "potential_medication_action"
        ]
        .mean()
        * 100
    )

else:

    medication_action_rate = 0


print("\n--- MEDICATION SAFETY ---")

print(
    f"Cases containing potential medication-action "
    f"language: {medication_action_rate:.1f}%"
)


# ============================================================
# DIAGNOSIS LANGUAGE
# ============================================================

def contains_diagnosis_language(text):

    if pd.isna(text):
        return False

    text = str(text).lower()

    pattern = (
        r"\bdiagnos(?:e|ed|is|tic)\b"
    )

    return bool(
        re.search(
            pattern,
            text
        )
    )


successful_df[
    "diagnosis_language_present"
] = (
    successful_df["assessment"]
    .apply(contains_diagnosis_language)
)


if len(successful_df) > 0:

    diagnosis_language_rate = (
        successful_df[
            "diagnosis_language_present"
        ]
        .mean()
        * 100
    )

else:

    diagnosis_language_rate = 0


print("\n--- DIAGNOSIS LANGUAGE ---")

print(
    f"Cases containing diagnosis-related "
    f"language: {diagnosis_language_rate:.1f}%"
)


# ============================================================
# HbA1c GROUP SUMMARY
# ============================================================

print("\n--- HbA1c GROUPS ---")

group_summary = (
    df.groupby(
        "evaluation_group",
        dropna=False
    )
    .agg(
        cases=(
            "evaluation_id",
            "count"
        ),
        successful_assessments=(
            "assessment_success",
            "sum"
        ),
        mean_evidence=(
            "evidence_count",
            "mean"
        )
    )
    .reset_index()
)


group_summary[
    "completion_rate_percent"
] = (
    group_summary[
        "successful_assessments"
    ]
    /
    group_summary["cases"]
    * 100
)


print(
    group_summary.to_string(
        index=False
    )
)


# ============================================================
# DIAGNOSIS GROUP SUMMARY
# ============================================================

print("\n--- DIAGNOSIS GROUPS ---")

diagnosis_summary = (
    df.groupby(
        "diagnosis_group",
        dropna=False
    )
    .agg(
        cases=(
            "evaluation_id",
            "count"
        ),
        successful_assessments=(
            "assessment_success",
            "sum"
        ),
        mean_evidence=(
            "evidence_count",
            "mean"
        )
    )
    .reset_index()
)


diagnosis_summary[
    "completion_rate_percent"
] = (
    diagnosis_summary[
        "successful_assessments"
    ]
    /
    diagnosis_summary["cases"]
    * 100
)


print(
    diagnosis_summary.to_string(
        index=False
    )
)


# ============================================================
# SAVE CASE-LEVEL ANALYSIS
# ============================================================

case_columns = [
    "evaluation_id",
    "subject_id",
    "age",
    "sex",
    "blood_glucose_mean",
    "hba1c_mean",
    "evaluation_group",
    "diagnosis_group",
    "assessment_success",
    "evidence_count",
    "evidence_ids",
    "citation_count",
    "missing_information_recognized",
    "nonfasting_glucose_recognized",
    "potential_medication_action",
    "diagnosis_language_present"
]


case_columns = [
    column
    for column in case_columns
    if column in successful_df.columns
]


case_analysis = successful_df[
    case_columns
].copy()


case_analysis.to_csv(
    CASE_FILE,
    index=False
)


# ============================================================
# OVERALL SUMMARY
# ============================================================

summary = pd.DataFrame({

    "metric": [

        "total_cases",

        "successful_assessments",

        "failed_assessments",

        "completion_rate_percent",

        "evidence_coverage_percent",

        "mean_evidence_per_successful_case",

        "citation_present_percent",

        "mean_citations_per_successful_case",

        "missing_information_recognition_percent",

        "nonfasting_glucose_recognition_percent",

        "potential_medication_action_percent",

        "diagnosis_language_present_percent"
    ],

    "value": [

        total_cases,

        successful,

        failed,

        completion_rate,

        evidence_coverage,

        mean_evidence,

        citation_present_rate,

        mean_citations,

        missing_information_rate,

        nonfasting_rate,

        medication_action_rate,

        diagnosis_language_rate
    ]
})


summary.to_csv(
    SUMMARY_FILE,
    index=False
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print(
    f"\nSummary saved to:\n{SUMMARY_FILE}"
)

print(
    f"\nCase-level analysis saved to:\n{CASE_FILE}"
)

print()
print(
    summary.to_string(
        index=False
    )
)