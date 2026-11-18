"""
T2D-EviGuide
Evidence Verification Module

Purpose:
Check whether AI-generated evidence citations match
the retrieved medical literature supplied to the system.

IMPORTANT:
This module verifies citation correspondence only.
It does not verify medical truth or semantic entailment.
"""

import re


# ============================================================
# CITATION PATTERN
# ============================================================

CITATION_PATTERN = re.compile(
    r"\[\s*Evidence\s+(\d+)\s*\|\s*([^\]]+?)\s*\]",
    re.IGNORECASE
)

ANY_EVIDENCE_REFERENCE_PATTERN = re.compile(
    r"\[\s*Evidence\b[^\]]*\]",
    re.IGNORECASE
)


# ============================================================
# MAIN VERIFICATION FUNCTION
# ============================================================

def verify_assessment(assessment, evidence):

    """
    Verify whether citations in an AI-generated assessment
    correspond to retrieved evidence.

    Checks:
        1. Assessment availability.
        2. Retrieved evidence availability.
        3. Citation format.
        4. Evidence number correspondence.
        5. Article ID correspondence.

    Does NOT verify:
        - Medical truth.
        - Clinical accuracy.
        - Semantic support of individual claims.
        - Quality of the original research.
    """

    if not isinstance(assessment, str) or not assessment.strip():

        return {
            "success": False,
            "status": "FAILED",
            "message": "No assessment was provided.",
            "evidence_references_found": [],
            "verified_references": [],
            "unverified_references": [],
            "total_evidence_items": 0,
            "total_references_found": 0,
            "total_verified": 0,
            "total_unverified": 0,
        }

    if not isinstance(evidence, (list, tuple)) or not evidence:

        return {
            "success": False,
            "status": "FAILED",
            "message": "No retrieved evidence was available.",
            "evidence_references_found": [],
            "verified_references": [],
            "unverified_references": [],
            "total_evidence_items": 0,
            "total_references_found": 0,
            "total_verified": 0,
            "total_unverified": 0,
        }

    # --------------------------------------------------------
    # BUILD AVAILABLE EVIDENCE MAP
    # --------------------------------------------------------

    available_evidence = {}

    for index, item in enumerate(evidence, start=1):

        if not isinstance(item, dict):
            continue

        evidence_number = item.get(
            "evidence_number",
            index
        )

        try:
            evidence_number = int(evidence_number)
        except (TypeError, ValueError):
            continue

        if evidence_number <= 0:
            continue

        article_id = str(
            item.get("article_id") or ""
        ).strip()

        available_evidence[evidence_number] = article_id

    # --------------------------------------------------------
    # EXTRACT VALID-FORMAT REFERENCES
    # --------------------------------------------------------

    matches = list(
        CITATION_PATTERN.finditer(assessment)
    )

    evidence_references_found = []

    for match in matches:

        evidence_number = int(match.group(1))

        article_id = match.group(2).strip()

        evidence_references_found.append({

            "evidence_number": evidence_number,

            "article_id": article_id

        })

    # --------------------------------------------------------
    # IDENTIFY MALFORMED EVIDENCE REFERENCES
    # --------------------------------------------------------

    all_reference_matches = list(
        ANY_EVIDENCE_REFERENCE_PATTERN.finditer(assessment)
    )

    malformed_references = []

    valid_spans = {
        match.span()
        for match in matches
    }

    for match in all_reference_matches:

        if match.span() not in valid_spans:

            malformed_references.append({

                "reference": match.group(0),

                "reason": "Citation does not follow the required format."

            })

    # --------------------------------------------------------
    # VERIFY CITATIONS
    # --------------------------------------------------------

    verified_references = []

    unverified_references = []

    for reference in evidence_references_found:

        number = reference["evidence_number"]

        article_id = reference["article_id"]

        if number not in available_evidence:

            unverified_references.append({

                "evidence_number": number,

                "article_id": article_id,

                "reason": "Evidence number was not retrieved."

            })

            continue

        retrieved_article_id = available_evidence[number]

        if not article_id:

            unverified_references.append({

                "evidence_number": number,

                "article_id": article_id,

                "reason": "Article ID is missing."

            })

            continue

        if not retrieved_article_id or retrieved_article_id.upper() == "UNKNOWN":

            unverified_references.append({

                "evidence_number": number,

                "article_id": article_id,

                "reason": "Retrieved evidence has no reliable article ID."

            })

            continue

        if article_id.casefold() == retrieved_article_id.casefold():

            verified_references.append({

                "evidence_number": number,

                "article_id": article_id,

                "status": "Verified"

            })

        else:

            unverified_references.append({

                "evidence_number": number,

                "article_id": article_id,

                "retrieved_article_id": retrieved_article_id,

                "reason": "Article ID does not match retrieved evidence."

            })

    # --------------------------------------------------------
    # ADD MALFORMED REFERENCES TO REVIEW COUNT
    # --------------------------------------------------------

    for malformed in malformed_references:

        unverified_references.append({

            "reference": malformed["reference"],

            "reason": malformed["reason"]

        })

    # --------------------------------------------------------
    # DETERMINE VERIFICATION STATUS
    # --------------------------------------------------------

    if not evidence_references_found and not malformed_references:

        status = "REVIEW REQUIRED"

        message = (
            "No explicit evidence citations were found. "
            "Manual review is required."
        )

    elif unverified_references:

        status = "REVIEW REQUIRED"

        message = (
            "Some evidence citations could not be matched "
            "to the retrieved literature. Manual review is required."
        )

    else:

        status = "VERIFIED"

        message = (
            "All detected evidence citations matched "
            "the corresponding retrieved article IDs. "
            "This does not establish medical accuracy."
        )

    # --------------------------------------------------------
    # RETURN VERIFICATION REPORT
    # --------------------------------------------------------

    return {

        "success": True,

        "status": status,

        "message": message,

        "evidence_references_found": evidence_references_found,

        "verified_references": verified_references,

        "unverified_references": unverified_references,

        "malformed_references": malformed_references,

        "total_evidence_items": len(evidence),

        "total_references_found": len(evidence_references_found),

        "total_verified": len(verified_references),

        "total_unverified": len(unverified_references),

    }