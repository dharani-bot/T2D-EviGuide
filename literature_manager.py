import csv
import os
import time
import re
import requests
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher


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
        "id": str(pmid),
        "linkname": "pubmed_pmc",
        "retmode": "xml"
    }

    response = requests.get(
        ELINK_API,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    root = ET.fromstring(response.text)

    pmc_ids = []

    for linkset in root.findall(".//LinkSetDb"):

        link_name = linkset.findtext("LinkName")

        if link_name != "pubmed_pmc":
            continue

        for element in linkset.findall("./Link/Id"):

            if element.text:
                pmc_ids.append(element.text.strip())

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

    root = ET.fromstring(xml_text)

    title_element = root.find(".//ArticleTitle")
    title = "".join(title_element.itertext()).strip() if title_element is not None else ""

    abstract_parts = []

    for element in root.findall(".//AbstractText"):
        text = "".join(element.itertext()).strip()

        if text:
            label = element.attrib.get("Label")
            abstract_parts.append(f"{label}: {text}" if label else text)

    abstract = "\n\n".join(abstract_parts)

    pmid_element = root.find(".//PMID")
    pmid = pmid_element.text.strip() if pmid_element is not None and pmid_element.text else ""

    doi_element = root.find(".//ArticleId[@IdType='doi']")

    if doi_element is None:
        doi_element = root.find(".//ELocationID[@EIdType='doi']")

    doi = "".join(doi_element.itertext()).strip() if doi_element is not None else ""

    return {
        "title": title,
        "abstract": abstract,
        "pmid": pmid,
        "doi": doi
    }


# EXTRACT PMC FULL TEXT
# ============================================================
# ============================================================
# EXTRACT PMC ARTICLE METADATA
# ============================================================

def extract_pmc_metadata(xml_text):

    root = ET.fromstring(xml_text)

    pmid = ""
    doi = ""
    title = ""

    for element in root.findall(".//article-meta/article-id"):

        id_type = element.attrib.get("pub-id-type", "").lower()
        value = "".join(element.itertext()).strip()

        if id_type == "pmid":
            pmid = value

        elif id_type == "doi":
            doi = value

    title_element = root.find(
        ".//article-meta/title-group/article-title"
    )

    if title_element is not None:
        title = "".join(title_element.itertext()).strip()

    return {
        "pmid": pmid,
        "doi": doi,
        "title": title
    }


# ============================================================
# VERIFY PMC ARTICLE IDENTITY
# ============================================================

def verify_pmc_identity(article, pmc_metadata):

    expected_pmid = str(article.get("pmid", "")).strip()
    actual_pmid = str(pmc_metadata.get("pmid", "")).strip()

    if not expected_pmid or not actual_pmid:
        return False, "PMID missing"

    if expected_pmid != actual_pmid:
        return False, "PMID mismatch"

    expected_doi = str(article.get("doi", "")).strip().lower()
    actual_doi = str(pmc_metadata.get("doi", "")).strip().lower()

    expected_doi = re.sub(
        r"^https?://(dx\\.)?doi\\.org/",
        "",
        expected_doi
    )

    actual_doi = re.sub(
        r"^https?://(dx\\.)?doi\\.org/",
        "",
        actual_doi
    )

    if expected_doi and actual_doi:
        if expected_doi != actual_doi:
            return False, "DOI mismatch"

    expected_title = str(article.get("title", "")).strip()
    actual_title = str(pmc_metadata.get("title", "")).strip()

    normalize = lambda value: re.sub(
        r"[^a-z0-9]+",
        "",
        value.lower()
    )

    expected_normalized = normalize(expected_title)
    actual_normalized = normalize(actual_title)

    if not expected_normalized or not actual_normalized:
        return False, "Article title missing"

    similarity = SequenceMatcher(
        None,
        expected_normalized,
        actual_normalized
    ).ratio()

    if similarity < 0.90:
        return False, f"Title mismatch (similarity: {similarity:.2f})"

    return True, "PMID, DOI and title verification passed"


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
            # VERIFY PUBMED ARTICLE IDENTITY
            # ------------------------------------------------

            returned_pmid = str(
                article_text.get("pmid", "")
            ).strip()

            if returned_pmid != pmid:
                print("  PubMed PMID mismatch. Article rejected.")
                failed += 1
                continue

            expected_doi = str(
                article.get("doi", "")
            ).strip().lower()

            returned_doi = str(
                article_text.get("doi", "")
            ).strip().lower()

            expected_doi = re.sub(
                r"^https?://(dx\.)?doi\.org/",
                "",
                expected_doi
            )

            returned_doi = re.sub(
                r"^https?://(dx\.)?doi\.org/",
                "",
                returned_doi
            )

            if (
                expected_doi
                and returned_doi
                and expected_doi != returned_doi
            ):
                print("  PubMed DOI mismatch. Article rejected.")
                failed += 1
                continue

            expected_title = str(
                article.get("title", "")
            ).strip()

            returned_title = str(
                article_text.get("title", "")
            ).strip()

            normalize_title = lambda value: re.sub(
                r"[^a-z0-9]+",
                "",
                value.lower()
            )

            title_similarity = SequenceMatcher(
                None,
                normalize_title(expected_title),
                normalize_title(returned_title)
            ).ratio()

            if (
                not expected_title
                or not returned_title
                or title_similarity < 0.90
            ):
                print(
                    f"  PubMed title mismatch "
                    f"(similarity: {title_similarity:.2f}). "
                    "Article rejected."
                )
                failed += 1
                continue

            print(
                "  PubMed identity verified: "
                "PMID, DOI and title checks passed."
            )

            # ------------------------------------------------
            # Try to find and verify PMC record
            # ------------------------------------------------

            pmc_id = find_pmc_id(pmid)

            full_text = ""

            if pmc_id:

                print(f"  PMC record found: PMC{pmc_id}")

                try:

                    pmc_xml = fetch_pmc_article(pmc_id)

                    # Extract PMC identity metadata
                    pmc_metadata = extract_pmc_metadata(
                        pmc_xml
                    )

                    # Verify against registered article
                    is_verified, verification_message = verify_pmc_identity(
                        article,
                        pmc_metadata
                    )

                    print(
                        f"  PMC identity check: {verification_message}"
                    )

                    if is_verified:

                        full_text = extract_pmc_full_text(
                            pmc_xml
                        )

                        if full_text:

                            print(
                                "  Verified full-text content retrieved."
                            )

                            full_text_count += 1

                        else:

                            print(
                                "  Verified PMC record, "
                                "but no article body was extracted."
                            )

                            abstract_only_count += 1

                    else:

                        print(
                            "  PMC identity verification failed. "
                            "Full text rejected."
                        )

                        pmc_id = None
                        abstract_only_count += 1

                except Exception as pmc_error:

                    print(
                        f"  PMC retrieval or verification failed: "
                        f"{pmc_error}"
                    )

                    pmc_id = None
                    full_text = ""
                    abstract_only_count += 1

            else:

                print(
                    "  No PMC full-text record found."
                )

                abstract_only_count += 1
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


