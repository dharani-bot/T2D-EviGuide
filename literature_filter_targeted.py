#!/usr/bin/env python3

"""
T2D-EviGuide Targeted PubMed Literature Triage

Input:
    data/pubmed_literature_targeted.csv

Output:
    reports/literature_targeted/
        pubmed_all.csv
        pubmed_core.csv
        pubmed_supporting.csv
        pubmed_review.csv
        pubmed_peripheral.csv
        literature_triage_report.txt

Purpose:
    Perform transparent, rule-based relevance triage of the targeted
    PubMed literature collection.

IMPORTANT:
    This is a relevance triage system, NOT a clinical evidence-quality
    assessment. Human review is required before permanent RAG ingestion.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path("data/pubmed_literature_targeted.csv")

OUTPUT_DIR = Path("reports/literature_targeted")

OUTPUT_ALL = OUTPUT_DIR / "pubmed_all.csv"
OUTPUT_CORE = OUTPUT_DIR / "pubmed_core.csv"
OUTPUT_SUPPORTING = OUTPUT_DIR / "pubmed_supporting.csv"
OUTPUT_REVIEW = OUTPUT_DIR / "pubmed_review.csv"
OUTPUT_PERIPHERAL = OUTPUT_DIR / "pubmed_peripheral.csv"
REPORT_FILE = OUTPUT_DIR / "literature_triage_report.txt"


# ============================================================
# KEYWORD GROUPS
# ============================================================

# Strong signals that an article is directly relevant to
# early T2D risk assessment.

CORE_TERMS = [
    "prediabetes",
    "pre-diabetes",
    "incident type 2 diabetes",
    "incident diabetes",
    "progression to type 2 diabetes",
    "progression to diabetes",
    "diabetes screening",
    "diabetes risk prediction",
    "type 2 diabetes risk prediction",
    "risk prediction model",
    "risk score",
    "early detection",
    "early risk",
    "hba1c",
    "glycated hemoglobin",
    "glycosylated hemoglobin",
    "fasting plasma glucose",
    "fasting glucose",
    "oral glucose tolerance",
    "ogtt",
    "diagnostic criteria",
    "diagnosis",
    "screening",
    "diabetes prevention",
]


# Supporting evidence is useful for contextualising
# patient risk but is not necessarily central to early
# risk assessment.

SUPPORTING_TERMS = [
    "obesity",
    "overweight",
    "body mass index",
    "bmi",
    "physical activity",
    "exercise",
    "diet",
    "lifestyle",
    "weight loss",
    "hypertension",
    "blood pressure",
    "family history",
    "genetic",
    "metabolic syndrome",
    "insulin resistance",
    "waist circumference",
    "visceral adiposity",
    "lipid",
    "triglyceride",
    "cholesterol",
    "sleep apnea",
    "sleep apnoea",
    "clinical guideline",
    "guideline",
    "consensus",
    "prevention",
]


# Topics that generally indicate the paper concerns
# established diabetes or downstream complications rather
# than early risk assessment.

PERIPHERAL_TERMS = [
    "diabetic retinopathy",
    "retinopathy",
    "neuropathy",
    "nephropathy",
    "kidney disease",
    "chronic kidney disease",
    "egfr",
    "albuminuria",
    "sarcopenia",
    "falls",
    "fracture",
    "cancer",
    "tumor",
    "cognitive decline",
    "dementia",
    "depression",
    "anxiety",
    "bowel preparation",
    "stroke",
    "heart failure",
    "carotid",
    "atherosclerosis",
    "vascular complication",
    "diabetic foot",
    "wound",
]


# Experimental/preclinical topics should normally not become
# permanent core evidence for an early-risk clinical system.

EXPERIMENTAL_TERMS = [
    "animal model",
    "mice",
    "mouse model",
    "rat model",
    "zebrafish",
    "in vitro",
    "cell culture",
    "cell line",
    "molecular mechanism",
    "gene expression",
    "transcriptomic",
    "proteomic",
    "metabolomic",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize(text: str) -> str:
    """
    Normalize text for keyword matching.
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def count_matches(text: str, terms: list[str]) -> int:
    """
    Count how many distinct keyword phrases occur in the text.
    """
    return sum(1 for term in terms if term in text)


def get_field(row: dict, field: str) -> str:
    """
    Safely retrieve a CSV field.
    """
    value = row.get(field, "")
    if value is None:
        return ""
    return str(value)


def classify_article(row: dict) -> tuple[str, int, list[str]]:
    """
    Assign an article to:

        core
        supporting
        review
        peripheral

    Returns:
        category, score, matched_terms
    """

    title = normalize(get_field(row, "title"))
    abstract = normalize(get_field(row, "abstract"))
    topic = normalize(get_field(row, "topic"))
    publication_types = normalize(get_field(row, "publication_types"))

    text = f"{title} {abstract}"

    core_matches = [
        term for term in CORE_TERMS
        if term in text
    ]

    supporting_matches = [
        term for term in SUPPORTING_TERMS
        if term in text
    ]

    peripheral_matches = [
        term for term in PERIPHERAL_TERMS
        if term in text
    ]

    experimental_matches = [
        term for term in EXPERIMENTAL_TERMS
        if term in text
    ]

    # --------------------------------------------------------
    # Base score
    # --------------------------------------------------------

    score = 0

    # Stronger weight for direct early-risk concepts.
    score += len(core_matches) * 3

    # Supporting concepts receive lower weight.
    score += len(supporting_matches)

    # Peripheral concepts reduce relevance.
    score -= len(peripheral_matches) * 2

    # Experimental evidence receives a penalty.
    score -= len(experimental_matches) * 2

    # --------------------------------------------------------
    # Topic-specific bonuses
    # --------------------------------------------------------

    high_value_topics = {
        "early_risk",
        "prediabetes_progression",
        "screening",
        "diagnosis",
        "hba1c",
        "fasting_glucose",
        "oral_glucose_tolerance",
        "risk_prediction",
        "prevention",
    }

    if topic in high_value_topics:
        score += 3

    if topic == "risk_factors":
        score += 2

    if topic == "lifestyle":
        score += 2

    if topic == "clinical_guidelines":
        score += 3

    # --------------------------------------------------------
    # Publication type information
    # --------------------------------------------------------

    is_systematic_review = (
        "systematic review" in publication_types
        or "meta-analysis" in publication_types
    )

    is_guideline = (
        "guideline" in publication_types
        or "practice guideline" in publication_types
    )

    if is_systematic_review:
        score += 2

    if is_guideline:
        score += 3

    # --------------------------------------------------------
    # Strong exclusion conditions
    # --------------------------------------------------------

    # If the article is primarily about established complications
    # and has little direct early-risk content, keep it peripheral.

    if (
        len(peripheral_matches) >= 3
        and len(core_matches) <= 2
    ):
        return (
            "peripheral",
            score,
            peripheral_matches[:10],
        )

    # Strong experimental signal without direct clinical
    # screening/risk content.
    if (
        len(experimental_matches) >= 2
        and len(core_matches) <= 2
    ):
        return (
            "peripheral",
            score,
            experimental_matches[:10],
        )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    if score >= 12 and len(core_matches) >= 2:
        category = "core"

    elif score >= 7:
        category = "supporting"

    elif is_systematic_review or is_guideline:
        category = "review"

    elif score >= 3:
        category = "review"

    else:
        category = "peripheral"

    matched_terms = (
        core_matches[:8]
        + supporting_matches[:8]
        + peripheral_matches[:5]
    )

    return category, score, matched_terms


# ============================================================
# LOAD CSV
# ============================================================

def load_records() -> list[dict]:
    """
    Load PubMed records from CSV.
    """

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_FILE}\n\n"
            "Make sure you have already run:\n"
            "python literature_search_targeted.py"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        records = list(reader)

    return records


# ============================================================
# WRITE CSV
# ============================================================

def write_csv(path: Path, records: list[dict]) -> None:
    """
    Write records to CSV.
    """

    if not records:
        return

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = list(records[0].keys())

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(records)


# ============================================================
# MAIN TRIAGE
# ============================================================

def main() -> None:

    print("=" * 60)
    print(" T2D-EviGuide Targeted PubMed Literature Triage")
    print("=" * 60)

    records = load_records()

    print(f"Input records: {len(records)}")

    classified = {
        "core": [],
        "supporting": [],
        "review": [],
        "peripheral": [],
    }

    # --------------------------------------------------------
    # Classify each article
    # --------------------------------------------------------

    for row in records:

        category, score, matched_terms = classify_article(row)

        # Add transparent classification metadata.
        row["triage_category"] = category
        row["triage_score"] = str(score)
        row["matched_terms"] = "; ".join(matched_terms)

        classified[category].append(row)

    # --------------------------------------------------------
    # Sort each group by relevance score
    # --------------------------------------------------------

    for category in classified:

        classified[category].sort(
            key=lambda r: int(
                r.get("triage_score", "0") or 0
            ),
            reverse=True,
        )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Write files
    # --------------------------------------------------------

    write_csv(
        OUTPUT_ALL,
        records
    )

    write_csv(
        OUTPUT_CORE,
        classified["core"]
    )

    write_csv(
        OUTPUT_SUPPORTING,
        classified["supporting"]
    )

    write_csv(
        OUTPUT_REVIEW,
        classified["review"]
    )

    write_csv(
        OUTPUT_PERIPHERAL,
        classified["peripheral"]
    )

    # --------------------------------------------------------
    # Create report
    # --------------------------------------------------------

    report_lines = []

    report_lines.append(
        "T2D-EviGuide Targeted PubMed Literature Triage"
    )

    report_lines.append(
        "=" * 45
    )

    report_lines.append(
        f"Input records: {len(records)}"
    )

    report_lines.append(
        f"core: {len(classified['core'])}"
    )

    report_lines.append(
        f"supporting: {len(classified['supporting'])}"
    )

    report_lines.append(
        f"review: {len(classified['review'])}"
    )

    report_lines.append(
        f"peripheral: {len(classified['peripheral'])}"
    )

    report_lines.append("")

    report_lines.append(
        "This is a transparent rule-based relevance "
        "triage, not a clinical evidence-quality assessment."
    )

    report_lines.append(
        "Human review is required before permanent RAG ingestion."
    )

    report_lines.append("")

    # --------------------------------------------------------
    # Top records
    # --------------------------------------------------------

    all_sorted = sorted(
        records,
        key=lambda r: int(
            r.get("triage_score", "0") or 0
        ),
        reverse=True,
    )

    report_lines.append(
        "Top 30 records:"
    )

    report_lines.append("")

    for row in all_sorted[:30]:

        category = row.get(
            "triage_category",
            ""
        )

        score = row.get(
            "triage_score",
            ""
        )

        pmid = row.get(
            "pmid",
            ""
        )

        title = row.get(
            "title",
            ""
        )

        report_lines.append(
            f"{category:<11} "
            f"{score:>3} "
            f"{pmid} "
            f"{title}"
        )

    report_lines.append("")

    # --------------------------------------------------------
    # Topic distribution
    # --------------------------------------------------------

    topic_counts = {}

    for row in records:

        topic = row.get(
            "topic",
            "unknown"
        )

        topic_counts[topic] = (
            topic_counts.get(topic, 0) + 1
        )

    report_lines.append(
        "Topic distribution:"
    )

    report_lines.append("")

    for topic, count in sorted(
        topic_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    ):

        report_lines.append(
            f"{topic:<30} {count}"
        )

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    REPORT_FILE.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Terminal summary
    # --------------------------------------------------------

    print()

    print(
        f"core       : {len(classified['core'])}"
    )

    print(
        f"supporting : {len(classified['supporting'])}"
    )

    print(
        f"review     : {len(classified['review'])}"
    )

    print(
        f"peripheral : {len(classified['peripheral'])}"
    )

    print()

    print(
        f"Outputs: {OUTPUT_DIR}"
    )

    print()

    print(
        "Human review is required before permanent RAG ingestion."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()