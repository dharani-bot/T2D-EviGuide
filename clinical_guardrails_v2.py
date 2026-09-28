import re


def _has_any(text, patterns):
    """Return True if any regex pattern matches the text."""
    return any(
        re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        for pattern in patterns
    )


def check_clinical_guardrails_v2(assessment, patient_data=None):
    """
    Measurement-aware clinical safety/terminology guardrails.

    Parameters
    ----------
    assessment : str
        LLM-generated clinical assessment.

    patient_data : dict, optional
        Structured patient measurements, e.g.
        {
            "hba1c": 7.1,
            "blood_glucose": 206.1,
            "fasting_glucose": None,
            "ogtt_2h_glucose": None,
            "glucose_measurement_type": "inpatient"
        }

    Returns
    -------
    dict
        Guardrail flags.
    """

    text = str(assessment)
    lower = text.lower()
    patient_data = patient_data or {}

    flags = {
        "hba1c_igt": False,
        "fasting": False,
        "threshold": False,
        "diagnostic_language": False,
    }

    # ---------------------------------------------------------
    # Patient measurement information
    # ---------------------------------------------------------

    hba1c = patient_data.get("hba1c")
    blood_glucose = patient_data.get("blood_glucose")
    fasting_glucose = patient_data.get("fasting_glucose")
    ogtt_2h_glucose = patient_data.get("ogtt_2h_glucose")

    measurement_type = str(
        patient_data.get("glucose_measurement_type", "")
    ).lower()

    has_hba1c = hba1c is not None
    has_fasting = fasting_glucose is not None
    has_ogtt = ogtt_2h_glucose is not None

    # In our MIMIC dataset, blood glucose is inpatient and
    # fasting status is not established.
    unspecified_inpatient_glucose = (
        blood_glucose is not None
        and not has_fasting
        and not has_ogtt
        and (
            "inpatient" in measurement_type
            or "unspecified" in measurement_type
            or measurement_type == ""
        )
    )

    # ---------------------------------------------------------
    # 1. HbA1c / IGT terminology
    # ---------------------------------------------------------

    hba1c_igt_patterns = [
        r"hba1c.{0,80}"
        r"(?:is|indicates|means|represents|defines|meets|qualifies as)"
        r".{0,50}"
        r"(?:igt|impaired glucose tolerance)",

        r"(?:igt|impaired glucose tolerance)"
        r".{0,80}"
        r"(?:is defined|defined|based)"
        r".{0,50}"
        r"hba1c",

        r"hba1c.{0,100}"
        r"(?:igt|impaired glucose tolerance)"
        r".{0,100}"
        r"(?:range|threshold|cutoff|criterion)",
    ]

    if has_hba1c and _has_any(lower, hba1c_igt_patterns):
        flags["hba1c_igt"] = True

    # ---------------------------------------------------------
    # 2. Fasting interpretation
    # ---------------------------------------------------------

    limitation_phrases = [
        "not confirmed as fasting",
        "not confirmed fasting",
        "cannot be considered fasting",
        "cannot be considered as fasting",
        "cannot be classified as fasting",
        "cannot be used to assess fasting",
        "fasting status is not established",
        "fasting status was not established",
        "fasting status is unknown",
        "fasting status was unknown",
        "not a fasting measurement",
        "not confirmed to be fasting",
        "fasting cannot be determined",
        "not equivalent to fasting",
        "fasting status cannot be established",
        "fasting status cannot be determined",
    ]

    # If the model explicitly explains the limitation,
    # do not flag it as a fasting error.
    if not _has_any(lower, limitation_phrases):

        positive_fasting_patterns = [
            r"\binpatient\b.{0,80}\bfasting glucose\b",
            r"\binpatient\b.{0,80}\bfasting value\b",
            r"\binpatient\b.{0,80}\bfasting level\b",
            r"\binpatient\b.{0,80}\bfasting measurement\b",
            r"\bthe patient's fasting glucose\b",
            r"\bpatient's fasting glucose\b",
        ]

        if (
            unspecified_inpatient_glucose
            and _has_any(lower, positive_fasting_patterns)
        ):
            flags["fasting"] = True

        # If the assessment gives a numerical fasting glucose
        # even though fasting glucose was not available.
        if not has_fasting:

            numeric_fasting_patterns = [
                r"\bfasting glucose\b.{0,40}"
                r"\d+(?:\.\d+)?\s*mg/dl\b",

                r"\bfasting glucose\b.{0,40}"
                r"\d+(?:\.\d+)?\b",
            ]

            if _has_any(lower, numeric_fasting_patterns):
                flags["fasting"] = True

    # ---------------------------------------------------------
    # 3. Threshold application
    # ---------------------------------------------------------

    # An unspecified inpatient glucose must not be compared
    # directly with fasting, IGT, or OGTT-specific thresholds.
    if unspecified_inpatient_glucose:

        inappropriate_threshold_patterns = [

            r"inpatient.{0,100}"
            r"(?:meets|does not meet|above|below|exceeds)"
            r".{0,100}"
            r"(?:fasting|igt|impaired glucose tolerance|"
            r"oral glucose tolerance|ogtt)",

            r"(?:fasting|igt|impaired glucose tolerance|"
            r"oral glucose tolerance|ogtt)"
            r".{0,100}"
            r"(?:meets|does not meet|above|below|exceeds)"
            r".{0,100}"
            r"inpatient",

            r"inpatient.{0,100}"
            r"(?:threshold|cutoff|criterion)"
            r".{0,100}"
            r"(?:fasting|igt|ogtt)",

            r"(?:fasting|igt|ogtt)"
            r".{0,100}"
            r"(?:threshold|cutoff|criterion)"
            r".{0,100}"
            r"inpatient",
        ]

        if _has_any(lower, inappropriate_threshold_patterns):
            flags["threshold"] = True

    # ---------------------------------------------------------
    # 4. Diagnostic overreach
    # ---------------------------------------------------------

    diagnostic_limitation_phrases = [
        "does not establish a diagnosis",
        "does not confirm a diagnosis",
        "cannot establish a diagnosis",
        "cannot confirm a diagnosis",
        "not sufficient to diagnose",
        "not sufficient for diagnosis",
        "not a diagnosis",
        "should not be interpreted as a diagnosis",
        "diagnosis cannot be made",
        "clinical diagnosis requires",
        "requires confirmation",
        "requires confirmatory testing",
        "diagnostic confirmation is required",
    ]

    if not _has_any(lower, diagnostic_limitation_phrases):

        diagnostic_patterns = [

            r"\b(?:this|the|patient's|patient)\b"
            r".{0,40}"
            r"\bconfirms diabetes\b",

            r"\b(?:this|the|patient's|patient)\b"
            r".{0,40}"
            r"\bconfirmed diabetes\b",

            r"\b(?:this|the|patient's|patient)\b"
            r".{0,40}"
            r"\bdiagnosed with diabetes\b",

            r"\b(?:this|the|patient's|patient)\b"
            r".{0,40}"
            r"\bhas diabetes\b",

            r"\bhba1c\b.{0,80}\bconfirms diabetes\b",

            r"\bhba1c\b.{0,80}\bdiagnostic of diabetes\b",
        ]

        if _has_any(lower, diagnostic_patterns):
            flags["diagnostic_language"] = True

    return flags