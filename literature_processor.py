import os
import re


# ============================================================
# DIRECTORIES
# ============================================================

INPUT_DIR = os.path.join(
    "data",
    "processed"
)

OUTPUT_DIR = os.path.join(
    "data",
    "cleaned"
)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    Clean extracted literature text while preserving
    paragraph structure.
    """

    # Normalize line endings
    text = re.sub(
        r"\r\n?",
        "\n",
        text
    )

    # Remove excessive spaces/tabs
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# PROCESS ARTICLE
# ============================================================

def process_article(file_name):

    input_path = os.path.join(
        INPUT_DIR,
        file_name
    )

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    cleaned_text = clean_text(
        text
    )

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        file_name
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            cleaned_text
        )

    return output_path


# ============================================================
# PROCESS ALL ARTICLES
# ============================================================

def process_all_articles():

    if not os.path.exists(
        INPUT_DIR
    ):

        print(
            f"Input directory not found: "
            f"{INPUT_DIR}"
        )

        return

    files = sorted(
        file_name
        for file_name in os.listdir(
            INPUT_DIR
        )
        if file_name.endswith(".txt")
    )

    print(
        f"Found {len(files)} literature files."
    )

    for file_name in files:

        print(
            f"Processing {file_name}..."
        )

        output_path = process_article(
            file_name
        )

        print(
            f"Saved cleaned file: "
            f"{output_path}"
        )

    print()
    print(
        "Literature processing complete."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    process_all_articles()