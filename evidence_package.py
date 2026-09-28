from retrieval import search_evidence


def build_evidence_package(
    query,
    top_k=3
):
    """
    Retrieve evidence and convert it into a structured
    evidence package for downstream LLM processing.

    The package preserves source traceability, retrieval
    metadata, and evidence text.
    """

    results = search_evidence(
        query,
        top_k=top_k
    )

    evidence = []

    for index, result in enumerate(
        results
    ):

        metadata = result[
            "metadata"
        ]

        evidence.append(
            {
                "evidence_number": index + 1,

                # ------------------------------------------------
                # Source identification
                # ------------------------------------------------

                "article_id": metadata.get(
                    "article_id",
                    ""
                ),

                "title": metadata.get(
                    "title",
                    ""
                ),

                "source": metadata.get(
                    "source",
                    ""
                ),

                "year": metadata.get(
                    "year",
                    ""
                ),

                "category": metadata.get(
                    "category",
                    ""
                ),

                # ------------------------------------------------
                # Bibliographic identifiers
                # ------------------------------------------------

                "pmid": metadata.get(
                    "pmid",
                    ""
                ),

                "doi": metadata.get(
                    "doi",
                    ""
                ),

                "pmc_id": metadata.get(
                    "pmc_id",
                    ""
                ),

                # ------------------------------------------------
                # Evidence metadata
                # ------------------------------------------------

                "section": metadata.get(
                    "section",
                    ""
                ),

                "distance": result.get(
                    "distance"
                ),

                "lexical_score": result.get(
                    "lexical_score",
                    0.0
                ),

                "combined_score": result.get(
                    "combined_score",
                    result.get(
                        "distance"
                    )
                ),

                # ------------------------------------------------
                # Retrieved evidence
                # ------------------------------------------------

                "text": result.get(
                    "document",
                    ""
                ),
            }
        )

    return evidence


def print_evidence_package(
    query
):
    """
    Print the structured evidence package for debugging
    and evaluation.
    """

    evidence = build_evidence_package(
        query,
        top_k=3
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
            "No relevant evidence retrieved."
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
            f"Evidence {item['evidence_number']}"
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

        print(
            f"Semantic Distance: "
            f"{item['distance']:.4f}"
        )

        print(
            f"Lexical Relevance: "
            f"{item['lexical_score']:.4f}"
        )

        print(
            f"Combined Score: "
            f"{item['combined_score']:.4f}"
        )

        print()

        print(
            "Evidence Text:"
        )

        print(
            item["text"]
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
        query
    )