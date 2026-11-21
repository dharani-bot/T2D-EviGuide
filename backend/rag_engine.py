import json
import os

import chromadb
from sentence_transformers import SentenceTransformer
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHUNKS_FILE = os.path.join(PROJECT_ROOT, "data", "chunks.json")

VECTOR_DB_DIR = os.path.join(PROJECT_ROOT, "data", "vector_db")

COLLECTION_NAME = "t2d_evidence"

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    MODEL_NAME
)

print("Embedding model loaded successfully.")


# ============================================================
# LOAD CHUNKS
# ============================================================

def load_chunks():

    if not os.path.exists(
        CHUNKS_FILE
    ):

        raise FileNotFoundError(
            f"Chunks file not found: "
            f"{CHUNKS_FILE}"
        )

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# BUILD VECTOR STORE
# ============================================================

def build_vector_store():

    print(
        "Loading embedding model..."
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "Loading chunks..."
    )

    chunks = load_chunks()

    if not chunks:

        raise ValueError(
            "No chunks found."
        )

    print(
        f"Chunks loaded: {len(chunks)}"
    )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    ids = [
        chunk["chunk_id"]
        for chunk in chunks
    ]

    metadatas = []

    for chunk in chunks:

        metadatas.append(
            {
                "article_id": chunk.get(
                    "article_id",
                    ""
                ),

                "title": chunk.get(
                    "title",
                    ""
                ),

                "source": chunk.get(
                    "source",
                    ""
                ),

                "year": chunk.get(
                    "year",
                    ""
                ),

                "category": chunk.get(
                    "category",
                    ""
                ),

                "pmid": chunk.get(
                    "pmid",
                    ""
                ),

                "doi": chunk.get(
                    "doi",
                    ""
                ),

                "pmc_id": chunk.get(
                    "pmc_id",
                    ""
                ),

                "section": chunk.get(
                    "section",
                    ""
                )
            }
        )

    print(
        "Creating document embeddings..."
    )

    embeddings = model.encode_document(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    os.makedirs(
        VECTOR_DB_DIR,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR
    )

    try:

        client.delete_collection(
            name=COLLECTION_NAME
        )

        print(
            "Previous vector collection removed."
        )

    except Exception:

        print(
            "No previous vector collection found."
        )

    collection = client.create_collection(
        name=COLLECTION_NAME,

        metadata={
            "description": (
                "Evidence collection for "
                "Type 2 Diabetes early risk "
                "assessment"
            )
        }
    )

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print()

    print(
        "===== Vector Store Summary ====="
    )

    print(
        f"Documents stored: "
        f"{collection.count()}"
    )

    print(
        f"Database location: "
        f"{VECTOR_DB_DIR}"
    )

    print(
        f"Collection name: "
        f"{COLLECTION_NAME}"
    )

    print()

    print(
        "Vector store created successfully."
    )


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

    client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR
    )

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    query_embedding = (
        embedding_model.encode_query(
            query,
            convert_to_numpy=True
        )
    )

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

    query_terms = extract_query_terms(
        query
    )
    try:
        query_language = detect(query)
    except Exception:
        query_language = None

    candidates = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        if not document:
            continue

        metadata = metadata or {}
        try:
            document_language = detect(document)
        except Exception:
            document_language = None

        lexical_score = lexical_relevance(
            document,
            query_terms
        )

        semantic_score = max(
            0.0,
            1.0 - float(distance)
        )

        combined_score = (
            semantic_score
            + (0.05 * lexical_score)
        )

        candidates.append(
            {
                "document": document,
                "metadata": metadata,
                "language": document_language,
                "distance": float(distance),
                "semantic_score": semantic_score,
                "lexical_score": lexical_score,
                "combined_score": combined_score,
            }
        )

    filtered_candidates = [
        candidate
        for candidate in candidates
        if candidate["distance"]
        <= max_distance
    ]

    if filtered_candidates:
        candidates = filtered_candidates

    if query_language:
        preferred_candidates = [
            candidate
            for candidate in candidates
            if candidate["language"] == query_language
        ]

        if len(preferred_candidates) >= top_k:
            candidates = preferred_candidates

    if query_language:
        candidates.sort(
            key=lambda x: (
                x["language"] == query_language,
                x["combined_score"]
            ),
            reverse=True
        )
    else:
        candidates.sort(
            key=lambda x: x["combined_score"],
            reverse=True
        )
    selected = []
    seen_articles = set()
    selected_ids = set()

    preferred_candidates = [
        candidate for candidate in candidates
        if candidate["language"] == query_language
    ]

    fallback_candidates = [
        candidate for candidate in candidates
        if candidate["language"] != query_language
    ]

    for candidate in preferred_candidates:
        article_id = candidate["metadata"].get("article_id", "")

        if article_id in seen_articles:
            continue

        selected.append(candidate)
        selected_ids.add(id(candidate))
        seen_articles.add(article_id)

        if len(selected) >= top_k:
            break

    if len(selected) < top_k:
        for candidate in preferred_candidates:
            if id(candidate) in selected_ids:
                continue

            selected.append(candidate)
            selected_ids.add(id(candidate))

            if len(selected) >= top_k:
                break

    if len(selected) < top_k:
        for candidate in fallback_candidates:
            if id(candidate) in selected_ids:
                continue

            selected.append(candidate)
            selected_ids.add(id(candidate))

            if len(selected) >= top_k:
                break

    return selected

    # --------------------------------------------------------
    # 3. Use other languages only as fallback
    # --------------------------------------------------------

    if len(selected) < top_k:

        for candidate in fallback_candidates:

            if id(candidate) in selected_ids:
                continue

            selected.append(candidate)
            selected_ids.add(id(candidate))

            if len(selected) >= top_k:
                break

    return selected


# ============================================================
# BUILD EVIDENCE PACKAGE
# ============================================================

def build_evidence_package(
    query,
    top_k=3
):

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

                "section": metadata.get(
                    "section",
                    ""
                ),
                "language": result.get(
                    "language",
                     "unknown"
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

                "text": result.get(
                    "document",
                    ""
                ),
            }
        )

    return evidence


# ============================================================
# PRINT SEARCH RESULTS
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


# ============================================================
# PRINT EVIDENCE PACKAGE
# ============================================================

def print_evidence_package(
    query
):

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
# MAIN TEST
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