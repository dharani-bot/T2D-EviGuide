import json
import os

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

CHUNKS_FILE = os.path.join(
    "data",
    "chunks.json"
)

VECTOR_DB_DIR = os.path.join(
    "data",
    "vector_db"
)

COLLECTION_NAME = "t2d_evidence"

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


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

    # --------------------------------------------------------
    # Prepare data
    # --------------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    ids = [
        chunk["chunk_id"]
        for chunk in chunks
    ]

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Create embeddings
    # --------------------------------------------------------

    print(
        "Creating document embeddings..."
    )

    embeddings = model.encode_document(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    # --------------------------------------------------------
    # Create database directory
    # --------------------------------------------------------

    os.makedirs(
        VECTOR_DB_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Connect to Chroma
    # --------------------------------------------------------

    client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR
    )

    # --------------------------------------------------------
    # Delete old collection
    #
    # This is important because the previous collection
    # contained older chunks.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Create fresh collection
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Store embeddings
    # --------------------------------------------------------

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

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
# MAIN
# ============================================================

if __name__ == "__main__":

    build_vector_store()