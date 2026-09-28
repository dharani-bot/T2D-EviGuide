import re


def check_clinical_guardrails(assessment):
    """
    Offline safety/quality screening of a generated clinical assessment.

    This function flags statements for human review.
    It does NOT diagnose, correct, or rewrite the assessment.
    """

    text = str(assessment)
    lower = text.lower()

    flags = {
        "hba1c_igt": False,
        "fasting": False,
        "threshold": False,
        "diagnostic_language": False,
    }

    # ---------------------------------------------------------
    # 1. HbA1c / IGT terminology confusion
    # ---------------------------------------------------------

    hba1c_patterns = [
        r"hba1c.{0,100}\bigt\b",
        r"\bigt\b.{0,100}hba1c",
        r"hba1c.{0,100}impaired glucose tolerance",
        r"impaired glucose tolerance.{0,100}hba1c",
    ]

    for pattern in hba1c_patterns:
        if re.search(pattern, lower, re.DOTALL):
            flags["hba1c_igt"] = True
            break

    # ---------------------------------------------------------
    # 2. Fasting interpretation
    # ---------------------------------------------------------

    fasting_patterns = [
        r"inpatient.{0,100}fasting glucose",
        r"inpatient.{0,100}fasting value",
        r"inpatient.{0,100}fasting level",
        r"hospital.{0,100}fasting glucose",
        r"blood glucose.{0,60}fasting",
    ]

    for pattern in fasting_patterns:
        if re.search(pattern, lower, re.DOTALL):
            flags["fasting"] = True
            break

    # ---------------------------------------------------------
    # 3. Threshold-related language
    # ---------------------------------------------------------

    threshold_patterns = [
        r"\bthreshold\b",
        r"\bcut[- ]?off\b",
        r"\bcutoff\b",
        r"\bgreater than\b",
        r"\bless than\b",
        r"\b≥\b",
        r"\b≤\b",
        r">=\s*\d",
        r"<=\s*\d",
    ]

    for pattern in threshold_patterns:
        if re.search(pattern, lower, re.DOTALL):
            flags["threshold"] = True
            break

    # ---------------------------------------------------------
    # 4. Potential diagnostic overreach
    # ---------------------------------------------------------

    diagnostic_patterns = [
        r"\bconfirms diabetes\b",
        r"\bconfirmed diabetes\b",
        r"\bdiagnosed with diabetes\b",
        r"\bdiagnosis of diabetes\b",
        r"\bhas diabetes\b",
    ]

    for pattern in diagnostic_patterns:
        if re.search(pattern, lower, re.DOTALL):
            flags["diagnostic_language"] = True
            break

    return flags