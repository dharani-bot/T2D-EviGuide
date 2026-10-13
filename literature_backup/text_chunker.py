import json
import os
import re


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIR = os.path.join(
    "data",
    "cleaned"
)

OUTPUT_FILE = os.path.join(
    "data",
    "chunks.json"
)


# ============================================================
# METADATA EXTRACTION
# ============================================================

def extract_metadata(text):

    metadata = {}

    fields = [
        "TITLE",
        "SOURCE",
        "YEAR",
        "CATEGORY",
        "PMID",
        "DOI",
        "PMC_ID"
    ]

    for index, field in enumerate(fields):

        if index + 1 < len(fields):

            next_field = fields[index + 1]

            pattern = (
                rf"{re.escape(field)}\s*\n"
                rf"(.*?)(?=\n\n"
                rf"{re.escape(next_field)}\s*\n)"
            )

        else:

            pattern = (
                rf"{re.escape(field)}\s*\n"
                rf"(.*?)(?=\n\n"
                rf"ABSTRACT\s*\n|\Z)"
            )

        match = re.search(
            pattern,
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        if match:

            metadata[field.lower()] = (
                match.group(1).strip()
            )

        else:

            metadata[field.lower()] = ""

    return metadata


# ============================================================
# SECTION EXTRACTION
# ============================================================

def extract_section(
    text,
    section_name,
    next_sections=None
):

    if next_sections:

        next_pattern = "|".join(
            re.escape(section)
            for section in next_sections
        )

        pattern = (
            rf"{re.escape(section_name)}\s*\n"
            rf"(.*?)(?=\n\n"
            rf"(?:{next_pattern})\s*\n|\Z)"
        )

    else:

        pattern = (
            rf"{re.escape(section_name)}\s*\n"
            rf"(.*)"
        )

    match = re.search(
        pattern,
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    if match:

        return match.group(1).strip()

    return ""


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SPLIT INTO PARAGRAPHS
# ============================================================

def split_into_paragraphs(text):

    # Normalize line endings
    text = re.sub(
        r"\r\n?",
        "\n",
        text
    )

    # Remove excessive spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Preserve paragraph boundaries
    paragraphs = re.split(
        r"\n\s*\n",
        text
    )

    cleaned = []

    for paragraph in paragraphs:

        paragraph = normalize_text(
            paragraph
        )

        if paragraph:

            cleaned.append(
                paragraph
            )

    return cleaned


# ============================================================
# PARAGRAPH-AWARE CHUNKING
# ============================================================

def split_into_chunks(
    text,
    target_size=900,
    overlap_paragraphs=1
):
    """
    Create chunks using paragraph boundaries.

    This avoids cutting clinical statements in the middle
    whenever possible.
    """

    paragraphs = split_into_paragraphs(
        text
    )

    if not paragraphs:

        return []

    chunks = []

    current_paragraphs = []
    current_length = 0

    for paragraph in paragraphs:

        paragraph_length = len(
            paragraph
        )

        # ----------------------------------------------------
        # If adding this paragraph would make the chunk
        # substantially larger than target size, save the
        # current chunk first.
        # ----------------------------------------------------

        if (
            current_paragraphs
            and current_length + paragraph_length
            > target_size
        ):

            chunk = " ".join(
                current_paragraphs
            ).strip()

            if chunk:

                chunks.append(
                    chunk
                )

            # ------------------------------------------------
            # Keep a small paragraph overlap for context.
            # ------------------------------------------------

            if overlap_paragraphs > 0:

                current_paragraphs = (
                    current_paragraphs[
                        -overlap_paragraphs:
                    ]
                )

                current_length = sum(
                    len(p)
                    for p in current_paragraphs
                )

            else:

                current_paragraphs = []

                current_length = 0

        current_paragraphs.append(
            paragraph
        )

        current_length += (
            paragraph_length + 1
        )

    # --------------------------------------------------------
    # Save final chunk
    # --------------------------------------------------------

    if current_paragraphs:

        chunk = " ".join(
            current_paragraphs
        ).strip()

        if chunk:

            chunks.append(
                chunk
            )

    return chunks


# ============================================================
# PROCESS ARTICLE
# ============================================================

def process_article(file_name):

    file_path = os.path.join(
        INPUT_DIR,
        file_name
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    metadata = extract_metadata(
        text
    )

    article_id = os.path.splitext(
        file_name
    )[0]

    # --------------------------------------------------------
    # Extract full text
    # --------------------------------------------------------

    full_text = extract_section(
        text,
        "FULL_TEXT"
    )

    # --------------------------------------------------------
    # Extract abstract
    # --------------------------------------------------------

    abstract = extract_section(
        text,
        "ABSTRACT",
        ["FULL_TEXT"]
    )

    # --------------------------------------------------------
    # Prefer full text when available
    # --------------------------------------------------------

    if full_text:

        content = full_text

        content_type = "full_text"

    elif abstract:

        content = abstract

        content_type = "abstract"

    else:

        return []

    # --------------------------------------------------------
    # Create paragraph-aware chunks
    # --------------------------------------------------------

    chunks = split_into_chunks(
        content,
        target_size=900,
        overlap_paragraphs=1
    )

    records = []

    for index, chunk in enumerate(
        chunks
    ):

        records.append(
            {
                "chunk_id": (
                    f"{article_id}_"
                    f"chunk_{index + 1}"
                ),

                "article_id": article_id,

                "title": metadata[
                    "title"
                ],

                "source": metadata[
                    "source"
                ],

                "year": metadata[
                    "year"
                ],

                "category": metadata[
                    "category"
                ],

                "pmid": metadata[
                    "pmid"
                ],

                "doi": metadata[
                    "doi"
                ],

                "pmc_id": metadata[
                    "pmc_id"
                ],

                "section": content_type,

                "text": chunk
            }
        )

    return records


# ============================================================
# BUILD ALL CHUNKS
# ============================================================

def build_chunks():

    if not os.path.exists(
        INPUT_DIR
    ):

        raise FileNotFoundError(
            f"Input directory not found: "
            f"{INPUT_DIR}"
        )

    files = sorted(
        file_name
        for file_name in os.listdir(
            INPUT_DIR
        )
        if file_name.endswith(".txt")
    )

    print(
        f"Found {len(files)} cleaned literature files."
    )

    all_chunks = []

    full_text_sources = 0
    abstract_sources = 0
    empty_sources = 0

    for file_name in files:

        records = process_article(
            file_name
        )

        if records:

            section_types = {
                record["section"]
                for record in records
            }

            if "full_text" in section_types:

                full_text_sources += 1

            elif "abstract" in section_types:

                abstract_sources += 1

        else:

            empty_sources += 1

        print(
            f"{file_name}: "
            f"{len(records)} chunks"
        )

        all_chunks.extend(
            records
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print(
        "===== Chunking Summary ====="
    )

    print(
        f"Articles processed: "
        f"{len(files)}"
    )

    print(
        f"Full-text sources:   "
        f"{full_text_sources}"
    )

    print(
        f"Abstract-only:       "
        f"{abstract_sources}"
    )

    print(
        f"Empty sources:       "
        f"{empty_sources}"
    )

    print(
        f"Total chunks:        "
        f"{len(all_chunks)}"
    )

    print(
        f"Saved to: "
        f"{OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    build_chunks()