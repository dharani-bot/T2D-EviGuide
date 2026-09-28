import os
import re
import chromadb


# ============================================================
# CONFIGURATION
# ============================================================

VECTOR_DB_DIR = os.path.join(
    "data",
    "vector_db"
)

COLLECTION_NAME = "t2d_evidence"


# ============================================================
# QUERY TERM EXTRACTION
# ============================================================

def extract_query_terms(query):
    query = query.lower()

    terms = [
        "hba1c",
        "fasting",
        "glucose",
        "blood glucose",
        "prediabetes",
        "diabetes",
        "diagnosis",
        "diagnostic",
        "threshold",
        "thresholds",
        "cutoff",
        "cut-off",
        "criteria",
        "glycemic",
        "glycaemic",
        "risk",
        "screening",
        "obesity",
        "bmi",
        "lifestyle",
        "medication",
        "drug",
        "kidney",
        "ckd",
    ]

    return [term for term in terms if term in query]


# ============================================================
# LEXICAL RELEVANCE
# ============================================================

def lexical_relevance(document, query_terms):
    text = document.lower()

    score = 0.0

    for term in query_terms:

        # Exact phrase match
        if term in text:
            score += 1.0

        # Extra weight for important clinical concepts
        if term in {
            "hba1c",
            "glucose",
            "fasting",
            "prediabetes",
            "diabetes",
            "diagnostic",
            "threshold",
            "criteria",
            "screening",
        }:
            if term in text:
                score += 1.0

    # Bonus when diagnostic concepts occur with biomarkers
    has_biomarker = any(
        x in text
        for x in ["hba1c", "glucose", "fasting"]
    )

    has_diagnostic = any(
        x in text
        for x in [
            "diagnos",
            "threshold",
            "criteria",
            "prediabetes",
        ]
    )

    if has_biomarker and has_diagnostic:
        score += 2.0

    return score


# ============================================================
# SEARCH EVIDENCE
# ============================================================

def search_evidence(
    query,
    top_k=5,
    max_distance=1.15
):

    client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR
    )

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    # Retrieve stored documents and metadata.
    # No sentence-transformers, sklearn or scipy required.
    data = collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    documents = data.get("documents", [])
    metadatas = data.get("metadatas", [])

    if not documents:
        return []

    query_terms = extract_query_terms(query)

    candidates = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        if not document:
            continue

        score = lexical_relevance(
            document,
            query_terms
        )

        if score <= 0:
            continue

        candidates.append({
            "document": document,
            "metadata": metadata or {},
            "distance": max(
                0.0,
                1.0 - min(score / 10.0, 1.0)
            ),
            "lexical_score": score,
            "combined_score": -score,
        })

    # Highest lexical score first
    candidates.sort(
        key=lambda x: x["lexical_score"],
        reverse=True
    )

    # Prefer different articles
    selected = []
    seen_articles = set()

    for candidate in candidates:

        article_id = candidate["metadata"].get(
            "article_id",
            ""
        )

        if article_id in seen_articles:
            continue

        selected.append(candidate)
        seen_articles.add(article_id)

        if len(selected) >= top_k:
            break

    # Fill remaining slots if necessary
    if len(selected) < top_k:

        selected_ids = {
            id(x)
            for x in selected
        }

        for candidate in candidates:

            if id(candidate) in selected_ids:
                continue

            selected.append(candidate)

            if len(selected) >= top_k:
                break

    return selected


# ============================================================
# PRINT RESULTS
# ============================================================

def print_search_results(query, results):

    print()
    print("=" * 70)
    print("T2D-EviGuide Evidence Retrieval")
    print("=" * 70)

    print()
    print("Clinical Query:")
    print(query)

    print()

    if not results:
        print("No relevant evidence retrieved.")
        return

    print(
        f"Retrieved evidence chunks: {len(results)}"
    )

    for index, result in enumerate(results):

        metadata = result["metadata"]

        print()
        print("-" * 70)
        print(f"RESULT {index + 1}")
        print("-" * 70)

        print(
            f"Title: {metadata.get('title', '')}"
        )

        print(
            f"Article ID: "
            f"{metadata.get('article_id', '')}"
        )

        print(
            f"Source: {metadata.get('source', '')}"
        )

        print(
            f"Category: "
            f"{metadata.get('category', '')}"
        )

        print(
            f"Lexical Score: "
            f"{result['lexical_score']:.2f}"
        )

        print()
        print("Evidence:")
        print(result["document"])


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    query = (
        "What are the diagnostic thresholds "
        "for fasting blood glucose and HbA1c "
        "for diabetes and prediabetes?"
    )

    results = search_evidence(
        query,
        top_k=5
    )

    print_search_results(
        query,
        results
    )