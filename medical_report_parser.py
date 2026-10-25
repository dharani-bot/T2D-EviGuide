
import csv
import io
import re
from datetime import datetime


# Recognized clinical measurements and common units.
PATTERNS = {
    "hba1c": [
        r"\bHbA1c\b\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%?"
    ],
    "fasting_glucose": [
        r"\bfasting\s+(?:blood\s+)?glucose\b\s*[:=]?\s*(\d+(?:\.\d+)?)",
        r"\bFBS\b\s*[:=]?\s*(\d+(?:\.\d+)?)"
    ],
    "blood_glucose": [
        r"\b(?:blood\s+)?glucose\b\s*[:=]?\s*(\d+(?:\.\d+)?)",
        r"\bRBS\b\s*[:=]?\s*(\d+(?:\.\d+)?)"
    ],
    "total_cholesterol": [
        r"\btotal\s+cholesterol\b\s*[:=]?\s*(\d+(?:\.\d+)?)"
    ],
    "systolic_bp": [
        r"\b(?:systolic\s+(?:blood\s+)?pressure|systolic\s+BP)\b\s*[:=]?\s*(\d+(?:\.\d+)?)"
    ],
    "diastolic_bp": [
        r"\b(?:diastolic\s+(?:blood\s+)?pressure|diastolic\s+BP)\b\s*[:=]?\s*(\d+(?:\.\d+)?)"
    ],
}

FIELD_LABELS = {
    "hba1c": "HbA1c (%)",
    "fasting_glucose": "Fasting glucose",
    "blood_glucose": "Blood glucose",
    "total_cholesterol": "Total cholesterol",
    "systolic_bp": "Systolic blood pressure",
    "diastolic_bp": "Diastolic blood pressure",
}


def extract_from_text(text):
    """Extract candidate clinical values from plain text."""

    results = {}
    warnings = []

    for field, patterns in PATTERNS.items():
        matches = []

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    value = float(match.group(1))
                    matches.append(value)
                except (ValueError, IndexError):
                    continue

        if matches:
            unique_values = list(dict.fromkeys(matches))

            if len(unique_values) > 1:
                warnings.append(
                    f"Multiple values found for {FIELD_LABELS[field]}: "
                    f"{unique_values}. Review the original report."
                )
            else:
                results[field] = unique_values[0]

    date_match = re.search(
        r"\b(?:report date|collection date|test date|date)\b"
        r"\s*[:=]?\s*(\d{4}-\d{2}-\d{2})",
        text,
        re.IGNORECASE,
    )

    if date_match:
        try:
            datetime.strptime(date_match.group(1), "%Y-%m-%d")
            results["report_date"] = date_match.group(1)
        except ValueError:
            warnings.append("The report date could not be interpreted.")

    results["fields_found"] = [
        field for field in FIELD_LABELS if field in results
    ]
    results["warnings"] = warnings
    results["extracted_text"] = text

    if not results["fields_found"]:
        warnings.append(
            "No recognized measurements were found. "
            "Check the report format or enter the values manually."
        )

    return results


def extract_from_csv(file_bytes):
    """Read a CSV report and convert it to searchable text."""

    try:
        content = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = file_bytes.decode("latin-1")

    reader = csv.reader(io.StringIO(content))
    lines = []

    for row in reader:
        lines.append(" ".join(str(cell).strip() for cell in row))

    return extract_from_text("\n".join(lines))


def parse_uploaded_report(uploaded_file):
    """
    Parse a PDF, TXT, or CSV uploaded through Streamlit.

    Returns a dictionary of candidate values, warnings, and source text.
    Values must be reviewed before importing them.
    """

    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if filename.endswith(".txt"):
        try:
            text = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1")

        return extract_from_text(text)

    if filename.endswith(".csv"):
        return extract_from_csv(file_bytes)

    if filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(file_bytes))
            pages = []

            for page in reader.pages:
                pages.append(page.extract_text() or "")

            text = "\n".join(pages)

            if not text.strip():
                return {
                    "fields_found": [],
                    "warnings": [
                        "No selectable text was found. "
                        "This may be a scanned PDF; OCR is not implemented yet."
                    ],
                    "extracted_text": "",
                }

            return extract_from_text(text)

        except ImportError:
            raise RuntimeError(
                "PDF support requires pypdf. Install it using: "
                "python -m pip install pypdf"
            )

    raise ValueError("Supported file types are PDF, CSV, and TXT.")
