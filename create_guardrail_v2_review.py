import pandas as pd


EVALUATION_FILE = (
    "data/real_clinical_data/mimic_evaluation_results.csv"
)

GUARDRAIL_FILE = (
    "data/real_clinical_data/mimic_guardrail_v2_test_results.csv"
)

OUTPUT_FILE = (
    "data/real_clinical_data/mimic_guardrail_v2_manual_review.csv"
)


print("Loading evaluation data...")
evaluation = pd.read_csv(EVALUATION_FILE)

print("Loading V2 guardrail results...")
guardrails = pd.read_csv(GUARDRAIL_FILE)


# Keep only successful assessments
evaluation = evaluation[
    evaluation["assessment_success"] == True
].copy()


# Select useful assessment information
assessment_columns = [
    "evaluation_id",
    "subject_id",
    "age",
    "sex",
    "blood_glucose_mean",
    "hba1c_mean",
    "evaluation_group",
    "diagnosis_group",
    "assessment",
    "patient_summary",
]


assessment = evaluation[assessment_columns].copy()


# Merge guardrail results
review = assessment.merge(
    guardrails,
    on=[
        "evaluation_id",
        "hba1c_mean",
        "blood_glucose_mean",
    ],
    how="left",
)


# Put the most important columns first
columns = [
    "evaluation_id",
    "subject_id",
    "age",
    "sex",
    "hba1c_mean",
    "blood_glucose_mean",
    "evaluation_group",
    "diagnosis_group",

    "hba1c_igt_flag",
    "fasting_flag",
    "threshold_flag",
    "diagnostic_language_flag",
    "any_flag",

    "assessment",
    "patient_summary",
]


review = review[columns]


review.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("========================================")
print("V2 MANUAL REVIEW FILE")
print("========================================")
print()

print("Total successful assessments:", len(review))

print(
    "HbA1c / IGT flagged:",
    int(review["hba1c_igt_flag"].sum())
)

print(
    "Fasting flagged:",
    int(review["fasting_flag"].sum())
)

print(
    "Threshold flagged:",
    int(review["threshold_flag"].sum())
)

print(
    "Diagnostic language flagged:",
    int(review["diagnostic_language_flag"].sum())
)

print(
    "Any guardrail flag:",
    int(review["any_flag"].sum())
)

print()

print("Saved to:")
print(OUTPUT_FILE)