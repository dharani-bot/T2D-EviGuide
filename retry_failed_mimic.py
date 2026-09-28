import os
import pandas as pd

from clinical_assessment import generate_risk_assessment


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

EVALUATION_FILE = os.path.join(
    BASE_DIR,
    "data",
    "real_clinical_data",
    "t2d_mimic_evaluation.csv"
)

RESULTS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "real_clinical_data",
    "mimic_evaluation_results.csv"
)


FAILED_IDS = {
    "MIMIC-EVAL-011",
    "MIMIC-EVAL-015",
    "MIMIC-EVAL-017"
}


def safe_value(value):

    if pd.isna(value):
        return "Not available"

    return value


def build_mimic_patient(row):

    age = safe_value(
        row.get("anchor_age")
    )

    sex = safe_value(
        row.get("gender")
    )

    blood_glucose = safe_value(
        row.get("blood_glucose_mean")
    )

    hba1c = safe_value(
        row.get("hba1c_mean")
    )

    diabetes_icd = row.get(
        "has_diabetes_related_diagnosis",
        False
    )

    if pd.isna(diabetes_icd):
        diabetes_icd = False

    if bool(diabetes_icd):

        medical_history = (
            "A diabetes-related ICD code flag is present "
            "in the MIMIC-IV diagnosis data. "
            "This is a data-derived flag and is not "
            "treated as an independent clinical diagnosis."
        )

    else:

        medical_history = (
            "No diabetes-related ICD code flag was identified "
            "in the supplied MIMIC-IV diagnosis data."
        )

    prescription_history = safe_value(
        row.get("prescription_history")
    )

    if prescription_history == "Not available":

        medications = (
            "Prescription history not available."
        )

    elif prescription_history == "":

        medications = (
            "No prescription history recorded."
        )

    else:

        medications = (
            "MIMIC-IV prescription history: "
            + str(prescription_history)
            + ". This is historical/inpatient prescription "
              "data and is not assumed to represent current "
              "outpatient medication use."
        )

    return {

        "age": age,

        "sex": sex,

        "weight": "Not available",

        "height": "Not available",

        "bmi": "Not available",

        "fasting_glucose": (
            "Not available; fasting status was not "
            "established in the MIMIC-IV data."
        ),

        "blood_glucose": (
            f"{blood_glucose} mg/dL "
            "(mean available inpatient blood glucose; "
            "not established as fasting)"
        ),

        "hba1c": hba1c,

        "systolic_bp": "Not available",

        "diastolic_bp": "Not available",

        "family_history": "Not available",

        "physical_activity": "Not available",

        "smoking": "Not available",

        "medical_history": medical_history,

        "medications": medications
    }


def main():

    print("=" * 70)
    print("Retry Failed MIMIC-IV Assessments")
    print("=" * 70)
    print()

    evaluation_df = pd.read_csv(
        EVALUATION_FILE
    )

    results_df = pd.read_csv(
        RESULTS_FILE
    )

    failed_cases = evaluation_df[
        evaluation_df["evaluation_id"].isin(
            FAILED_IDS
        )
    ].copy()

    print(
        f"Cases to retry: {len(failed_cases)}"
    )

    print()

    for _, row in failed_cases.iterrows():

        evaluation_id = row[
            "evaluation_id"
        ]

        print(
            f"Retrying {evaluation_id}..."
        )

        try:

            patient_data = build_mimic_patient(
                row
            )

            result = generate_risk_assessment(
                patient_data,
                top_k=3
            )

            evidence = result.get(
                "evidence",
                []
            )

            evidence_ids = [
                item.get(
                    "article_id",
                    ""
                )
                for item in evidence
            ]

            mask = (
                results_df["evaluation_id"]
                == evaluation_id
            )

            results_df.loc[
                mask,
                "assessment_success"
            ] = result.get(
                "success",
                False
            )

            results_df.loc[
                mask,
                "evidence_count"
            ] = len(evidence)

            results_df.loc[
                mask,
                "evidence_ids"
            ] = " | ".join(
                evidence_ids
            )

            results_df.loc[
                mask,
                "assessment"
            ] = result.get(
                "assessment",
                ""
            )

            results_df.loc[
                mask,
                "patient_summary"
            ] = result.get(
                "patient_summary",
                ""
            )

            results_df.loc[
                mask,
                "clinical_question"
            ] = result.get(
                "clinical_question",
                ""
            )

            print(
                "    Result:",
                "SUCCESS"
                if result.get(
                    "success",
                    False
                )
                else "FAILED"
            )

            print(
                "    Evidence:",
                len(evidence)
            )

        except Exception as error:

            print(
                "    ERROR:",
                error
            )

    results_df.to_csv(
        RESULTS_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("RETRY COMPLETE")
    print("=" * 70)

    successful = (
        results_df[
            "assessment_success"
        ]
        .fillna(False)
        .astype(bool)
        .sum()
    )

    failed = (
        len(results_df)
        - successful
    )

    print(
        f"\nSuccessful assessments: "
        f"{successful}"
    )

    print(
        f"Failed assessments: "
        f"{failed}"
    )

    print(
        f"\nUpdated results:\n"
        f"{RESULTS_FILE}"
    )


if __name__ == "__main__":
    main()