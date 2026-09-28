from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "real_clinical_data"

lab_items = pd.read_csv(
    DATA_DIR / "d_labitems.csv.gz",
    compression="gzip"
)

print("=" * 70)
print("MIMIC-IV LABORATORY ITEM INSPECTION")
print("=" * 70)

print("\nAll glucose-related items:\n")

glucose = lab_items[
    lab_items["label"]
    .fillna("")
    .str.contains("glucose", case=False, na=False)
]

print(
    glucose[
        ["itemid", "label", "fluid", "category"]
    ].to_string(index=False)
)

print("\n" + "=" * 70)
print("HbA1c-related items")
print("=" * 70)

hba1c = lab_items[
    lab_items["label"]
    .fillna("")
    .str.contains(
        "a1c|glycated hemoglobin",
        case=False,
        regex=True,
        na=False
    )
]

print(
    hba1c[
        ["itemid", "label", "fluid", "category"]
    ].to_string(index=False)
)

print("\n" + "=" * 70)
print("Done")
print("=" * 70)