# ============================================================
# T2D-EviGuide
# Evidence Verification Module
# ============================================================

import re


def verify_assessment(assessment, evidence):
    """
    Verify whether an AI-generated assessment refers to
    the retrieved evidence provided to the system.

    This is a prototype-level verification layer.
    It checks:

    1. Whether an assessment was generated.
    2. Whether evidence was retrieved.
    3. Whether the assessment contains evidence references.
    4. Whether referenced evidence numbers/article IDs
       correspond to the retrieved evidence.

    It does NOT independently verify medical truth.
    """

    if not assessment:
        return {
            "success": False,
            "status": "FAILED",
            "message": "No assessment was provided.",
            "evidence_references_found": [],
            "verified_references": [],
            "unverified_references": [],
        }

    if not evidence:
        return {
            "success": False,
            "status": "FAILED",
            "message": "No retrieved evidence was available.",
            "evidence_references_found": [],
            "verified_references": [],
            "unverified_references": [],
        }

    # --------------------------------------------------------
    # Extract evidence references such as:
    # [Evidence 1 | ARTICLE_ID]
    # [Evidence 2 | PMID12345]
    # --------------------------------------------------------

    reference_pattern = r"\[Evidence\s+(\d+)\s*\|\s*([^\]]+)\]"

    matches = re.findall(
        reference_pattern,
        assessment,
        flags=re.IGNORECASE
    )

    evidence_references_found = []

    for evidence_number, article_id in matches:

        evidence_references_found.append({
            "evidence_number": int(evidence_number),
            "article_id": article_id.strip()
        })

    # --------------------------------------------------------
    # Build available evidence reference map
    # --------------------------------------------------------

    available_evidence = {}

    for item in evidence:

        evidence_number = item.get(
            "evidence_number"
        )

        article_id = str(
            item.get(
                "article_id",
                ""
            )
        ).strip()

        if evidence_number is not None:

            available_evidence[
                int(evidence_number)
            ] = article_id

    # --------------------------------------------------------
    # Verify references
    # --------------------------------------------------------

    verified_references = []
    unverified_references = []

    for reference in evidence_references_found:

        number = reference[
            "evidence_number"
        ]

        article_id = reference[
            "article_id"
        ]

        if number not in available_evidence:

            unverified_references.append({
                "evidence_number": number,
                "article_id": article_id,
                "reason": "Evidence number was not retrieved."
            })

            continue

        retrieved_article_id = available_evidence[
            number
        ]

        # Compare article IDs when available
        if (
            article_id.lower()
            == retrieved_article_id.lower()
        ):

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
    # Determine overall status
    # --------------------------------------------------------

    if not evidence_references_found:

        status = "REVIEW REQUIRED"

        message = (
            "The assessment does not contain explicit "
            "evidence references in the expected format."
        )

    elif unverified_references:

        status = "REVIEW REQUIRED"

        message = (
            "Some evidence references could not be "
            "verified against the retrieved evidence."
        )

    else:

        status = "VERIFIED"

        message = (
            "All explicit evidence references in the "
            "assessment matched the retrieved evidence."
        )

    return {
        "success": True,
        "status": status,
        "message": message,
        "evidence_references_found": (
            evidence_references_found
        ),
        "verified_references": (
            verified_references
        ),
        "unverified_references": (
            unverified_references
        ),
        "total_evidence_items": len(evidence),
        "total_references_found": (
            len(evidence_references_found)
        ),
        "total_verified": (
            len(verified_references)
        ),
        "total_unverified": (
            len(unverified_references)
        ),
    }