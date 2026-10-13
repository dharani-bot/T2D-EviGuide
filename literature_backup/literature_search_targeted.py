#!/usr/bin/env python3
"""
Targeted PubMed literature collection for T2D-EviGuide.

Purpose:
    Collect recent literature specifically relevant to early Type 2 diabetes
    risk assessment, screening, glycemic interpretation, prediction and
    prevention.

This script uses only the Python standard library plus requests, so it is
compatible with the restricted Windows environment used by this project.

Output:
    data/pubmed_literature_targeted.csv

The records are metadata/abstracts returned by PubMed E-utilities. Full-text
reuse is handled separately according to availability and licensing.
"""

from __future__ import annotations

import csv
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import requests


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OUTPUT = Path("data/pubmed_literature_targeted.csv")

# Targeted evidence domains for the project's early-risk-assessment objective.
TOPICS = {
    "early_risk": (
        '("type 2 diabetes"[Title/Abstract] OR "type 2 diabetes mellitus"[Title/Abstract]) '
        'AND ("risk assessment"[Title/Abstract] OR "early risk"[Title/Abstract] '
        'OR "incident diabetes"[Title/Abstract] OR "future diabetes"[Title/Abstract])'
    ),
    "prediabetes_progression": (
        '("type 2 diabetes"[Title/Abstract] OR "type 2 diabetes mellitus"[Title/Abstract]) '
        'AND ("prediabetes"[Title/Abstract] OR "pre-diabetes"[Title/Abstract]) '
        'AND ("progression"[Title/Abstract] OR "incident"[Title/Abstract] '
        'OR "conversion"[Title/Abstract] OR "risk"[Title/Abstract])'
    ),
    "screening": (
        '("type 2 diabetes"[Title/Abstract] OR "type 2 diabetes mellitus"[Title/Abstract]) '
        'AND ("screening"[Title/Abstract] OR "screen"[Title/Abstract]) '
        'AND ("prediabetes"[Title/Abstract] OR "risk"[Title/Abstract] '
        'OR "asymptomatic"[Title/Abstract])'
    ),
    "diagnosis": (
        '("type 2 diabetes"[Title/Abstract] OR "type 2 diabetes mellitus"[Title/Abstract]) '
        'AND ("diagnos*"[Title/Abstract] OR "classification"[Title/Abstract] '
        'OR "diagnostic criteria"[Title/Abstract] OR "threshold"[Title/Abstract])'
    ),
    "hba1c": (
        '("type 2 diabetes"[Title/Abstract] OR "prediabetes"[Title/Abstract]) '
        'AND ("HbA1c"[Title/Abstract] OR "glycated hemoglobin"[Title/Abstract] '
        'OR "glycosylated hemoglobin"[Title/Abstract]) '
        'AND ("screening"[Title/Abstract] OR "risk"[Title/Abstract] '
        'OR "diagnos*"[Title/Abstract] OR "prediction"[Title/Abstract])'
    ),
    "fasting_glucose": (
        '("type 2 diabetes"[Title/Abstract] OR "prediabetes"[Title/Abstract]) '
        'AND ("fasting plasma glucose"[Title/Abstract] OR "fasting glucose"[Title/Abstract]) '
        'AND ("risk"[Title/Abstract] OR "screening"[Title/Abstract] '
        'OR "prediction"[Title/Abstract] OR "progression"[Title/Abstract])'
    ),
    "oral_glucose_tolerance": (
        '("type 2 diabetes"[Title/Abstract] OR "prediabetes"[Title/Abstract]) '
        'AND ("oral glucose tolerance test"[Title/Abstract] OR "OGTT"[Title/Abstract]) '
        'AND ("screening"[Title/Abstract] OR "diagnos*"[Title/Abstract] '
        'OR "risk"[Title/Abstract] OR "progression"[Title/Abstract])'
    ),
    "risk_factors": (
        '("incident type 2 diabetes"[Title/Abstract] OR "incident diabetes"[Title/Abstract] '
        'OR "type 2 diabetes"[Title/Abstract]) '
        'AND ("risk factor*"[Title/Abstract] OR "predictor*"[Title/Abstract] '
        'OR "determinant*"[Title/Abstract]) '
        'AND ("adult*"[Title/Abstract] OR "population"[Title/Abstract])'
    ),
    "risk_prediction": (
        '("type 2 diabetes"[Title/Abstract] OR "type 2 diabetes mellitus"[Title/Abstract]) '
        'AND ("risk prediction"[Title/Abstract] OR "prediction model*"[Title/Abstract] '
        'OR "risk score*"[Title/Abstract] OR "machine learning"[Title/Abstract] '
        'OR "artificial intelligence"[Title/Abstract]) '
        'AND ("incident"[Title/Abstract] OR "future"[Title/Abstract] '
        'OR "early"[Title/Abstract] OR "screening"[Title/Abstract])'
    ),
    "prevention": (
        '("type 2 diabetes"[Title/Abstract] OR "prediabetes"[Title/Abstract]) '
        'AND ("prevention"[Title/Abstract] OR "preventing"[Title/Abstract]) '
        'AND ("adult*"[Title/Abstract] OR "high risk"[Title/Abstract] '
        'OR "prediabetes"[Title/Abstract])'
    ),
    "lifestyle": (
        '("prediabetes"[Title/Abstract] OR "high risk for type 2 diabetes"[Title/Abstract] '
        'OR "type 2 diabetes"[Title/Abstract]) '
        'AND ("lifestyle"[Title/Abstract] OR "diet"[Title/Abstract] '
        'OR "physical activity"[Title/Abstract] OR "exercise"[Title/Abstract] '
        'OR "weight loss"[Title/Abstract]) '
        'AND ("prevention"[Title/Abstract] OR "risk"[Title/Abstract] '
        'OR "progression"[Title/Abstract])'
    ),
    "clinical_guidelines": (
        '("type 2 diabetes"[Title/Abstract] OR "prediabetes"[Title/Abstract]) '
        'AND ("guideline"[Title/Abstract] OR "standards of care"[Title/Abstract] '
        'OR "consensus"[Title/Abstract] OR "recommendation*"[Title/Abstract]) '
        'AND ("screening"[Title/Abstract] OR "diagnos*"[Title/Abstract] '
        'OR "prevention"[Title/Abstract] OR "risk"[Title/Abstract])'
    ),
}

RETMAX = 25
REQUEST_DELAY = 0.35
CURRENT_YEAR = datetime.now().year
START_YEAR = CURRENT_YEAR - 5


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def get_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


def search_pubmed(query: str) -> list[str]:
    params = {
        "db": "pubmed",
        "term": f"({query}) AND ({START_YEAR}: {CURRENT_YEAR}[pdat])",
        "retmax": RETMAX,
        "retmode": "json",
        "sort": "date",
    }
    response = requests.get(
        f"{BASE_URL}/esearch.fcgi",
        params=params,
        timeout=30,
        headers={"User-Agent": "T2D-EviGuide/1.0"},
    )
    response.raise_for_status()
    return response.json()["esearchresult"]["idlist"]


def fetch_pubmed(pmids: list[str], topic: str) -> list[dict]:
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
        timeout=60,
        headers={"User-Agent": "T2D-EviGuide/1.0"},
    )
    response.raise_for_status()

    root = ET.fromstring(response.text)
    records = []

    for article in root.findall(".//PubmedArticle"):
        pmid = get_text(article.find(".//PMID"))
        title = get_text(article.find(".//ArticleTitle"))

        abstract_parts = []
        for node in article.findall(".//Abstract/AbstractText"):
            label = node.attrib.get("Label", "")
            text = get_text(node)
            abstract_parts.append(f"{label}: {text}" if label else text)
        abstract = " ".join(abstract_parts)

        journal = get_text(article.find(".//Journal/Title"))

        year = ""
        for path in (
            ".//PubDate/Year",
            ".//PubDate/MedlineDate",
            ".//ArticleDate/Year",
        ):
            node = article.find(path)
            if node is not None:
                year = get_text(node)
                break

        doi = ""
        for node in article.findall(".//ArticleId"):
            if node.attrib.get("IdType") == "doi":
                doi = get_text(node)
                break

        pmcid = ""
        for node in article.findall(".//ArticleId"):
            if node.attrib.get("IdType") == "pmc":
                pmcid = get_text(node)
                break

        publication_types = [
            get_text(node)
            for node in article.findall(".//PublicationType")
            if get_text(node)
        ]

        records.append(
            {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "journal": journal,
                "year": year,
                "doi": doi,
                "pmcid": pmcid,
                "publication_types": "; ".join(publication_types),
                "topic": topic,
                "source": "PubMed",
            }
        )

    return records


def deduplicate(records: list[dict]) -> list[dict]:
    seen_pmid = set()
    seen_doi = set()
    seen_title = set()
    unique = []

    for record in records:
        pmid = record["pmid"].strip()
        doi = record["doi"].strip().lower()
        title = normalize_title(record["title"])

        if pmid and pmid in seen_pmid:
            continue
        if doi and doi in seen_doi:
            continue
        if title and title in seen_title:
            continue

        if pmid:
            seen_pmid.add(pmid)
        if doi:
            seen_doi.add(doi)
        if title:
            seen_title.add(title)

        unique.append(record)

    return unique


def main() -> None:
    print("=" * 64)
    print(" T2D-EviGuide Targeted PubMed Literature Collection")
    print("=" * 64)
    print(f"Publication window: {START_YEAR}-{CURRENT_YEAR}")
    print(f"Topics: {len(TOPICS)}")
    print()

    all_records = []

    for topic, query in TOPICS.items():
        print(f"Searching topic: {topic}")
        try:
            pmids = search_pubmed(query)
            print(f"  PMID results: {len(pmids)}")

            records = fetch_pubmed(pmids, topic)
            print(f"  Articles fetched: {len(records)}")

            all_records.extend(records)
            time.sleep(REQUEST_DELAY)

        except requests.RequestException as exc:
            print(f"  ERROR: {exc}")

    unique_records = deduplicate(all_records)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "pmid",
        "title",
        "abstract",
        "journal",
        "year",
        "doi",
        "pmcid",
        "publication_types",
        "topic",
        "source",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_records)

    print()
    print("=" * 64)
    print(f"Raw records collected: {len(all_records)}")
    print(f"Unique articles:       {len(unique_records)}")
    print(f"Saved to:              {OUTPUT}")
    print("=" * 64)


if __name__ == "__main__":
    main()
