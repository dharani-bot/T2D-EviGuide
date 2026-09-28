import os
import pandas as pd

from clinical_assessment import generate_risk_assessment


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
    "t2d_mimic_evaluation.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "real_clinical_data",
    "mimic_evaluation_results.csv"
)


# ============================================================
# HELPERS
# ============================================================

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

    # --------------------------------------------------------
    # Diagnosis context
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Prescription context
    # --------------------------------------------------------

    prescription_history = safe_value(
        row.get("prescription_history")
    )

    if prescription_history == "Not available":

        medications = (
            "Prescription history not available."
        )

    elif prescription_history == "":

        medications = (
            "No prescription history recorded in the "
            "evaluation record."
        )

    else:

        medications = (
            "MIMIC-IV prescription history: "
            + str(prescription_history)
            + ". This is historical/inpatient prescription "
              "data and is not assumed to represent current "
              "outpatient medication use."
        )

    # --------------------------------------------------------
    # IMPORTANT:
    # These variables are deliberately NOT fabricated.
    # --------------------------------------------------------

    patient = {

        "age": age,

        "sex": sex,

        "weight": "Not available",

        "height": "Not available",

        "bmi": "Not available",

        # Fasting glucose is NOT available.
        "fasting_glucose": (
            "Not available; fasting status was not "
            "established in the MIMIC-IV data."
        ),

        # This is available inpatient blood glucose.
        "blood_glucose": (
            f"{blood_glucose} mg/dL"
            " (mean available inpatient blood glucose; "
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

    return patient


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("T2D-EviGuide MIMIC-IV Real-Data Evaluation")
    print("=" * 70)
    print()

    if not os.path.exists(INPUT_FILE):

        raise FileNotFoundError(
            f"Evaluation input file not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Evaluation cases found: {len(df)}"
    )

    print()

    results = []

    for index, row in df.iterrows():

        evaluation_id = row.get(
            "evaluation_id",
            f"MIMIC-EVAL-{index + 1:03d}"
        )

        subject_id = row.get(
            "subject_id",
            "Unknown"
        )

        print(
            f"[{index + 1}/{len(df)}] "
            f"{evaluation_id} "
            f"(subject_id={subject_id})"
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

            evidence_ids = []

            for item in evidence:

                evidence_ids.append(
                    item.get(
                        "article_id",
                        ""
                    )
                )

            results.append({

                "evaluation_id":
                    evaluation_id,

                "subject_id":
                    subject_id,

                "age":
                    row.get("anchor_age"),

                "sex":
                    row.get("gender"),

                "blood_glucose_mean":
                    row.get(
                        "blood_glucose_mean"
                    ),

                "hba1c_mean":
                    row.get(
                        "hba1c_mean"
                    ),

                "evaluation_group":
                    row.get(
                        "evaluation_group"
                    ),

                "diagnosis_group":
                    row.get(
                        "diagnosis_group"
                    ),

                "has_diabetes_related_diagnosis":
                    row.get(
                        "has_diabetes_related_diagnosis"
                    ),

                "assessment_success":
                    result.get(
                        "success",
                        False
                    ),

                "evidence_count":
                    len(evidence),

                "evidence_ids":
                    " | ".join(
                        evidence_ids
                    ),

                "assessment":
                    result.get(
                        "assessment",
                        ""
                    ),

                "patient_summary":
                    result.get(
                        "patient_summary",
                        ""
                    ),

                "clinical_question":
                    result.get(
                        "clinical_question",
                        ""
                    )
            })

            print(
                "    Assessment:",
                "SUCCESS"
                if result.get(
                    "success",
                    False
                )
                else "FAILED"
            )

            print(
                "    Evidence retrieved:",
                len(evidence)
            )

        except Exception as error:

            print(
                "    ERROR:",
                error
            )

            results.append({

                "evaluation_id":
                    evaluation_id,

                "subject_id":
                    subject_id,

                "age":
                    row.get(
                        "anchor_age"
                    ),

                "sex":
                    row.get(
                        "gender"
                    ),

                "blood_glucose_mean":
                    row.get(
                        "blood_glucose_mean"
                    ),

                "hba1c_mean":
                    row.get(
                        "hba1c_mean"
                    ),

                "evaluation_group":
                    row.get(
                        "evaluation_group"
                    ),

                "diagnosis_group":
                    row.get(
                        "diagnosis_group"
                    ),

                "has_diabetes_related_diagnosis":
                    row.get(
                        "has_diabetes_related_diagnosis"
                    ),

                "assessment_success":
                    False,

                "evidence_count":
                    0,

                "evidence_ids":
                    "",

                "assessment":
                    f"Evaluation error: {error}",

                "patient_summary":
                    "",

                "clinical_question":
                    ""
            })

    # ========================================================
    # SAVE
    # ========================================================

    results_df = pd.DataFrame(
        results
    )

    results_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

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

    print()
    print("=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)

    print(
        f"\nCases processed: "
        f"{len(results_df)}"
    )

    print(
        f"Successful assessments: "
        f"{successful}"
    )

    print(
        f"Failed assessments: "
        f"{failed}"
    )

    print(
        f"\nResults saved to:\n"
        f"{OUTPUT_FILE}"
    )

    print()


if __name__ == "__main__":

    main()