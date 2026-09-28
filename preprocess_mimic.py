import os
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
    "real_clinical_data"
)

PATIENTS_FILE = os.path.join(
    DATA_DIR,
    "patients.csv.gz"
)

LABEVENTS_FILE = os.path.join(
    DATA_DIR,
    "labevents.csv.gz"
)

DIAGNOSES_FILE = os.path.join(
    DATA_DIR,
    "diagnoses_icd.csv.gz"
)

PRESCRIPTIONS_FILE = os.path.join(
    DATA_DIR,
    "prescriptions.csv.gz"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "t2d_real_patient_data.csv"
)

AUDIT_FILE = os.path.join(
    DATA_DIR,
    "t2d_laboratory_audit.csv"
)


# ============================================================
# MIMIC LAB ITEM IDS
# ============================================================

# Blood glucose only.
#
# IMPORTANT:
# These measurements are NOT assumed to be fasting glucose.
#
BLOOD_GLUCOSE_ITEMIDS = {
    52027,
    50809,
    50931,
    52569
}


# HbA1c percentage only.
#
# MIMIC inspection confirmed:
# itemid 50852 = % Hemoglobin A1c
# valueuom = %
#
# We intentionally use ONLY this item to avoid mixing
# different HbA1c representations or units.
#
HBA1C_ITEMIDS = {
    50852
}


# ============================================================
# LOAD PATIENTS
# ============================================================

print("=" * 70)
print("MIMIC-IV preprocessing")
print("=" * 70)

print("\nLoading patients...")

patients = pd.read_csv(
    PATIENTS_FILE,
    compression="gzip"
)

print(
    f"Patients loaded: {len(patients)}"
)


# ============================================================
# LOAD LAB EVENTS
# ============================================================

print("\nLoading laboratory events...")

labevents = pd.read_csv(
    LABEVENTS_FILE,
    compression="gzip",
    low_memory=False
)

print(
    f"Laboratory rows loaded: {len(labevents)}"
)


# ============================================================
# SELECT RELEVANT LABORATORY MEASUREMENTS
# ============================================================

print("\nSelecting blood glucose and HbA1c measurements...")

relevant_itemids = (
    BLOOD_GLUCOSE_ITEMIDS
    | HBA1C_ITEMIDS
)

labs = labevents[
    labevents["itemid"].isin(relevant_itemids)
].copy()


# Numeric laboratory value
labs["valuenum"] = pd.to_numeric(
    labs["valuenum"],
    errors="coerce"
)


# Remove rows without usable numeric values
labs = labs[
    labs["valuenum"].notna()
].copy()


# ============================================================
# TEST TYPE
# ============================================================

labs["test_type"] = "other"

labs.loc[
    labs["itemid"].isin(BLOOD_GLUCOSE_ITEMIDS),
    "test_type"
] = "blood_glucose"

labs.loc[
    labs["itemid"].isin(HBA1C_ITEMIDS),
    "test_type"
] = "hba1c"


# ============================================================
# CREATE LABORATORY AUDIT FILE
# ============================================================

audit_columns = [
    "subject_id",
    "hadm_id",
    "charttime",
    "itemid",
    "value",
    "valuenum",
    "valueuom",
    "test_type"
]

audit = labs[
    [
        column
        for column in audit_columns
        if column in labs.columns
    ]
].copy()

audit.to_csv(
    AUDIT_FILE,
    index=False
)

print(
    f"\nLaboratory audit saved to:\n{AUDIT_FILE}"
)


# ============================================================
# BLOOD GLUCOSE SUMMARY
# ============================================================

blood_glucose = labs[
    labs["test_type"] == "blood_glucose"
].copy()

blood_glucose_summary = (
    blood_glucose
    .groupby("subject_id")["valuenum"]
    .agg(
        blood_glucose_measurements="count",
        blood_glucose_mean="mean",
        blood_glucose_min="min",
        blood_glucose_max="max"
    )
    .reset_index()
)


# ============================================================
# HbA1c SUMMARY
# ============================================================

hba1c = labs[
    labs["test_type"] == "hba1c"
].copy()

hba1c_summary = (
    hba1c
    .groupby("subject_id")["valuenum"]
    .agg(
        hba1c_measurements="count",
        hba1c_mean="mean",
        hba1c_min="min",
        hba1c_max="max"
    )
    .reset_index()
)


# ============================================================
# DIABETES-RELATED ICD CODES
# ============================================================

print("\nLoading diagnoses...")

diagnoses = pd.read_csv(
    DIAGNOSES_FILE,
    compression="gzip",
    low_memory=False
)

print(
    f"Diagnosis rows loaded: {len(diagnoses)}"
)


diagnoses["icd_code"] = (
    diagnoses["icd_code"]
    .astype(str)
    .str.upper()
    .str.strip()
)


# Broad transparent grouping.
#
# This is NOT being used to diagnose the patient.
# It simply identifies whether diabetes-related ICD-10/ICD-9
# codes are present in the supplied MIMIC diagnosis data.
#
diabetes_related = diagnoses[
    diagnoses["icd_code"].str.startswith(
        ("E10", "E11", "E13")
    )
].copy()


diagnosis_summary = (
    diabetes_related
    .groupby("subject_id")
    .size()
    .reset_index(
        name="diabetes_related_icd_count"
    )
)

diagnosis_summary[
    "has_diabetes_related_diagnosis"
] = True


# ============================================================
# PRESCRIPTION HISTORY
# ============================================================

print("\nLoading prescriptions...")

prescriptions = pd.read_csv(
    PRESCRIPTIONS_FILE,
    compression="gzip",
    low_memory=False
)

print(
    f"Prescription rows loaded: {len(prescriptions)}"
)


# Create a compact medication-history representation.
#
# IMPORTANT:
# These are MIMIC prescription records and are NOT assumed
# to represent the patient's current outpatient medication.
#

if "drug" in prescriptions.columns:

    medication_history = (
        prescriptions[
            ["subject_id", "drug"]
        ]
        .dropna()
        .drop_duplicates()
        .groupby("subject_id")["drug"]
        .apply(
            lambda values:
            "; ".join(
                sorted(
                    set(
                        str(value)
                        for value in values
                    )
                )
            )
        )
        .reset_index(
            name="prescription_history"
        )
    )

else:

    medication_history = pd.DataFrame(
        columns=[
            "subject_id",
            "prescription_history"
        ]
    )


# ============================================================
# COMBINE PATIENT-LEVEL DATA
# ============================================================

print("\nCombining patient-level data...")

result = patients.copy()


# Patient demographics
demographic_columns = [
    column
    for column in [
        "subject_id",
        "gender",
        "anchor_age",
        "anchor_year",
        "dod"
    ]
    if column in result.columns
]

result = result[
    demographic_columns
].copy()


# Blood glucose
result = result.merge(
    blood_glucose_summary,
    on="subject_id",
    how="left"
)


# HbA1c
result = result.merge(
    hba1c_summary,
    on="subject_id",
    how="left"
)


# Diagnosis
result = result.merge(
    diagnosis_summary,
    on="subject_id",
    how="left"
)


# Medication history
result = result.merge(
    medication_history,
    on="subject_id",
    how="left"
)


# ============================================================
# MISSING-VALUE FLAGS
# ============================================================

result[
    "has_blood_glucose"
] = (
    result["blood_glucose_measurements"]
    .fillna(0)
    > 0
)


result[
    "has_hba1c"
] = (
    result["hba1c_measurements"]
    .fillna(0)
    > 0
)


result[
    "has_diabetes_related_diagnosis"
] = (
    result[
        "has_diabetes_related_diagnosis"
    ]
    .fillna(False)
)


result[
    "diabetes_related_icd_count"
] = (
    result[
        "diabetes_related_icd_count"
    ]
    .fillna(0)
)


result[
    "prescription_history"
] = (
    result[
        "prescription_history"
    ]
    .fillna("")
)


# ============================================================
# METHODOLOGICAL NOTES
# ============================================================

result["blood_glucose_note"] = (
    "Blood glucose measurements from MIMIC-IV; "
    "fasting status is not established."
)


result["hba1c_note"] = (
    "HbA1c based only on MIMIC-IV item 50852 "
    "(% Hemoglobin A1c; unit %)."
)


result["medication_note"] = (
    "Prescription history from MIMIC-IV; "
    "not assumed to represent current outpatient "
    "medication use."
)


result["diagnosis_note"] = (
    "Diabetes-related ICD flag is based on ICD codes "
    "beginning E10, E11, or E13 and is not treated "
    "as an independent clinical diagnosis."
)


# ============================================================
# SAVE
# ============================================================

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("PREPROCESSING COMPLETE")
print("=" * 70)

print(
    f"Patients: {len(result)}"
)

print(
    f"Patients with blood glucose: "
    f"{result['has_blood_glucose'].sum()}"
)

print(
    f"Patients with HbA1c: "
    f"{result['has_hba1c'].sum()}"
)

print(
    f"Patients with diabetes-related ICD flag: "
    f"{result['has_diabetes_related_diagnosis'].sum()}"
)

print()

print(
    "HbA1c source: MIMIC item 50852 (% Hemoglobin A1c)"
)

print(
    "\nOutput:"
)

print(
    OUTPUT_FILE
)

print(
    "\nAudit:"
)

print(
    AUDIT_FILE
)