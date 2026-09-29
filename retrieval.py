import os
import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

VECTOR_DB_DIR = os.path.join(
    "data",
    "vector_db"
)

COLLECTION_NAME = "t2d_evidence"

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    MODEL_NAME
)

print("Embedding model loaded successfully.")


# ============================================================
# CLINICAL QUERY TERM EXTRACTION
# ============================================================

def extract_query_terms(query):

    query = query.lower()

    terms = [
        "hba1c",
        "fasting glucose",
        "glucose",
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
        "body weight",
        "physical activity",
        "lifestyle",
        "family history",
        "hypertension",
        "blood pressure",
        "medication",
        "drug interaction",
        "drug",
        "kidney",
        "ckd",
        "biomarker",
        "biomarkers",
        "insulin resistance",
        "beta cell",
        "c-peptide",
        "fasting insulin",
        "homa-ir",
        "lipid",
        "cholesterol",
    ]

    return [
        term
        for term in terms
        if term in query
    ]


# ============================================================
# LEXICAL RELEVANCE
# ============================================================

def lexical_relevance(
    document,
    query_terms
):

    text = document.lower()

    score = 0.0

    for term in query_terms:

        if term in text:

            score += 1.0

            if term in {
                "hba1c",
                "fasting glucose",
                "glucose",
                "prediabetes",
                "diabetes",
                "diagnostic",
                "threshold",
                "criteria",
                "screening",
                "biomarker",
                "biomarkers",
            }:

                score += 1.0

    return score


# ============================================================
# SEARCH EVIDENCE
# ============================================================

def search_evidence(
    query,
    top_k=5,
    candidate_k=20,
    max_distance=1.20
):

    # --------------------------------------------------------
    # Connect to ChromaDB
    # --------------------------------------------------------

    client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR
    )

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    # --------------------------------------------------------
    # Create query embedding
    # --------------------------------------------------------

    query_embedding = (
        embedding_model.encode_query(
            query,
            convert_to_numpy=True
        )
    )

    # --------------------------------------------------------
    # Semantic vector search
    # --------------------------------------------------------

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=candidate_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    if not documents:
        return []

    # --------------------------------------------------------
    # Extract important terms from query
    # --------------------------------------------------------

    query_terms = extract_query_terms(
        query
    )

    candidates = []

    # --------------------------------------------------------
    # Combine semantic + lexical relevance
    # --------------------------------------------------------

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        if not document:
            continue

        metadata = metadata or {}

        lexical_score = lexical_relevance(
            document,
            query_terms
        )

        # Convert semantic distance into a similarity-like
        # score where higher is better.
        semantic_score = max(
            0.0,
            1.0 - float(distance)
        )

        # Small lexical boost helps prioritize documents
        # containing important clinical concepts.
        combined_score = (
            semantic_score
            + (0.05 * lexical_score)
        )

        candidates.append(
            {
                "document": document,

                "metadata": metadata,

                "distance": float(
                    distance
                ),

                "semantic_score": (
                    semantic_score
                ),

                "lexical_score": (
                    lexical_score
                ),

                "combined_score": (
                    combined_score
                ),
            }
        )

    # --------------------------------------------------------
    # Remove very distant results
    # --------------------------------------------------------

    filtered_candidates = [
        candidate
        for candidate in candidates
        if candidate["distance"]
        <= max_distance
    ]

    # If filtering removes everything, keep the semantic
    # candidates rather than returning no evidence.
    if filtered_candidates:

        candidates = filtered_candidates

    # --------------------------------------------------------
    # Highest combined relevance first
    # --------------------------------------------------------

    candidates.sort(
        key=lambda x: x["combined_score"],
        reverse=True
    )

    # --------------------------------------------------------
    # Prefer different articles
    # --------------------------------------------------------

    selected = []

    seen_articles = set()

    for candidate in candidates:

        article_id = candidate[
            "metadata"
        ].get(
            "article_id",
            ""
        )

        if article_id in seen_articles:
            continue

        selected.append(
            candidate
        )

        seen_articles.add(
            article_id
        )

        if len(selected) >= top_k:
            break

    # --------------------------------------------------------
    # Fill remaining slots if needed
    # --------------------------------------------------------

    if len(selected) < top_k:

        selected_ids = {
            id(candidate)
            for candidate in selected
        }

        for candidate in candidates:

            if id(candidate) in selected_ids:
                continue

            selected.append(
                candidate
            )

            if len(selected) >= top_k:
                break

    return selected


# ============================================================
# PRINT RESULTS
# ============================================================

def print_search_results(
    query,
    results
):

    print()

    print(
        "=" * 70
    )

    print(
        "T2D-EviGuide Semantic Evidence Retrieval"
    )

    print(
        "=" * 70
    )

    print()

    print(
        "Clinical Query:"
    )

    print(
        query
    )

    print()

    if not results:

        print(
            "No relevant evidence retrieved."
        )

        return

    print(
        f"Retrieved evidence chunks: "
        f"{len(results)}"
    )

    for index, result in enumerate(
        results
    ):

        metadata = result[
            "metadata"
        ]

        print()

        print(
            "-" * 70
        )

        print(
            f"RESULT {index + 1}"
        )

        print(
            "-" * 70
        )

        print(
            f"Title: "
            f"{metadata.get('title', '')}"
        )

        print(
            f"Article ID: "
            f"{metadata.get('article_id', '')}"
        )

        print(
            f"Source: "
            f"{metadata.get('source', '')}"
        )

        print(
            f"Category: "
            f"{metadata.get('category', '')}"
        )

        print(
            f"Semantic Distance: "
            f"{result['distance']:.4f}"
        )

        print(
            f"Semantic Score: "
            f"{result['semantic_score']:.4f}"
        )

        print(
            f"Lexical Score: "
            f"{result['lexical_score']:.2f}"
        )

        print(
            f"Combined Score: "
            f"{result['combined_score']:.4f}"
        )

        print()

        print(
            "Evidence:"
        )

        print(
            result["document"]
        )


# TEST
#sonu
