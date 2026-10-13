import requests
import xml.etree.ElementTree as ET
import csv
from pathlib import Path
from datetime import datetime


# ============================================================
# Configuration
# ============================================================

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "pubmed_literature.csv"


# ============================================================
# Type 2 Diabetes search topics
# ============================================================

SEARCH_QUERIES = {
    "risk_factors": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND (risk factors OR risk assessment OR risk prediction)'
    ),

    "prediabetes": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND (prediabetes OR impaired glucose)'
    ),

    "screening": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND (screening OR early detection)'
    ),

    "hba1c": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND (HbA1c OR glycated hemoglobin)'
    ),

    "glucose": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND (blood glucose OR plasma glucose)'
    ),

    "obesity": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND (obesity OR overweight)'
    ),

    "lifestyle": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND (physical activity OR diet OR lifestyle)'
    ),

    "prevention": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND prevention'
    ),

    "clinical_guidelines": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND (guideline OR consensus OR standards)'
    ),

    "medications": (
        '"Type 2 Diabetes Mellitus"[Title/Abstract] '
        'AND (medication OR pharmacotherapy OR treatment)'
    ),
}


# ============================================================
# Search PubMed
# ============================================================

def search_pubmed(query, max_results=20, years=5):

    current_year = datetime.now().year
    start_year = current_year - years

    dated_query = (
        f"({query}) AND "
        f'("{start_year}"[Date - Publication] : '
        f'"{current_year}"[Date - Publication])'
    )

    params = {
        "db": "pubmed",
        "term": dated_query,
        "retmode": "xml",
        "retmax": max_results,
        "sort": "date",
    }

    response = requests.get(
        f"{BASE_URL}/esearch.fcgi",
        params=params,
        timeout=30
    )

    response.raise_for_status()

    root = ET.fromstring(response.text)

    return [
        element.text
        for element in root.findall(".//Id")
        if element.text
    ]


# ============================================================
# Fetch PubMed records
# ============================================================

def fetch_pubmed_records(pmids):

    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    }

    response = requests.get(
        f"{BASE_URL}/efetch.fcgi",
        params=params,
        timeout=60
    )

    response.raise_for_status()

    root = ET.fromstring(response.text)

    records = []

    for article in root.findall(".//PubmedArticle"):

        pmid_element = article.find(".//PMID")

        if pmid_element is None:
            continue

        pmid = pmid_element.text

        title_element = article.find(".//ArticleTitle")

        title = (
            "".join(title_element.itertext())
            if title_element is not None
            else ""
        )

        abstract_parts = []

        for abstract in article.findall(".//AbstractText"):

            text = "".join(abstract.itertext())

            label = abstract.attrib.get("Label")

            if label:
                text = f"{label}: {text}"

            abstract_parts.append(text)

        abstract = " ".join(abstract_parts)

        journal_element = article.find(".//Journal/Title")

        journal = (
            journal_element.text
            if journal_element is not None
            else ""
        )

        year = ""

        pub_date = article.find(".//PubDate")

        if pub_date is not None:

            year_element = pub_date.find("Year")

            if year_element is not None:
                year = year_element.text

            else:

                medline_date = pub_date.find("MedlineDate")

                if medline_date is not None:
                    year = medline_date.text[:4]

        doi = ""
        pmcid = ""

        for article_id in article.findall(".//ArticleId"):

            id_type = article_id.attrib.get("IdType")

            if id_type == "doi":
                doi = article_id.text

            elif id_type == "pmc":
                pmcid = article_id.text

        records.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "year": year,
            "doi": doi,
            "pmcid": pmcid,
        })

    return records


# ============================================================
# Main collection process
# ============================================================

def collect_literature():

    all_records = []

    print()
    print("=" * 60)
    print(" T2D-EviGuide Automated PubMed Literature Collection")
    print("=" * 60)
    print()

    for topic, query in SEARCH_QUERIES.items():

        print(f"Searching topic: {topic}")

        try:

            pmids = search_pubmed(
                query,
                max_results=20,
                years=5
            )

            print(f"  Articles found: {len(pmids)}")

            records = fetch_pubmed_records(pmids)

            for record in records:

                record["topic"] = topic
                record["source"] = "PubMed"

            all_records.extend(records)

        except Exception as error:

            print(f"  ERROR: {error}")

    # ========================================================
    # Deduplicate
    # ========================================================

    unique_records = {}

    for record in all_records:

        if record["pmid"]:
            key = "PMID:" + record["pmid"]

        elif record["doi"]:
            key = "DOI:" + record["doi"].lower()

        else:
            key = "TITLE:" + record["title"].strip().lower()

        unique_records[key] = record

    records = list(unique_records.values())

    # ========================================================
    # Save CSV
    # ========================================================

    fieldnames = [
        "pmid",
        "title",
        "abstract",
        "journal",
        "year",
        "doi",
        "pmcid",
        "topic",
        "source",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(records)

    print()
    print("=" * 60)
    print(f" Unique articles collected: {len(records)}")
    print(f" Saved to: {OUTPUT_FILE}")
    print("=" * 60)
    print()


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    collect_literature()