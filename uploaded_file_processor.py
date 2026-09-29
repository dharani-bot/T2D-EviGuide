"""
uploaded_file_processor.py

Extracts basic clinical information from uploaded
PDF, TXT, CSV, and XLSX files.

Important:
- Extracted values are not assumed to be clinically correct.
- Missing values remain None or "Unknown".
- Extracted values must be reviewed before assessment.
- This module does not diagnose patients.
"""

import re

import pandas as pd


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".csv",
    ".xlsx",
}


# ============================================================
# BASIC TEXT EXTRACTION
# ============================================================

def extract_text_from_txt(uploaded_file):
    """
    Extract text from a TXT file.
    """

    raw = uploaded_file.read()

    try:
        return raw.decode("utf-8")

    except UnicodeDecodeError:

        return raw.decode(
            "latin-1",
            errors="ignore"
        )


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from a PDF file.

    Requires PyMuPDF:

        pip install pymupdf
    """

    try:

        import fitz

    except ImportError:

        raise ImportError(
            "PDF support requires PyMuPDF. "
            "Install it with: pip install pymupdf"
        )

    pdf_bytes = uploaded_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    pages = []

    for page in document:

        pages.append(
            page.get_text()
        )

    document.close()

    return "\n".join(pages)


# ============================================================
# CSV / XLSX EXTRACTION
# ============================================================

def dataframe_to_text(dataframe):
    """
    Convert the first row of a dataframe into
    simple clinical text.
    """

    if dataframe.empty:

        return ""

    lines = []

    first_row = dataframe.iloc[0]

    for column in dataframe.columns:

        value = first_row[column]

        if pd.isna(value):

            value = ""

        lines.append(
            f"{column}: {value}"
        )

    return "\n".join(lines)


def extract_text_from_csv(uploaded_file):
    """
    Extract the first patient record from CSV.
    """

    dataframe = pd.read_csv(
        uploaded_file
    )

    return dataframe_to_text(
        dataframe
    )


def extract_text_from_xlsx(uploaded_file):
    """
    Extract the first patient record from XLSX.
    """

    dataframe = pd.read_excel(
        uploaded_file
    )

    return dataframe_to_text(
        dataframe
    )


# ============================================================
# VALUE EXTRACTION HELPERS
# ============================================================

def _first_match(
    text,
    patterns,
    flags=re.IGNORECASE
):
    """
    Return the first regex match from a list
    of patterns.
    """

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags
        )

        if match:

            try:

                return match.group(1)

            except IndexError:

                return match.group(0)

    return None


def _to_float(value):
    """
    Safely convert a value to float.
    """

    if value is None:

        return None

    try:

        return float(
            str(value)
            .replace(",", "")
            .strip()
        )

    except (
        ValueError,
        TypeError
    ):

        return None


def _to_int(value):
    """
    Safely convert a value to integer.
    """

    value = _to_float(
        value
    )

    if value is None:

        return None

    return int(
        value
    )


# ============================================================
# PATIENT INFORMATION
# ============================================================

def extract_age(text):
    """
    Extract patient age.
    """

    value = _first_match(
        text,
        [
            r"\bage\s*[:\-]?\s*(\d{1,3})\s*(?:years?|yrs?)?",
            r"\b(\d{1,3})\s*(?:years?|yrs?)\s*old\b",
        ]
    )

    return _to_int(
        value
    )


def extract_sex(text):
    """
    Extract patient sex.
    """

    value = _first_match(
        text,
        [
            r"\bsex\s*[:\-]?\s*(female|male|other)",
            r"\bgender\s*[:\-]?\s*(female|male|other)",
        ]
    )

    if value is None:

        return "Unknown"

    return value.capitalize()


# ============================================================
# ANTHROPOMETRIC DATA
# ============================================================

def extract_weight(text):
    """
    Extract weight in kilograms.
    """

    value = _first_match(
        text,
        [
            r"\bweight\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*kg\b",
            r"\bweight\s*[:\-]?\s*(\d+(?:\.\d+)?)\b",
        ]
    )

    return _to_float(
        value
    )


def extract_height(text):
    """
    Extract height in centimetres.
    """

    value = _first_match(
        text,
        [
            r"\bheight\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*cm\b",
            r"\bheight\s*[:\-]?\s*(\d+(?:\.\d+)?)\b",
        ]
    )

    return _to_float(
        value
    )


def extract_bmi(text):
    """
    Extract explicitly reported BMI.
    """

    value = _first_match(
        text,
        [
            r"\bBMI\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"\bbody mass index\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ]
    )

    return _to_float(
        value
    )


# ============================================================
# LABORATORY DATA
# ============================================================

def extract_hba1c(text):
    """
    Extract HbA1c percentage.
    """

    value = _first_match(
        text,
        [
            r"\bHbA1c\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%",
            r"\bHbA1C\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"\bA1c\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%",
        ]
    )

    return _to_float(
        value
    )


def extract_glucose(text):
    """
    Extract blood glucose in mg/dL.
    """

    value = _first_match(
        text,
        [
            r"\bblood\s+glucose\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*mg/dL",
            r"\bglucose\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*mg/dL",
            r"\bglucose\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ]
    )

    return _to_float(
        value
    )


def extract_fasting_status(text):
    """
    Determine the stated glucose measurement status.

    Returns:
        Fasting
        Random
        Non-fasting
        2-hour OGTT
        Unknown
    """

    lowered = text.lower()

    if re.search(
        r"\bfasting\s+(blood\s+)?glucose\b",
        lowered
    ):

        return "Fasting"

    if re.search(
        r"\brandom\s+(blood\s+)?glucose\b",
        lowered
    ):

        return "Random"

    if re.search(
        r"\bnon[-\s]?fasting\s+(blood\s+)?glucose\b",
        lowered
    ):

        return "Non-fasting"

    if re.search(
        r"\b2[-\s]?hour\b.*\bogtt\b",
        lowered
    ):

        return "2-hour OGTT"

    return "Unknown"


def extract_total_cholesterol(text):
    """
    Extract total cholesterol in mg/dL.
    """

    value = _first_match(
        text,
        [
            r"\btotal\s+cholesterol\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*mg/dL",
            r"\btotal\s+cholesterol\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ]
    )

    return _to_float(
        value
    )


# ============================================================
# BLOOD PRESSURE
# ============================================================

def extract_systolic_bp(text):
    """
    Extract systolic blood pressure.
    """

    value = _first_match(
        text,
        [
            r"\bsystolic\s*(?:blood\s*)?pressure\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"\bSBP\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ]
    )

    return _to_float(
        value
    )


def extract_diastolic_bp(text):
    """
    Extract diastolic blood pressure.
    """

    value = _first_match(
        text,
        [
            r"\bdiastolic\s*(?:blood\s*)?pressure\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"\bDBP\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ]
    )

    return _to_float(
        value
    )


# ============================================================
# FAMILY HISTORY
# ============================================================

def extract_family_history(text):
    """
    Extract family history of diabetes.
    """

    lowered = text.lower()

    if re.search(
        r"family\s+history.*\b(yes|positive)\b",
        lowered
    ):

        return "Yes"

    if re.search(
        r"family\s+history.*\b(no|negative)\b",
        lowered
    ):

        return "No"

    return "Unknown"


# ============================================================
# LIFESTYLE
# ============================================================

def extract_physical_activity(text):
    """
    Extract physical activity level.
    """

    lowered = text.lower()

    if re.search(
        r"physical\s+activity.*\blow\b",
        lowered
    ):

        return "Low"

    if re.search(
        r"physical\s+activity.*\bmoderate\b",
        lowered
    ):

        return "Moderate"

    if re.search(
        r"physical\s+activity.*\bhigh\b",
        lowered
    ):

        return "High"

    return "Unknown"


def extract_smoking(text):
    """
    Extract smoking status.
    """

    lowered = text.lower()

    if re.search(
        r"\bsmoking\b.*\b(current|active)\b",
        lowered
    ):

        return "Current"

    if re.search(
        r"\bsmoking\b.*\b(former|ex[-\s]?smoker)\b",
        lowered
    ):

        return "Former"

    if re.search(
        r"\bsmoking\b.*\b(never|no)\b",
        lowered
    ):

        return "Never"

    return "Unknown"


# ============================================================
# MEDICAL HISTORY
# ============================================================

def extract_medical_history(text):
    """
    Extract previous medical conditions.
    """

    value = _first_match(
        text,
        [
            r"\bmedical\s+history\s*[:\-]?\s*(.+)",
            r"\bprevious\s+medical\s+conditions\s*[:\-]?\s*(.+)",
        ]
    )

    if value:

        return value.strip()

    return ""


def extract_medications(text):
    """
    Extract current medications.
    """

    value = _first_match(
        text,
        [
            r"\bcurrent\s+medications?\s*[:\-]?\s*(.+)",
            r"\bmedications?\s*[:\-]?\s*(.+)",
        ]
    )

    if value:

        return value.strip()

    return ""


# ============================================================
# PATIENT DATA EXTRACTION
# ============================================================

def extract_patient_data_from_text(text):
    """
    Extract a standardized patient-data dictionary
    from clinical text.
    """

    weight = extract_weight(
        text
    )

    height = extract_height(
        text
    )

    bmi = extract_bmi(
        text
    )

    # --------------------------------------------------------
    # Calculate BMI only when weight and height are
    # explicitly available and BMI itself was not reported.
    # --------------------------------------------------------

    if (
        bmi is None
        and weight is not None
        and height is not None
        and height > 0
    ):

        bmi = round(
            weight / (
                (height / 100) ** 2
            ),
            1
        )

    patient_data = {

        "age": extract_age(
            text
        ),

        "sex": extract_sex(
            text
        ),

        "weight": weight,

        "height": height,

        "bmi": bmi,

        "blood_glucose": extract_glucose(
            text
        ),

        "fasting_status": extract_fasting_status(
            text
        ),

        "hba1c": extract_hba1c(
            text
        ),

        "total_cholesterol": extract_total_cholesterol(
            text
        ),

        "systolic_bp": extract_systolic_bp(
            text
        ),

        "diastolic_bp": extract_diastolic_bp(
            text
        ),

        "family_history": extract_family_history(
            text
        ),

        "physical_activity": extract_physical_activity(
            text
        ),

        "smoking": extract_smoking(
            text
        ),

        "medical_history": extract_medical_history(
            text
        ),

        "medications": extract_medications(
            text
        ),
    }

    return patient_data


# ============================================================
# UPLOADED FILE ROUTER
# ============================================================

def extract_patient_data(uploaded_file):
    """
    Main function called by Streamlit.

    Parameters:
        uploaded_file:
            Streamlit UploadedFile object.

    Returns:
        patient_data:
            Standardized clinical data dictionary.

        extracted_text:
            Raw text extracted from the uploaded file.
    """

    filename = uploaded_file.name.lower()

    if filename.endswith(".txt"):

        text = extract_text_from_txt(
            uploaded_file
        )

    elif filename.endswith(".pdf"):

        text = extract_text_from_pdf(
            uploaded_file
        )

    elif filename.endswith(".csv"):

        text = extract_text_from_csv(
            uploaded_file
        )

    elif filename.endswith(".xlsx"):

        text = extract_text_from_xlsx(
            uploaded_file
        )

    else:

        raise ValueError(
            "Unsupported file format. "
            "Please upload PDF, TXT, CSV, or XLSX."
        )

    if not text.strip():

        raise ValueError(
            "No readable text was found in the uploaded file."
        )

    patient_data = (
        extract_patient_data_from_text(
            text
        )
    )

    return (
        patient_data,
        text
    )


# ============================================================
# SIMPLE LOCAL TEST
# ============================================================

if __name__ == "__main__":

    sample_text = """
    Patient Clinical Report

    Age: 45 years
    Sex: Female
    Weight: 62 kg
    Height: 160 cm

    Fasting Blood Glucose: 100 mg/dL
    HbA1c: 5.7%

    Systolic Blood Pressure: 120 mmHg
    Diastolic Blood Pressure: 80 mmHg

    Family history of diabetes: No
    Physical activity: Low
    Smoking: Never

    Medical History: Hypertension
    Medications: No medications
    """

    result = extract_patient_data_from_text(
        sample_text
    )

    print()
    print(
        "Extracted Patient Data"
    )
    print(
        "=" * 40
    )

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )