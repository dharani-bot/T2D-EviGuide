import pandas as pd
import re


INPUT_FILE = (
    "data/real_clinical_data/mimic_guardrail_v2_manual_review.csv"
)

OUTPUT_FILE = (
    "data/real_clinical_data/mimic_guardrail_v2_sentence_review.csv"
)


df = pd.read_csv(INPUT_FILE)


def extract_relevant_sentences(text):
    text = str(text)

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    keywords = [
        "IGT",
        "impaired glucose tolerance",
        "fasting",
        "threshold",
        "cutoff",
        "criterion",
        "diagnos",
        "confirms diabetes",
        "confirmed diabetes",
        "diagnostic",
        "inpatient blood glucose",
    ]

    relevant = []

    for sentence in sentences:
        sentence_clean = sentence.strip()

        if not sentence_clean:
            continue

        if any(
            keyword.lower() in sentence_clean.lower()
            for keyword in keywords
        ):
            relevant.append(sentence_clean)

    return " || ".join(relevant)


flagged = df[df["any_flag"] == True].copy()

flagged["relevant_sentences"] = flagged[
    "assessment"
].apply(extract_relevant_sentences)


columns = [
    "evaluation_id",
    "hba1c_mean",
    "blood_glucose_mean",
    "hba1c_igt_flag",
    "fasting_flag",
    "threshold_flag",
    "diagnostic_language_flag",
    "relevant_sentences",
]


review = flagged[columns]

review.to_csv(
    OUTPUT_FILE,
    index=False
)


print("========================================")
print("V2 SENTENCE-LEVEL MANUAL REVIEW")
print("========================================")

print()

print(
    "Flagged assessments:",
    len(review)
)

print()

print("Saved to:")
print(OUTPUT_FILE)

print()

for _, row in review.iterrows():

    print("=" * 80)

    print(
        f"{row['evaluation_id']} | "
        f"HbA1c={row['hba1c_mean']} | "
        f"Glucose={row['blood_glucose_mean']}"
    )

    print(
        f"HbA1c/IGT: {row['hba1c_igt_flag']} | "
        f"Fasting: {row['fasting_flag']} | "
        f"Threshold: {row['threshold_flag']} | "
        f"Diagnostic: {row['diagnostic_language_flag']}"
    )

    print()

    print(row["relevant_sentences"])

    print()