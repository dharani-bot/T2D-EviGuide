import pandas as pd

from clinical_guardrails_v2 import check_clinical_guardrails_v2


RESULTS_FILE = "data/real_clinical_data/mimic_evaluation_results.csv"
OUTPUT_FILE = "data/real_clinical_data/mimic_guardrail_v2_test_results.csv"


print("Loading evaluation data...")

df = pd.read_csv(RESULTS_FILE)

results = []

successful = df[df["assessment_success"] == True].copy()

print(f"Successful assessments found: {len(successful)}")
print()


for _, row in successful.iterrows():

    patient_data = {
        "hba1c": row["hba1c_mean"],
        "blood_glucose": row["blood_glucose_mean"],

        # MIMIC Demo data used here does not establish
        # fasting glucose status.
        "fasting_glucose": None,

        # No OGTT 2-hour glucose is being used.
        "ogtt_2h_glucose": None,

        # Blood glucose is treated as inpatient/unspecified,
        # not fasting.
        "glucose_measurement_type": "inpatient",
    }

    flags = check_clinical_guardrails_v2(
        row["assessment"],
        patient_data
    )

    results.append({
        "evaluation_id": row["evaluation_id"],
        "hba1c_mean": row["hba1c_mean"],
        "blood_glucose_mean": row["blood_glucose_mean"],

        "hba1c_igt_flag": flags["hba1c_igt"],
        "fasting_flag": flags["fasting"],
        "threshold_flag": flags["threshold"],
        "diagnostic_language_flag": flags["diagnostic_language"],

        "any_flag": any(flags.values()),
    })


results_df = pd.DataFrame(results)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("========================================")
print("T2D-EviGuide Guardrail V2 Evaluation")
print("========================================")

print()

print(
    "Successful assessments tested:",
    len(results_df)
)

print(
    "HbA1c / IGT flags:",
    int(results_df["hba1c_igt_flag"].sum())
)

print(
    "Fasting interpretation flags:",
    int(results_df["fasting_flag"].sum())
)

print(
    "Threshold application flags:",
    int(results_df["threshold_flag"].sum())
)

print(
    "Diagnostic language flags:",
    int(results_df["diagnostic_language_flag"].sum())
)

print(
    "Assessments with no guardrail flags:",
    int((~results_df["any_flag"]).sum()),
    "/",
    len(results_df)
)

if len(results_df) > 0:
    no_flag_rate = (
        (~results_df["any_flag"]).sum()
        / len(results_df)
        * 100
    )

    print(
        f"No-flag rate: {no_flag_rate:.1f}%"
    )

print()

print("Saved results to:")
print(OUTPUT_FILE)