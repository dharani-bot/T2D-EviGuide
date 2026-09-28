import csv
import os
import time
import requests
import xml.etree.ElementTree as ET


# ============================================================
# API CONFIGURATION
# ============================================================

PUBMED_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ELINK_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"

PMC_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

REGISTRY_PATH = os.path.join(
    "data",
    "article_registry.csv"
)

OUTPUT_DIR = os.path.join(
    "data",
    "processed"
)


# ============================================================
# LOAD ARTICLE REGISTRY
# ============================================================

def load_article_registry():

    if not os.path.exists(REGISTRY_PATH):

        raise FileNotFoundError(
            f"Registry not found: {REGISTRY_PATH}"
        )

    with open(
        REGISTRY_PATH,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        return list(csv.DictReader(file))


# ============================================================
# FETCH PUBMED ARTICLE
# ============================================================

def fetch_pubmed_article(pmid):

    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml"
    }

    response = requests.get(
        PUBMED_API,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# FIND PMC ID
# ============================================================

def find_pmc_id(pmid):

    params = {
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": pmid,
        "retmode": "xml"
    }

    response = requests.get(
        ELINK_API,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    root = ET.fromstring(
        response.text
    )

    pmc_ids = []

    for element in root.findall(
        ".//Link/Id"
    ):

        if element.text:

            pmc_ids.append(
                element.text.strip()
            )

    if pmc_ids:

        return pmc_ids[0]

    return None


# ============================================================
# FETCH PMC ARTICLE
# ============================================================

def fetch_pmc_article(pmc_id):

    params = {
        "db": "pmc",
        "id": pmc_id,
        "retmode": "xml"
    }

    response = requests.get(
        PMC_API,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# EXTRACT PUBMED CONTENT
# ============================================================

def extract_pubmed_content(xml_text):

    root = ET.fromstring(
        xml_text
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title_element = root.find(
        ".//ArticleTitle"
    )

    title = ""

    if title_element is not None:

        title = "".join(
            title_element.itertext()
        ).strip()

    # --------------------------------------------------------
    # Abstract
    # --------------------------------------------------------

    abstract_parts = []

    for abstract_text in root.findall(
        ".//AbstractText"
    ):

        text = "".join(
            abstract_text.itertext()
        ).strip()

        if not text:
            continue

        label = abstract_text.attrib.get(
            "Label"
        )

        if label:

            abstract_parts.append(
                f"{label}: {text}"
            )

        else:

            abstract_parts.append(
                text
            )

    abstract = "\n\n".join(
        abstract_parts
    )

    return {
        "title": title,
        "abstract": abstract
    }


# ============================================================
# EXTRACT PMC FULL TEXT
# ============================================================

def extract_pmc_full_text(xml_text):

    root = ET.fromstring(
        xml_text
    )

    sections = []

    # --------------------------------------------------------
    # Main article body
    # --------------------------------------------------------

    for section in root.findall(
        ".//body//sec"
    ):

        title_element = section.find(
            "./title"
        )

        section_title = ""

        if title_element is not None:

            section_title = "".join(
                title_element.itertext()
            ).strip()

        paragraphs = []

        for paragraph in section.findall(
            ".//p"
        ):

            paragraph_text = "".join(
                paragraph.itertext()
            ).strip()

            if paragraph_text:

                paragraphs.append(
                    paragraph_text
                )

        if not paragraphs:
            continue

        section_text = "\n\n".join(
            paragraphs
        )

        if section_title:

            sections.append(
                f"{section_title}\n"
                f"{section_text}"
            )

        else:

            sections.append(
                section_text
            )

    return "\n\n".join(
        sections
    )


# ============================================================
# SAVE ARTICLE
# ============================================================

def save_article(
    article,
    article_text,
    pmc_id=None,
    full_text=None
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    article_id = article[
        "article_id"
    ]

    output_path = os.path.join(
        OUTPUT_DIR,
        f"{article_id}.txt"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "TITLE\n"
        )

        file.write(
            f"{article_text['title']}\n\n"
        )

        file.write(
            "SOURCE\n"
        )

        file.write(
            f"{article['source']}\n\n"
        )

        file.write(
            "YEAR\n"
        )

        file.write(
            f"{article['year']}\n\n"
        )

        file.write(
            "CATEGORY\n"
        )

        file.write(
            f"{article['category']}\n\n"
        )

        file.write(
            "PMID\n"
        )

        file.write(
            f"{article['pmid']}\n\n"
        )

        file.write(
            "DOI\n"
        )

        file.write(
            f"{article['doi']}\n\n"
        )

        file.write(
            "PMC_ID\n"
        )

        file.write(
            f"{pmc_id or ''}\n\n"
        )

        file.write(
            "ABSTRACT\n"
        )

        file.write(
            f"{article_text['abstract']}\n\n"
        )

        # ----------------------------------------------------
        # Full text
        # ----------------------------------------------------

        if full_text:

            file.write(
                "FULL_TEXT\n"
            )

            file.write(
                f"{full_text}\n"
            )


    return output_path


# ============================================================
# BUILD LITERATURE COLLECTION
# ============================================================

def build_literature_collection():

    articles = load_article_registry()

    print(
        f"Found {len(articles)} articles in registry."
    )

    successful = 0
    skipped = 0
    failed = 0
    full_text_count = 0
    abstract_only_count = 0

    for article in articles:

        article_id = article[
            "article_id"
        ]

        pmid = article.get(
            "pmid",
            ""
        ).strip()

        # ----------------------------------------------------
        # Check PMID
        # ----------------------------------------------------

        if not pmid:

            print(
                f"Skipping {article_id}: "
                f"no PMID available."
            )

            skipped += 1

            continue

        print()
        print(
            f"Retrieving PMID {pmid}..."
        )

        try:

            # ------------------------------------------------
            # PubMed
            # ------------------------------------------------

            pubmed_xml = fetch_pubmed_article(
                pmid
            )

            article_text = extract_pubmed_content(
                pubmed_xml
            )

            # ------------------------------------------------
            # Try to find PMC record
            # ------------------------------------------------

            pmc_id = find_pmc_id(
                pmid
            )

            full_text = ""

            if pmc_id:

                print(
                    f"  PMC record found: PMC{pmc_id}"
                )

                try:

                    pmc_xml = fetch_pmc_article(
                        pmc_id
                    )

                    full_text = extract_pmc_full_text(
                        pmc_xml
                    )

                    if full_text:

                        print(
                            "  Full-text content retrieved."
                        )

                        full_text_count += 1

                    else:

                        print(
                            "  PMC record found, "
                            "but no article body was extracted."
                        )

                        abstract_only_count += 1

                except Exception as pmc_error:

                    print(
                        f"  PMC retrieval failed: "
                        f"{pmc_error}"
                    )

                    abstract_only_count += 1

            else:

                print(
                    "  No PMC full-text record found."
                )

                abstract_only_count += 1

            # ------------------------------------------------
            # Save
            # ------------------------------------------------

            output_path = save_article(
                article,
                article_text,
                pmc_id=pmc_id,
                full_text=full_text
            )

            print(
                f"  Saved: {output_path}"
            )

            successful += 1

        except Exception as error:

            print(
                f"  Error retrieving PMID {pmid}: "
                f"{error}"
            )

            failed += 1

        # ----------------------------------------------------
        # API delay
        # ----------------------------------------------------

        time.sleep(0.5)

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print(
        "===== Literature Collection Summary ====="
    )

    print(
        f"Successful:          {successful}"
    )

    print(
        f"Skipped:             {skipped}"
    )

    print(
        f"Failed:              {failed}"
    )

    print(
        f"Full-text sources:   {full_text_count}"
    )

    print(
        f"Abstract-only:       {abstract_only_count}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    build_literature_collection()