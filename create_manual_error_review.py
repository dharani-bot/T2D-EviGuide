import pandas as pd
from pathlib import Path

BASE = Path("data/real_clinical_data")

results_file = BASE / "mimic_evaluation_results.csv"
output_file = BASE / "mimic_manual_error_review.csv"

df = pd.read_csv(results_file)

# Only successful LLM assessments are eligible for manual review.
df = df[df["assessment_success"] == True].copy()

# Manually confirmed baseline findings from the assessment review.
confirmed_errors = [
    {
        "evaluation_id": "MIMIC-EVAL-001",
        "error_category": "HbA1c_IGT_terminology",
        "automated_flag": True,
        "manual_status": "Confirmed",
        "evidence": "HbA1c 7.5% was explicitly described as impaired glucose tolerance (IGT).",
        "notes": "HbA1c and IGT were incorrectly conflated."
    },
    {
        "evaluation_id": "MIMIC-EVAL-003",
        "error_category": "HbA1c_IGT_terminology",
        "automated_flag": True,
        "manual_status": "Confirmed",
        "evidence": "HbA1c 7.1% was explicitly described as IGT and IGT was incorrectly defined using an HbA1c threshold.",
        "notes": "HbA1c and IGT were incorrectly conflated."
    },
    {
        "evaluation_id": "MIMIC-EVAL-023",
        "error_category": "HbA1c_IGT_terminology",
        "automated_flag": True,
        "manual_status": "Confirmed",
        "evidence": "HbA1c 5.9% was described as being in an IGT range.",
        "notes": "HbA1c was incorrectly equated with IGT."
    },
    {
        "evaluation_id": "MIMIC-EVAL-025",
        "error_category": "HbA1c_IGT_terminology",
        "automated_flag": True,
        "manual_status": "Confirmed",
        "evidence": "HbA1c 6.1% was discussed using an incorrect IGT threshold.",
        "notes": "HbA1c and IGT terminology were incorrectly conflated."
    },
    {
        "evaluation_id": "MIMIC-EVAL-033",
        "error_category": "HbA1c_IGT_terminology",
        "automated_flag": True,
        "manual_status": "Confirmed",
        "evidence": "HbA1c 5.6% was incorrectly described as being within the 5.7%-6.4% prediabetes range.",
        "notes": "Numerical threshold application error as well as incorrect glycemic terminology."
    },

    {
        "evaluation_id": "MIMIC-EVAL-001",
        "error_category": "Numerical_threshold",
        "automated_flag": True,
        "manual_status": "Confirmed",
        "evidence": "Inpatient glucose of 201.85 mg/dL was described as below a threshold of >=140 mg/dL.",
        "notes": "201.85 is numerically greater than 140; additionally, the inpatient measurement was not established as an OGTT/postprandial measurement."
    },
    {
        "evaluation_id": "MIMIC-EVAL-033",
        "error_category": "Numerical_threshold",
        "automated_flag": True,
        "manual_status": "Confirmed",
        "evidence": "HbA1c 5.6% was described as falling within the 5.7%-6.4% range.",
        "notes": "5.6% is below 5.7%."
    },

    # Representative fasting cases manually reviewed.
    {
        "evaluation_id": "MIMIC-EVAL-002",
        "error_category": "Fasting_interpretation",
        "automated_flag": True,
        "manual_status": "Not an error",
        "evidence": "Assessment explicitly states that inpatient glucose was not confirmed as fasting.",
        "notes": "Automated detector produced a false-positive review flag."
    },
    {
        "evaluation_id": "MIMIC-EVAL-003",
        "error_category": "Fasting_interpretation",
        "automated_flag": True,
        "manual_status": "Not an error",
        "evidence": "Assessment explicitly states that inpatient glucose cannot be considered fasting.",
        "notes": "Automated detector produced a false-positive review flag."
    },
    {
        "evaluation_id": "MIMIC-EVAL-004",
        "error_category": "Fasting_interpretation",
        "automated_flag": True,
        "manual_status": "Not an error",
        "evidence": "Assessment explicitly states that inpatient glucose cannot be classified as fasting.",
        "notes": "Automated detector produced a false-positive review flag."
    },
    {
        "evaluation_id": "MIMIC-EVAL-005",
        "error_category": "Fasting_interpretation",
        "automated_flag": True,
        "manual_status": "Not an error",
        "evidence": "Assessment explicitly identifies the glucose as non-fasting.",
        "notes": "Automated detector produced a false-positive review flag."
    },
    {
        "evaluation_id": "MIMIC-EVAL-021",
        "error_category": "Fasting_interpretation",
        "automated_flag": True,
        "manual_status": "Not an error",
        "evidence": "Assessment explicitly states that inpatient glucose cannot be used to assess fasting hyperglycemia.",
        "notes": "Automated detector produced a false-positive review flag."
    }
]

review_df = pd.DataFrame(confirmed_errors)

# Add patient measurements for easier auditing.
patient_cols = [
    "evaluation_id",
    "hba1c_mean",
    "blood_glucose_mean",
    "evaluation_group",
    "diagnosis_group",
    "age",
    "sex",
]

patient_data = df[patient_cols].drop_duplicates("evaluation_id")

review_df = review_df.merge(
    patient_data,
    on="evaluation_id",
    how="left"
)

review_df = review_df[
    [
        "evaluation_id",
        "error_category",
        "automated_flag",
        "manual_status",
        "hba1c_mean",
        "blood_glucose_mean",
        "evaluation_group",
        "diagnosis_group",
        "age",
        "sex",
        "evidence",
        "notes",
    ]
]

review_df.to_csv(output_file, index=False)

print("=" * 70)
print("T2D-EviGuide MANUAL ERROR REVIEW")
print("=" * 70)

print(f"\nSuccessful assessments: {len(df)}")
print(f"Manual review records: {len(review_df)}")

print("\n--- CONFIRMED ERRORS ---")

confirmed = review_df[review_df["manual_status"] == "Confirmed"]

if len(confirmed) > 0:
    summary = (
        confirmed.groupby("error_category")
        .size()
        .reset_index(name="confirmed_cases")
    )

    summary["rate_percent"] = (
        summary["confirmed_cases"] / len(df) * 100
    )

    print(summary.to_string(index=False))
else:
    print("None")

print("\n--- MANUAL REVIEW OUTCOMES ---")

print(
    review_df.groupby(
        ["error_category", "manual_status"]
    ).size().reset_index(name="cases").to_string(index=False)
)

print("\n--- HbA1c / IGT ---")

hba1c_errors = review_df[
    (review_df["error_category"] == "HbA1c_IGT_terminology")
    & (review_df["manual_status"] == "Confirmed")
]

print(f"Confirmed cases: {len(hba1c_errors)}")
print(f"Rate: {len(hba1c_errors) / len(df) * 100:.1f}%")

print("\n--- Numerical Threshold ---")

numeric_errors = review_df[
    (review_df["error_category"] == "Numerical_threshold")
    & (review_df["manual_status"] == "Confirmed")
]

print(f"Confirmed cases: {len(numeric_errors)}")
print(f"Rate: {len(numeric_errors) / len(df) * 100:.1f}%")

print("\n--- Fasting Interpretation ---")

fasting_review = review_df[
    review_df["error_category"] == "Fasting_interpretation"
]

fasting_errors = fasting_review[
    fasting_review["manual_status"] == "Confirmed"
]

print(f"Reviewed cases: {len(fasting_review)}")
print(f"Confirmed errors: {len(fasting_errors)}")

print("\nSaved to:")
print(output_file)