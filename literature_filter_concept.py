"""
Concept-based literature triage for T2D-EviGuide.

Purpose:
    Triage targeted PubMed literature before permanent RAG ingestion.

Important:
    This is a transparent relevance filter, NOT an evidence-quality assessment
    and NOT a clinical validation system.

Categories:
    - core: directly relevant to early T2D risk assessment
    - supporting: useful contextual/risk-factor evidence
    - review: systematic reviews, meta-analyses, guidelines
    - peripheral: not sufficiently relevant for the current project
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


INPUT = Path("data/pubmed_literature_targeted.csv")
OUTPUT_DIR = Path("reports/literature_concept")


# ---------------------------------------------------------------------
# Concept groups
# ---------------------------------------------------------------------

EARLY_RISK_CONCEPTS = {
    "prediabetes",
    "prediabetic",
    "progression to diabetes",
    "progression to type 2 diabetes",
    "incident diabetes",
    "incident type 2 diabetes",
    "future diabetes",
    "future type 2 diabetes",
    "risk of developing diabetes",
    "risk of developing type 2 diabetes",
    "diabetes development",
    "diabetes onset",
    "new-onset diabetes",
    "screen-detected diabetes",
    "diabetes screening",
    "screening for diabetes",
    "risk prediction",
    "prediction model",
    "predictive model",
    "risk score",
    "risk assessment",
}


GLYCEMIC_ASSESSMENT_CONCEPTS = {
    "hba1c",
    "glycated hemoglobin",
    "glycosylated hemoglobin",
    "fasting plasma glucose",
    "fasting glucose",
    "fasting blood glucose",
    "oral glucose tolerance test",
    "oral glucose tolerance",
    "ogtt",
    "2-hour plasma glucose",
    "two-hour plasma glucose",
    "post-load glucose",
    "impaired fasting glucose",
    "impaired glucose tolerance",
    "glucose intolerance",
}


RISK_FACTOR_CONCEPTS = {
    "obesity",
    "overweight",
    "body mass index",
    "bmi",
    "waist circumference",
    "central obesity",
    "visceral adiposity",
    "physical inactivity",
    "physical activity",
    "sedentary",
    "diet",
    "dietary",
    "family history",
    "hypertension",
    "dyslipidemia",
    "metabolic syndrome",
    "insulin resistance",
    "gestational diabetes",
    "socioeconomic",
    "smoking",
    "age",
}


PREVENTION_CONCEPTS = {
    "diabetes prevention",
    "prevention of diabetes",
    "prevent type 2 diabetes",
    "lifestyle intervention",
    "lifestyle modification",
    "weight loss",
    "weight reduction",
    "physical activity intervention",
    "dietary intervention",
}


GUIDELINE_CONCEPTS = {
    "guideline",
    "guidelines",
    "standard of care",
    "consensus statement",
    "clinical practice guideline",
    "recommendations",
}


# ---------------------------------------------------------------------
# Strong exclusion concepts
#
# These are deliberately stronger than generic keyword matches.
# ---------------------------------------------------------------------

EXCLUSION_CONCEPTS = {
    "retinopathy",
    "neuropathy",
    "nephropathy",
    "diabetic kidney disease",
    "chronic kidney disease",
    "heart failure",
    "myocardial infarction",
    "stroke",
    "cardiovascular complication",
    "vascular complication",
    "carotid atherosclerosis",
    "atherosclerosis",
    "sarcopenia",
    "musculoskeletal pain",
    "cognitive decline",
    "cognition",
    "depression",
    "anxiety",
    "bowel preparation",
    "cancer",
    "carcinogenicity",
    "thyroid cancer",
    "fracture",
    "falls",
    "liver fibrosis",
}


ESTABLISHED_T2D_CONCEPTS = {
    "patients with type 2 diabetes",
    "adults with type 2 diabetes",
    "patients with t2dm",
    "established type 2 diabetes",
    "long-standing diabetes",
    "diabetes duration",
    "diabetes complications",
}


EXPERIMENTAL_CONCEPTS = {
    "mouse",
    "mice",
    "rat",
    "rats",
    "zebrafish",
    "animal model",
    "murine",
    "in vitro",
    "cell culture",
    "cell line",
    "molecular docking",
    "gene expression",
    "transcriptomic",
    "proteomic",
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_any(text: str, concepts: set[str]) -> list[str]:
    return sorted(
        concept for concept in concepts
        if concept in text
    )


def publication_type_score(title: str, abstract: str) -> tuple[int, list[str]]:
    text = f"{title} {abstract}"

    review_terms = [
        "systematic review",
        "meta-analysis",
        "scoping review",
        "narrative review",
        "consensus",
        "guideline",
    ]

    matched = [x for x in review_terms if x in text]

    return (2 if matched else 0, matched)


# ---------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------

def classify(row: dict) -> dict:
    title = normalize(row.get("title", ""))
    abstract = normalize(row.get("abstract", ""))

    text = f"{title} {abstract}"

    early = contains_any(text, EARLY_RISK_CONCEPTS)
    glycemic = contains_any(text, GLYCEMIC_ASSESSMENT_CONCEPTS)
    risk = contains_any(text, RISK_FACTOR_CONCEPTS)
    prevention = contains_any(text, PREVENTION_CONCEPTS)

    exclusions = contains_any(text, EXCLUSION_CONCEPTS)
    established = contains_any(text, ESTABLISHED_T2D_CONCEPTS)
    experimental = contains_any(text, EXPERIMENTAL_CONCEPTS)

    review_bonus, review_matches = publication_type_score(title, abstract)

    score = 0

    # Direct early-risk concepts carry the most weight.
    score += min(len(early), 4) * 4

    # Measurement concepts are important for the actual assessment workflow.
    score += min(len(glycemic), 3) * 3

    # Risk factors provide contextual evidence.
    score += min(len(risk), 4) * 2

    # Prevention is relevant but less central than assessment.
    score += min(len(prevention), 2) * 2

    score += review_bonus

    # Strong exclusions.
    score -= min(len(exclusions), 3) * 5

    # Experimental work should not enter the main clinical evidence pool.
    score -= min(len(experimental), 2) * 5

    # Studies exclusively focused on established T2D get a penalty unless
    # they also contain a strong early-risk concept.
    if established and not early:
        score -= 5

    # -------------------------------------------------------------
    # Decision logic
    # -------------------------------------------------------------

    # Strong direct evidence:
    # must contain an actual early-risk concept OR a clear glycemic
    # assessment concept combined with risk/prediction context.
    if (
        (
            len(early) >= 1
            and (len(risk) >= 1 or len(glycemic) >= 1 or len(prevention) >= 1)
        )
        or
        (
            len(glycemic) >= 1
            and len(risk) >= 1
            and not exclusions
        )
    ):
        category = "core"

    elif review_matches and (
        len(early) >= 1
        or len(glycemic) >= 1
        or len(risk) >= 2
        or len(prevention) >= 1
    ):
        category = "review"

    elif (
        (len(risk) >= 1 or len(prevention) >= 1)
        and len(exclusions) == 0
        and len(experimental) == 0
    ):
        category = "supporting"

    else:
        category = "peripheral"

    # Strong exclusions override weak keyword matches.
    if (
        len(exclusions) >= 2
        and not (
            len(early) >= 2
            and len(glycemic) >= 1
        )
    ):
        category = "peripheral"

    if len(experimental) >= 2 and not early:
        category = "peripheral"

    matched = {
        "early_risk": early,
        "glycemic": glycemic,
        "risk_factors": risk,
        "prevention": prevention,
        "exclusions": exclusions,
        "established_t2d": established,
        "experimental": experimental,
        "publication_type": review_matches,
    }

    matched_string = "; ".join(
        f"{group}={','.join(values)}"
        for group, values in matched.items()
        if values
    )

    return {
        **row,
        "triage_category": category,
        "triage_score": score,
        "matched_concepts": matched_string,
    }


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with INPUT.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        rows = list(csv.DictReader(f))

    classified = [classify(row) for row in rows]

    categories = {
        "core": [],
        "supporting": [],
        "review": [],
        "peripheral": [],
    }

    for row in classified:
        categories[row["triage_category"]].append(row)

    # Save complete classified dataset.
    all_file = OUTPUT_DIR / "pubmed_concept_triage_all.csv"

    fieldnames = list(classified[0].keys())

    with all_file.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(classified)

    # Save category-specific files.
    for category, records in categories.items():

        path = OUTPUT_DIR / f"pubmed_{category}.csv"

        with path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(records)

    # Highest-scoring candidates for manual review.
    candidates = sorted(
        classified,
        key=lambda x: int(x["triage_score"]),
        reverse=True
    )

    top_file = OUTPUT_DIR / "top_candidates_for_review.csv"

    with top_file.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(candidates[:50])

    # Human-readable report.
    report = OUTPUT_DIR / "concept_triage_report.txt"

    with report.open(
        "w",
        encoding="utf-8"
    ) as f:

        f.write("T2D-EviGuide Concept-Based PubMed Triage\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"Input records: {len(rows)}\n")

        for category in [
            "core",
            "supporting",
            "review",
            "peripheral",
        ]:
            f.write(
                f"{category}: "
                f"{len(categories[category])}\n"
            )

        f.write("\n")
        f.write(
            "This is a transparent relevance triage, "
            "not a clinical evidence-quality assessment.\n"
        )
        f.write(
            "Human review is required before permanent "
            "RAG ingestion.\n\n"
        )

        f.write("Top 50 candidates:\n")
        f.write("-" * 50 + "\n")

        for row in candidates[:50]:
            f.write(
                f"{row['triage_category']:12} "
                f"{row['triage_score']:>3} "
                f"{row.get('pmid', '')} "
                f"{row.get('title', '')}\n"
            )

    print("Concept-based triage complete.")
    print(f"Input records: {len(rows)}")

    for category in [
        "core",
        "supporting",
        "review",
        "peripheral",
    ]:
        print(
            f"{category}: "
            f"{len(categories[category])}"
        )

    print(f"\nOutput directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()