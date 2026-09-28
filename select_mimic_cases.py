import os
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
    "t2d_real_patient_data.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "real_clinical_data",
    "t2d_mimic_evaluation.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("MIMIC-IV evaluation case selection")
print("=" * 70)

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"\nInput patients: {len(df)}"
)


# ============================================================
# ELIGIBILITY
# ============================================================

# We require both:
# - blood glucose measurements
# - HbA1c percentage measurements
#
# Blood glucose is retained as contextual inpatient glucose.
# It is NOT treated as fasting glucose.
#

df[
    "eligible_for_glycemic_evaluation"
] = (
    df["has_blood_glucose"].fillna(False)
    &
    df["has_hba1c"].fillna(False)
)


eligible = df[
    df["eligible_for_glycemic_evaluation"]
].copy()


# ============================================================
# HbA1c EVALUATION GROUPS
# ============================================================

def classify_hba1c(value):

    if pd.isna(value):
        return "missing"

    if value < 5.7:
        return "lower_hba1c"

    elif value < 6.5:
        return "increased_risk_hba1c"

    else:
        return "elevated_hba1c"


eligible[
    "evaluation_group"
] = eligible[
    "hba1c_mean"
].apply(
    classify_hba1c
)


# ============================================================
# DIAGNOSIS GROUP
# ============================================================

eligible[
    "diagnosis_group"
] = eligible[
    "has_diabetes_related_diagnosis"
].apply(
    lambda value:
    "diabetes_related_icd_present"
    if bool(value)
    else "no_diabetes_related_icd"
)


# ============================================================
# COMPLETENESS
# ============================================================

# Age and sex should be available from patients.csv.gz.
#
# Weight, height, BMI, BP, family history, activity and
# smoking are NOT required because they are not available
# in the supplied MIMIC files.
#

eligible[
    "core_data_complete"
] = (
    eligible["anchor_age"].notna()
    &
    eligible["gender"].notna()
    &
    eligible["blood_glucose_mean"].notna()
    &
    eligible["hba1c_mean"].notna()
)


eligible = eligible[
    eligible["core_data_complete"]
].copy()


# ============================================================
# SORT
# ============================================================

eligible = eligible.sort_values(
    by=[
        "evaluation_group",
        "subject_id"
    ]
).reset_index(
    drop=True
)


# ============================================================
# EVALUATION IDS
# ============================================================

eligible[
    "evaluation_id"
] = [
    f"MIMIC-EVAL-{i:03d}"
    for i in range(
        1,
        len(eligible) + 1
    )
]


# ============================================================
# METHODOLOGICAL NOTES
# ============================================================

eligible[
    "data_source"
] = "MIMIC-IV Demo"


eligible[
    "data_type"
] = (
    "Real de-identified electronic health record data"
)


eligible[
    "clinical_use_note"
] = (
    "Prototype/evidence-grounding evaluation only; "
    "not clinical validation or population-level "
    "risk prediction."
)


eligible[
    "blood_glucose_interpretation"
] = (
    "Available inpatient blood glucose measurement; "
    "fasting status is not established."
)


eligible[
    "hba1c_interpretation"
] = (
    "HbA1c percentage based on MIMIC-IV item 50852."
)


eligible[
    "medication_interpretation"
] = (
    "Prescription history represents MIMIC-IV "
    "prescription records and is not assumed to "
    "represent current outpatient medication use."
)


eligible[
    "missing_clinical_variables"
] = (
    "Weight, height, BMI, blood pressure, family "
    "history, physical activity and smoking status "
    "were not available in the supplied dataset."
)


eligible[
    "diagnosis_interpretation"
] = (
    "Diabetes-related ICD grouping is a data-derived "
    "flag and is not treated as an independent "
    "clinical diagnosis."
)


# ============================================================
# SELECT OUTPUT COLUMNS
# ============================================================

output_columns = [

    "evaluation_id",

    "subject_id",

    "gender",

    "anchor_age",

    "blood_glucose_measurements",

    "blood_glucose_mean",

    "blood_glucose_min",

    "blood_glucose_max",

    "hba1c_measurements",

    "hba1c_mean",

    "hba1c_min",

    "hba1c_max",

    "evaluation_group",

    "diagnosis_group",

    "has_diabetes_related_diagnosis",

    "diabetes_related_icd_count",

    "prescription_history",

    "data_source",

    "data_type",

    "clinical_use_note",

    "blood_glucose_interpretation",

    "hba1c_interpretation",

    "medication_interpretation",

    "missing_clinical_variables",

    "diagnosis_interpretation"
]


output_columns = [
    column
    for column in output_columns
    if column in eligible.columns
]


evaluation = eligible[
    output_columns
].copy()


# ============================================================
# SAVE
# ============================================================

evaluation.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("CASE SELECTION COMPLETE")
print("=" * 70)

print(
    f"\nSelected evaluation cases: "
    f"{len(evaluation)}"
)

print(
    "\nEvaluation groups:"
)

print(
    evaluation[
        "evaluation_group"
    ].value_counts()
    .to_string()
)

print(
    "\nDiagnosis groups:"
)

print(
    evaluation[
        "diagnosis_group"
    ].value_counts()
    .to_string()
)

print(
    "\nAge range:"
)

print(
    f"{evaluation['anchor_age'].min():.0f} - "
    f"{evaluation['anchor_age'].max():.0f}"
)

print(
    "\nSex:"
)

print(
    evaluation[
        "gender"
    ].value_counts()
    .to_string()
)

print(
    "\nOutput:"
)

print(
    OUTPUT_FILE
)