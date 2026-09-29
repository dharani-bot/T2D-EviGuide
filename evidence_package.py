from retrieval import search_evidence


# ============================================================
# CONFIGURATION
# ============================================================

# Terms that are directly relevant to the T2D early-risk
# assessment workflow.
CORE_T2D_TERMS = {
    "type 2 diabetes",
    "type 2 diabetes mellitus",
    "diabetes mellitus",
    "prediabetes",
    "diabetes risk",
    "diabetes screening",
    "diabetes prevention",
    "early diabetes",
    "incident diabetes",
}


# Clinical measurement terms relevant to this project.
MEASUREMENT_TERMS = {
    "hba1c",
    "hemoglobin a1c",
    "glycated hemoglobin",
    "fasting glucose",
    "fasting plasma glucose",
    "blood glucose",
    "plasma glucose",
    "oral glucose tolerance",
    "ogtt",
    "impaired fasting glucose",
    "ifg",
    "impaired glucose tolerance",
    "igt",
}


# Risk-factor terms relevant to early T2D assessment.
RISK_FACTOR_TERMS = {
    "bmi",
    "body mass index",
    "obesity",
    "overweight",
    "body weight",
    "physical activity",
    "sedentary",
    "family history",
    "hypertension",
    "blood pressure",
    "smoking",
    "age",
    "lifestyle",
}


# Terms that commonly indicate an unrelated clinical passage.
#
# These are NOT automatically considered bad if they appear
# alongside clearly relevant T2D context. They are used as
# negative signals when the passage is dominated by unrelated
# disease-specific content.
IRRELEVANT_TERMS = {
    "cushing syndrome",
    "cushing's syndrome",
    "adrenal incidentaloma",
    "adrenal lesion",
    "hyperaldosteronism",
    "primary aldosteronism",
    "pheochromocytoma",
    "macs",
    "mild autonomous cortisol secretion",
    "dexamethasone suppression test",
    "dst screening",
    "hypercortisolism",
    "cortisol non-suppression",
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text for simple lexical relevance checks.
    """

    if text is None:
        return ""

    return " ".join(
        str(text)
        .lower()
        .replace("\n", " ")
        .replace("\r", " ")
        .split()
    )


# ============================================================
# QUERY TERM EXTRACTION
# ============================================================

def extract_query_terms(query):
    """
    Identify clinically relevant concepts present in the
    retrieval query.

    This is intentionally simple and transparent.
    """

    query_text = normalize_text(query)

    terms = set()

    all_terms = (
        CORE_T2D_TERMS
        | MEASUREMENT_TERMS
        | RISK_FACTOR_TERMS
    )

    for term in all_terms:

        if term in query_text:

            terms.add(term)

    return terms


# ============================================================
# EVIDENCE RELEVANCE SCORING
# ============================================================

def calculate_relevance_score(
    query,
    result
):
    """
    Calculate a lightweight lexical relevance score.

    This does NOT replace the retrieval model.

    It provides a second-stage quality check so that an
    obviously unrelated passage is less likely to be passed
    to the LLM.
    """

    query_text = normalize_text(
        query
    )

    document_text = normalize_text(
        result.get("document", "")
    )

    metadata = result.get(
        "metadata",
        {}
    )

    title = normalize_text(
        metadata.get(
            "title",
            ""
        )
    )

    category = normalize_text(
        metadata.get(
            "category",
            ""
        )
    )

    combined_text = (
        title
        + " "
        + document_text
        + " "
        + category
    )

    score = 0.0

    # --------------------------------------------------------
    # Query concept overlap
    # --------------------------------------------------------

    query_terms = extract_query_terms(
        query
    )

    matched_query_terms = []

    for term in query_terms:

        if term in combined_text:

            matched_query_terms.append(
                term
            )

            score += 2.0

    # --------------------------------------------------------
    # Strong T2D relevance
    # --------------------------------------------------------

    for term in CORE_T2D_TERMS:

        if term in combined_text:

            score += 3.0

    # --------------------------------------------------------
    # Measurement relevance
    # --------------------------------------------------------

    for term in MEASUREMENT_TERMS:

        if term in combined_text:

            score += 2.5

    # --------------------------------------------------------
    # Risk-factor relevance
    # --------------------------------------------------------

    for term in RISK_FACTOR_TERMS:

        if term in combined_text:

            score += 1.5

    # --------------------------------------------------------
    # Title relevance gets additional weight
    # --------------------------------------------------------

    for term in query_terms:

        if term in title:

            score += 3.0

    # --------------------------------------------------------
    # Negative signals
    # --------------------------------------------------------

    negative_matches = []

    for term in IRRELEVANT_TERMS:

        if term in document_text:

            negative_matches.append(
                term
            )

            score -= 3.0

    # --------------------------------------------------------
    # Query-specific evidence bonus
    # --------------------------------------------------------

    if (
        "hba1c" in query_text
        or "hemoglobin a1c" in query_text
        or "glycated hemoglobin" in query_text
    ):

        if (
            "hba1c" in document_text
            or "hemoglobin a1c" in document_text
            or "glycated hemoglobin" in document_text
        ):

            score += 4.0

    if (
        "fasting glucose" in query_text
        or "fasting plasma glucose" in query_text
    ):

        if (
            "fasting glucose" in document_text
            or "fasting plasma glucose" in document_text
            or "impaired fasting glucose" in document_text
        ):

            score += 4.0

    if (
        "family history" in query_text
    ):

        if "family history" in document_text:

            score += 3.0

    if (
        "physical activity" in query_text
    ):

        if (
            "physical activity" in document_text
            or "exercise" in document_text
            or "sedentary" in document_text
        ):

            score += 3.0

    if (
        "blood pressure" in query_text
        or "hypertension" in query_text
    ):

        if (
            "blood pressure" in document_text
            or "hypertension" in document_text
        ):

            score += 3.0

    if (
        "bmi" in query_text
        or "body mass index" in query_text
    ):

        if (
            "bmi" in document_text
            or "body mass index" in document_text
        ):

            score += 3.0

    return {
        "score": score,

        "matched_query_terms":
            matched_query_terms,

        "negative_matches":
            negative_matches,
    }


# ============================================================
# EVIDENCE QUALITY DECISION
# ============================================================

def is_relevant_evidence(
    query,
    result,
    minimum_score=3.0
):
    """
    Decide whether a retrieved passage contains enough
    lexical/clinical relevance to be passed downstream.

    This is a conservative heuristic.

    A result is accepted when:
      - it reaches the minimum relevance score, AND
      - it is not dominated by clearly unrelated terminology.
    """

    relevance = calculate_relevance_score(
        query,
        result
    )

    score = relevance["score"]

    negative_matches = relevance[
        "negative_matches"
    ]

    matched_terms = relevance[
        "matched_query_terms"
    ]

    # --------------------------------------------------------
    # Strong negative evidence
    # --------------------------------------------------------

    if (
        len(negative_matches) >= 2
        and len(matched_terms) == 0
    ):

        return False, relevance

    # --------------------------------------------------------
    # Minimum relevance
    # --------------------------------------------------------

    if score < minimum_score:

        return False, relevance

    return True, relevance


# ============================================================
# REMOVE DUPLICATE / NEAR-DUPLICATE ARTICLES
# ============================================================

def deduplicate_results(results):
    """
    Keep the strongest retrieved passage from each article.

    This prevents several chunks from the same article from
    occupying the entire evidence package.
    """

    article_groups = {}

    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )

        article_id = metadata.get(
            "article_id"
        )

        if not article_id:

            article_id = metadata.get(
                "pmid"
            )

        if not article_id:

            article_id = metadata.get(
                "doi"
            )

        if not article_id:

            # Last-resort unique key
            article_id = id(
                result
            )

        if article_id not in article_groups:

            article_groups[
                article_id
            ] = []

        article_groups[
            article_id
        ].append(
            result
        )

    selected = []

    for article_id, group in article_groups.items():

        # Sort using the existing retrieval score when
        # available. Lower distance is normally better.
        group = sorted(
            group,
            key=lambda item: (
                item.get(
                    "combined_score",
                    item.get(
                        "distance",
                        999999
                    )
                )
                if item.get(
                    "combined_score"
                ) is not None
                else item.get(
                    "distance",
                    999999
                )
            )
        )

        selected.append(
            group[0]
        )

    return selected


# ============================================================
# BUILD STRUCTURED EVIDENCE ITEM
# ============================================================

def build_evidence_item(
    result,
    evidence_number,
    relevance
):
    """
    Convert one retrieval result into the stable evidence
    structure used by the rest of the application.
    """

    metadata = result.get(
        "metadata",
        {}
    )

    return {
        "evidence_number":
            evidence_number,

        # ----------------------------------------------------
        # Source identification
        # ----------------------------------------------------

        "article_id":
            metadata.get(
                "article_id",
                ""
            ),

        "title":
            metadata.get(
                "title",
                ""
            ),

        "source":
            metadata.get(
                "source",
                ""
            ),

        "year":
            metadata.get(
                "year",
                ""
            ),

        "category":
            metadata.get(
                "category",
                ""
            ),

        # ----------------------------------------------------
        # Bibliographic identifiers
        # ----------------------------------------------------

        "pmid":
            metadata.get(
                "pmid",
                ""
            ),

        "doi":
            metadata.get(
                "doi",
                ""
            ),

        "pmc_id":
            metadata.get(
                "pmc_id",
                ""
            ),

        # ----------------------------------------------------
        # Evidence metadata
        # ----------------------------------------------------

        "section":
            metadata.get(
                "section",
                ""
            ),

        "distance":
            result.get(
                "distance"
            ),

        "lexical_score":
            result.get(
                "lexical_score",
                0.0
            ),

        "combined_score":
            result.get(
                "combined_score",
                result.get(
                    "distance"
                )
            ),

        # ----------------------------------------------------
        # New evidence-quality metadata
        # ----------------------------------------------------

        "relevance_score":
            relevance["score"],

        "matched_query_terms":
            relevance[
                "matched_query_terms"
            ],

        "negative_relevance_terms":
            relevance[
                "negative_matches"
            ],

        # ----------------------------------------------------
        # Retrieved evidence
        # ----------------------------------------------------

        "text":
            result.get(
                "document",
                ""
            ),
    }


# ============================================================
# BUILD EVIDENCE PACKAGE
# ============================================================

def build_evidence_package(
    query,
    top_k=3
):
    """
    Retrieve evidence and convert it into a structured
    evidence package for downstream LLM processing.

    Pipeline:

        retrieval
            ↓
        deduplication
            ↓
        relevance filtering
            ↓
        evidence packaging
            ↓
        LLM

    The original retrieval metadata and bibliographic
    identifiers are preserved.
    """

    if not query or not str(query).strip():

        return []

    # --------------------------------------------------------
    # Retrieve a larger candidate pool than the final
    # requested number.
    #
    # This allows the relevance filter to reject poor
    # passages while still returning enough evidence.
    # --------------------------------------------------------

    candidate_k = max(
        int(top_k) * 4,
        10
    )

    try:

        results = search_evidence(
            query,
            top_k=candidate_k
        )

    except Exception:

        return []

    if not results:

        return []

    # --------------------------------------------------------
    # Deduplicate by article
    # --------------------------------------------------------

    results = deduplicate_results(
        results
    )

    # --------------------------------------------------------
    # Relevance filtering
    # --------------------------------------------------------

    accepted = []

    for result in results:

        is_relevant, relevance = (
            is_relevant_evidence(
                query,
                result
            )
        )

        if not is_relevant:

            continue

        accepted.append(
            (
                result,
                relevance
            )
        )

    # --------------------------------------------------------
    # If the filter rejected everything, do not silently
    # invent evidence.
    # --------------------------------------------------------

    if not accepted:

        return []

    # --------------------------------------------------------
    # Rank accepted evidence by relevance.
    #
    # Higher relevance is better.
    # --------------------------------------------------------

    accepted = sorted(
        accepted,
        key=lambda pair:
            pair[1]["score"],
        reverse=True
    )

    # --------------------------------------------------------
    # Limit to requested top_k
    # --------------------------------------------------------

    accepted = accepted[
        :int(top_k)
    ]

    # --------------------------------------------------------
    # Build final evidence package
    # --------------------------------------------------------

    evidence = []

    for index, (
        result,
        relevance
    ) in enumerate(
        accepted,
        start=1
    ):

        evidence.append(
            build_evidence_item(
                result=result,
                evidence_number=index,
                relevance=relevance
            )
        )

    return evidence


# ============================================================
# DEBUG / INSPECTION
# ============================================================

def print_evidence_package(
    query,
    top_k=3
):
    """
    Print the structured evidence package for debugging
    and evaluation.
    """

    evidence = build_evidence_package(
        query,
        top_k=top_k
    )

    print()
    print(
        "=" * 70
    )
    print(
        "T2D-EviGuide Evidence Package"
    )
    print(
        "=" * 70
    )

    print()
    print(
        "Clinical Question:"
    )

    print(
        query
    )

    print()

    if not evidence:

        print(
            "No sufficiently relevant evidence retrieved."
        )

        return

    print(
        f"Evidence items: {len(evidence)}"
    )

    print()

    for item in evidence:

        print(
            "-" * 70
        )

        print(
            f"Evidence "
            f"{item['evidence_number']}"
        )

        print(
            "-" * 70
        )

        print(
            f"Article ID: "
            f"{item['article_id']}"
        )

        print(
            f"Title: "
            f"{item['title']}"
        )

        print(
            f"Source: "
            f"{item['source']}"
        )

        print(
            f"Year: "
            f"{item['year']}"
        )

        print(
            f"Category: "
            f"{item['category']}"
        )

        print(
            f"PMID: "
            f"{item['pmid']}"
        )

        print(
            f"DOI: "
            f"{item['doi']}"
        )

        print(
            f"PMC ID: "
            f"{item['pmc_id']}"
        )

        print(
            f"Evidence Type: "
            f"{item['section']}"
        )

        # ----------------------------------------------------
        # Retrieval scores
        # ----------------------------------------------------

        distance = item.get(
            "distance"
        )

        lexical_score = item.get(
            "lexical_score",
            0.0
        )

        combined_score = item.get(
            "combined_score"
        )

        relevance_score = item.get(
            "relevance_score",
            0.0
        )

        try:

            print(
                f"Semantic Distance: "
                f"{float(distance):.4f}"
            )

        except (
            TypeError,
            ValueError
        ):

            print(
                f"Semantic Distance: "
                f"{distance}"
            )

        try:

            print(
                f"Lexical Relevance: "
                f"{float(lexical_score):.4f}"
            )

        except (
            TypeError,
            ValueError
        ):

            print(
                f"Lexical Relevance: "
                f"{lexical_score}"
            )

        try:

            print(
                f"Combined Score: "
                f"{float(combined_score):.4f}"
            )

        except (
            TypeError,
            ValueError
        ):

            print(
                f"Combined Score: "
                f"{combined_score}"
            )

        print(
            f"Evidence Relevance Score: "
            f"{relevance_score:.2f}"
        )

        print()

        print(
            "Matched Query Terms:"
        )

        print(
            item[
                "matched_query_terms"
            ]
        )

        print()

        print(
            "Negative Relevance Terms:"
        )

        print(
            item[
                "negative_relevance_terms"
            ]
        )

        print()

        print(
            "Evidence Text:"
        )

        print(
            item[
                "text"
            ]
        )

        print()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    query = (
        "What are the diagnostic thresholds "
        "for fasting blood glucose and HbA1c "
        "for diabetes and prediabetes?"
    )

    print_evidence_package(
        query,
        top_k=3
    )