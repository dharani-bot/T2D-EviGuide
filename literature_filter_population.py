"""
T2D-EviGuide Population-Aware Literature Triage v2

Purpose:
    Filter targeted PubMed literature according to:
    1. Study population
    2. Early-T2D-risk relevance
    3. Clinical measurement relevance
    4. Study design/publication type
    5. Explicit exclusion concepts

This is a transparent relevance-triage system.
It is NOT a clinical evidence-quality assessment.
Human review is required before permanent RAG ingestion.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


# ============================================================
# Paths
# ============================================================

INPUT = Path("data/pubmed_literature_targeted.csv")

OUTPUT_DIR = Path("reports/literature_population")


# ============================================================
# Population concepts
# ============================================================

CORE_POPULATIONS = {
    "prediabetes",
    "prediabetic",
    "impaired fasting glucose",
    "impaired glucose tolerance",
    "at risk for diabetes",
    "at-risk for diabetes",
    "high risk for diabetes",
    "high-risk for diabetes",
    "diabetes risk",
    "future diabetes",
    "incident diabetes",
    "incident type 2 diabetes",
    "develop type 2 diabetes",
    "developing type 2 diabetes",
    "develop type 2 diabetes mellitus",
    "screening for diabetes",
    "diabetes screening",
    "screen-detected diabetes",
    "undiagnosed diabetes",
    "without diabetes",
    "non-diabetic",
    "nondiabetic",
    "general population",
    "community-dwelling adults",
    "primary care",
}


SPECIAL_POPULATIONS = {
    "gestational diabetes",
    "gestational diabetes mellitus",
    "pregnancy",
    "pregnant women",
    "postpartum",
    "postpartum women",
    "women with prior gestational diabetes",
    "hiv",
    "tuberculosis",
    "tuberculosis-associated hyperglycemia",
    "pancreatitis",
    "post-pancreatitis diabetes",
    "pancreatic disease",
    "cystic fibrosis",
    "liver cirrhosis",
    "hepatogenous diabetes",
    "adrenal adenoma",
}


ESTABLISHED_T2D = {
    "patients with type 2 diabetes",
    "adults with type 2 diabetes",
    "people with type 2 diabetes",
    "patients with t2dm",
    "adults with t2dm",
    "established type 2 diabetes",
    "long-standing type 2 diabetes",
    "diabetes duration",
    "diabetes complications",
}


# ============================================================
# Early-risk concepts
# ============================================================

EARLY_RISK = {
    "prediabetes",
    "prediabetic",
    "progression to type 2 diabetes",
    "progression to diabetes",
    "incident type 2 diabetes",
    "incident diabetes",
    "development of type 2 diabetes",
    "developing type 2 diabetes",
    "new-onset diabetes",
    "future diabetes",
    "future type 2 diabetes",
    "risk of developing diabetes",
    "risk of developing type 2 diabetes",
    "diabetes risk",
    "risk prediction",
    "risk prediction model",
    "prediction model",
    "predictive model",
    "risk score",
    "risk assessment",
    "screening",
    "screen-detected diabetes",
}


# ============================================================
# Glycaemic assessment concepts
# ============================================================

GLYCEMIC = {
    "hba1c",
    "glycated hemoglobin",
    "glycated haemoglobin",
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
}


# ============================================================
# Risk-factor concepts
# ============================================================

RISK_FACTORS = {
    "obesity",
    "overweight",
    "body mass index",
    "bmi",
    "waist circumference",
    "waist-to-height ratio",
    "central obesity",
    "visceral adiposity",
    "physical activity",
    "physical inactivity",
    "sedentary",
    "diet",
    "dietary",
    "family history",
    "family history of diabetes",
    "hypertension",
    "dyslipidemia",
    "metabolic syndrome",
    "insulin resistance",
    "age",
    "smoking",
    "alcohol",
}


# ============================================================
# Prevention concepts
# ============================================================

PREVENTION = {
    "diabetes prevention",
    "prevention of diabetes",
    "prevent type 2 diabetes",
    "diabetes prevention program",
    "lifestyle intervention",
    "lifestyle modification",
    "weight loss",
    "weight reduction",
    "physical activity intervention",
    "dietary intervention",
}


# ============================================================
# Review / guideline concepts
# ============================================================

REVIEW_TYPES = {
    "systematic review",
    "meta-analysis",
    "scoping review",
    "umbrella review",
    "narrative review",
    "consensus statement",
    "clinical practice guideline",
    "guideline",
    "guidelines",
    "standard of care",
    "recommendations",
}


# ============================================================
# Strong exclusion concepts
# ============================================================

COMPLICATIONS = {
    "retinopathy",
    "neuropathy",
    "nephropathy",
    "diabetic kidney disease",
    "chronic kidney disease",
    "heart failure",
    "myocardial infarction",
    "stroke",
    "cardiovascular complications",
    "cardiovascular complication",
    "vascular complications",
    "vascular complication",
    "carotid atherosclerosis",
    "atherosclerosis",
    "macrovascular complications",
    "microvascular complications",
}


NON_TARGET_OUTCOMES = {
    "sarcopenia",
    "musculoskeletal pain",
    "cognitive decline",
    "cognitive function",
    "depression",
    "anxiety",
    "bowel preparation",
    "falls",
    "fracture",
    "cancer",
    "carcinogenicity",
    "thyroid cancer",
    "liver fibrosis",
    "cirrhosis",
}


EXPERIMENTAL = {
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


# ============================================================
# Utility functions
# ============================================================

def normalize(text: str) -> str:
    """
    Convert text to lowercase and normalize whitespace.
    """

    text = text or ""

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def find_matches(
    text: str,
    concepts: set[str]
) -> list[str]:
    """
    Match concepts using word boundaries.

    This is important because simple substring matching can
    create false positives.

    Example:
        'rat' should NOT match 'stratification'.

    Multi-word concepts such as:
        'type 2 diabetes'
        'risk prediction model'

    are also supported.
    """

    matches = []

    for concept in concepts:

        pattern = (
            r"\b"
            + re.escape(concept)
            + r"\b"
        )

        if re.search(pattern, text):

            matches.append(concept)

    return sorted(matches)


def has_any(matches: list[str]) -> bool:
    return len(matches) > 0


# ============================================================
# Classification
# ============================================================

def classify(row: dict) -> dict:

    title = normalize(
        row.get("title", "")
    )

    abstract = normalize(
        row.get("abstract", "")
    )

    text = f"{title} {abstract}"

    # --------------------------------------------------------
    # Match concepts
    # --------------------------------------------------------

    core_population = find_matches(
        text,
        CORE_POPULATIONS
    )

    special_population = find_matches(
        text,
        SPECIAL_POPULATIONS
    )

    established = find_matches(
        text,
        ESTABLISHED_T2D
    )

    early_risk = find_matches(
        text,
        EARLY_RISK
    )

    glycemic = find_matches(
        text,
        GLYCEMIC
    )

    risk_factors = find_matches(
        text,
        RISK_FACTORS
    )

    prevention = find_matches(
        text,
        PREVENTION
    )

    review_types = find_matches(
        text,
        REVIEW_TYPES
    )

    complications = find_matches(
        text,
        COMPLICATIONS
    )

    non_target = find_matches(
        text,
        NON_TARGET_OUTCOMES
    )

    experimental = find_matches(
        text,
        EXPERIMENTAL
    )

    # --------------------------------------------------------
    # Determine population
    # --------------------------------------------------------

    if experimental:

        population = "experimental"

    elif special_population:

        population = "special_population"

    elif established and not core_population:

        population = "established_t2d"

    elif core_population:

        population = "core_population"

    else:

        population = "other"

    # --------------------------------------------------------
    # Calculate relevance score
    # --------------------------------------------------------

    score = 0

    # Core population gets the strongest positive weight.
    if population == "core_population":

        score += 10

    elif population == "special_population":

        score += 2

    elif population == "established_t2d":

        score -= 4

    elif population == "experimental":

        score -= 10

    # Early-risk concepts.
    score += (
        min(len(early_risk), 3)
        * 4
    )

    # Glycaemic assessment concepts.
    score += (
        min(len(glycemic), 3)
        * 2
    )

    # Risk factors.
    score += (
        min(len(risk_factors), 4)
        * 1
    )

    # Prevention.
    score += (
        min(len(prevention), 2)
        * 2
    )

    # Review/guideline bonus.
    if review_types:

        score += 3

    # Exclusion penalties.
    score -= (
        min(len(complications), 3)
        * 5
    )

    score -= (
        min(len(non_target), 2)
        * 4
    )

    score -= (
        min(len(experimental), 2)
        * 8
    )

    # Special populations are contextual rather than
    # automatically generalizable to the core population.
    if population == "special_population":

        score -= 5

    # Established T2D is not the main target population.
    if population == "established_t2d":

        score -= 5

    # --------------------------------------------------------
    # Category assignment
    # --------------------------------------------------------

    # CORE
    #
    # Requires:
    #   - core population
    #   - direct early-risk or measurement/risk relevance
    #   - no experimental evidence
    #   - no strong complication/non-target focus
    #
    if (
        population == "core_population"
        and (
            has_any(early_risk)
            or (
                has_any(glycemic)
                and has_any(risk_factors)
            )
        )
        and not experimental
        and not complications
        and not non_target
    ):

        category = "core"

    # REVIEW
    #
    # Relevant review/guideline for the core population.
    elif (
        review_types
        and population == "core_population"
        and (
            has_any(early_risk)
            or has_any(glycemic)
            or has_any(risk_factors)
            or has_any(prevention)
        )
    ):

        category = "review"

    # SUPPORTING
    #
    # Contextual evidence that can support the system but
    # should not be treated as direct core early-risk evidence.
    elif (
        (
            has_any(risk_factors)
            or has_any(prevention)
            or has_any(glycemic)
        )
        and not experimental
        and len(complications) == 0
    ):

        category = "supporting"

    else:

        category = "peripheral"

    # --------------------------------------------------------
    # Final overrides
    # --------------------------------------------------------

    # Experimental evidence is never core/review.
    if experimental:

        category = "peripheral"

    # Complication-focused studies cannot be core.
    if len(complications) >= 1:

        if category == "core":

            category = "supporting"

        if len(complications) >= 2:

            category = "peripheral"

    # Special populations cannot be core.
    if population == "special_population":

        if category == "core":

            category = "supporting"

    # Established T2D cannot be core.
    if population == "established_t2d":

        if category == "core":

            category = "supporting"

    # --------------------------------------------------------
    # Matched concepts
    # --------------------------------------------------------

    groups = {

        "population": core_population,

        "special_population": special_population,

        "established_t2d": established,

        "early_risk": early_risk,

        "glycemic": glycemic,

        "risk_factors": risk_factors,

        "prevention": prevention,

        "review_type": review_types,

        "complications": complications,

        "non_target_outcomes": non_target,

        "experimental": experimental,
    }

    matched = "; ".join(
        f"{name}={','.join(values)}"
        for name, values in groups.items()
        if values
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        **row,

        "population_class":
            population,

        "triage_category":
            category,

        "triage_score":
            score,

        "matched_concepts":
            matched,
    }


# ============================================================
# Main
# ============================================================

def main():

    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    if not INPUT.exists():

        raise FileNotFoundError(
            f"Input file not found: {INPUT}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    with INPUT.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        rows = list(
            csv.DictReader(f)
        )

    if not rows:

        raise ValueError(
            "Input CSV contains no records."
        )

    # --------------------------------------------------------
    # Classify records
    # --------------------------------------------------------

    classified = [
        classify(row)
        for row in rows
    ]

    # --------------------------------------------------------
    # Category containers
    # --------------------------------------------------------

    categories = {

        "core": [],

        "supporting": [],

        "review": [],

        "peripheral": [],
    }

    for row in classified:

        category = row[
            "triage_category"
        ]

        categories[
            category
        ].append(row)

    # --------------------------------------------------------
    # Population counts
    # --------------------------------------------------------

    populations = {}

    for row in classified:

        population = row[
            "population_class"
        ]

        populations.setdefault(
            population,
            0
        )

        populations[
            population
        ] += 1

    # --------------------------------------------------------
    # CSV field names
    # --------------------------------------------------------

    fieldnames = list(
        classified[0].keys()
    )

    # --------------------------------------------------------
    # Save complete classified dataset
    # --------------------------------------------------------

    all_file = (
        OUTPUT_DIR
        / "pubmed_population_triage_all.csv"
    )

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

        writer.writerows(
            classified
        )

    # --------------------------------------------------------
    # Save category files
    # --------------------------------------------------------

    for category, records in categories.items():

        path = (
            OUTPUT_DIR
            / f"pubmed_{category}.csv"
        )

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

            writer.writerows(
                records
            )

    # --------------------------------------------------------
    # Sort candidates
    # --------------------------------------------------------

    candidates = sorted(
        classified,
        key=lambda row: (
            int(row["triage_score"]),

            row["triage_category"] == "core",

            row.get("title", ""),
        ),

        reverse=True,
    )

    # --------------------------------------------------------
    # Save top candidates
    # --------------------------------------------------------

    top_file = (
        OUTPUT_DIR
        / "top_candidates_for_review.csv"
    )

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

        writer.writerows(
            candidates[:50]
        )

    # --------------------------------------------------------
    # Create report
    # --------------------------------------------------------

    report = (
        OUTPUT_DIR
        / "population_triage_report.txt"
    )

    with report.open(
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "T2D-EviGuide Population-Aware "
            "PubMed Triage v2\n"
        )

        f.write(
            "=" * 55
            + "\n\n"
        )

        f.write(
            f"Input records: {len(rows)}\n\n"
        )

        # Category distribution.
        f.write(
            "Category distribution:\n"
        )

        for category in [
            "core",
            "supporting",
            "review",
            "peripheral",
        ]:

            f.write(
                f"{category:12} "
                f"{len(categories[category])}\n"
            )

        # Population distribution.
        f.write(
            "\nPopulation distribution:\n"
        )

        for population, count in sorted(
            populations.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        ):

            f.write(
                f"{population:22} "
                f"{count}\n"
            )

        f.write("\n")

        f.write(
            "This is a transparent rule-based "
            "relevance triage, not a clinical "
            "evidence-quality assessment.\n"
        )

        f.write(
            "Human review is required before "
            "permanent RAG ingestion.\n\n"
        )

        # Top candidates.
        f.write(
            "Top 50 candidates for manual review:\n"
        )

        f.write(
            "-" * 55
            + "\n"
        )

        for row in candidates[:50]:

            f.write(

                f"{row['triage_category']:12} "

                f"{row['population_class']:20} "

                f"{int(row['triage_score']):>3} "

                f"{row.get('pmid', '')} "

                f"{row.get('title', '')}\n"
            )

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    print()

    print(
        "T2D-EviGuide Population-Aware "
        "Literature Triage v2"
    )

    print(
        "=" * 50
    )

    print(
        f"Input records: {len(rows)}"
    )

    print()

    print(
        "Categories:"
    )

    for category in [
        "core",
        "supporting",
        "review",
        "peripheral",
    ]:

        print(
            f"{category:12} "
            f"{len(categories[category])}"
        )

    print()

    print(
        "Populations:"
    )

    for population, count in sorted(
        populations.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    ):

        print(
            f"{population:22} "
            f"{count}"
        )

    print()

    print(
        "Report:"
    )

    print(
        report
    )


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    main()

    #dharani