import pandas as pd
from pathlib import Path

from clinical_guardrails import check_clinical_guardrails


BASE = Path("data/real_clinical_data")
INPUT_FILE = BASE / "mimic_evaluation_results.csv"
OUTPUT_FILE = BASE / "mimic_guardrail_test_results.csv"


df = pd.read_csv(INPUT_FILE)

results = []

for _, row in df.iterrows():

    if str(row["assessment_success"]).lower() != "true":
        continue

    assessment = str(row["assessment"])

    flags = check_clinical_guardrails(assessment)

    results.append({
        "evaluation_id": row["evaluation_id"],
        "hba1c_mean": row["hba1c_mean"],
        "blood_glucose_mean": row["blood_glucose_mean"],
        "hba1c_igt_flag": flags.get("hba1c_igt", False),
        "fasting_flag": flags.get("fasting", False),
        "threshold_flag": flags.get("threshold", False),
        "diagnostic_language_flag": flags.get("diagnostic_language", False),
        "total_flags": sum(
            bool(value)
            for value in flags.values()
        )
    })


results_df = pd.DataFrame(results)

results_df.to_csv(OUTPUT_FILE, index=False)


print("=" * 70)
print("T2D-EviGuide CLINICAL GUARDRAIL TEST")
print("=" * 70)

print(f"\nSuccessful assessments tested: {len(results_df)}")

if len(results_df) > 0:

    print("\n--- GUARDRAIL RESULTS ---")

    print(
        f"HbA1c / IGT flags: "
        f"{results_df['hba1c_igt_flag'].sum()}"
    )

    print(
        f"Fasting interpretation flags: "
        f"{results_df['fasting_flag'].sum()}"
    )

    print(
        f"Threshold flags: "
        f"{results_df['threshold_flag'].sum()}"
    )

    print(
        f"Diagnostic language flags: "
        f"{results_df['diagnostic_language_flag'].sum()}"
    )

    clean = (results_df["total_flags"] == 0).sum()

    print(
        f"\nAssessments with no guardrail flags: "
        f"{clean}/{len(results_df)} "
        f"({clean / len(results_df) * 100:.1f}%)"
    )

    print("\n--- CASES WITH FLAGS ---")

    flagged = results_df[results_df["total_flags"] > 0]

    if len(flagged) > 0:
        print(
            flagged[
                [
                    "evaluation_id",
                    "hba1c_igt_flag",
                    "fasting_flag",
                    "threshold_flag",
                    "diagnostic_language_flag",
                    "total_flags"
                ]
            ].to_string(index=False)
        )
    else:
        print("No guardrail flags detected.")

print("\nSaved to:")
print(OUTPUT_FILE)