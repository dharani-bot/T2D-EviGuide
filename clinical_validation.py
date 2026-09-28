from typing import Dict, List, Any


def validate_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs basic data-quality validation.

    This function checks whether entered values are:
    - present where required
    - within reasonable input boundaries
    - internally consistent

    It does NOT diagnose disease or determine medical risk.
    """

    errors: List[str] = []
    warnings: List[str] = []

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------

    required_fields = {
        "age": "Age",
        "sex": "Sex",
        "weight": "Weight",
        "height": "Height",
        "fasting_glucose": "Fasting blood glucose",
        "hba1c": "HbA1c",
        "systolic_bp": "Systolic blood pressure",
        "diastolic_bp": "Diastolic blood pressure",
    }

    for field, label in required_fields.items():
        value = data.get(field)

        if value is None or value == "":
            errors.append(f"{label} is required.")

    # ---------------------------------------------------------
    # Age validation
    # ---------------------------------------------------------

    age = data.get("age")

    if age is not None:
        if age < 1 or age > 120:
            errors.append("Age must be between 1 and 120 years.")

    # ---------------------------------------------------------
    # Height validation
    # ---------------------------------------------------------

    height = data.get("height")

    if height is not None:
        if height < 50 or height > 250:
            errors.append("Height must be between 50 and 250 cm.")

    # ---------------------------------------------------------
    # Weight validation
    # ---------------------------------------------------------

    weight = data.get("weight")

    if weight is not None:
        if weight <= 0 or weight > 300:
            errors.append("Weight must be greater than 0 and no more than 300 kg.")

    # ---------------------------------------------------------
    # BMI calculation and validation
    # ---------------------------------------------------------

    bmi = None

    if height and weight and height > 0:
        height_m = height / 100
        bmi = weight / (height_m ** 2)

        if bmi < 10 or bmi > 100:
            warnings.append(
                "The calculated BMI is outside the expected range. "
                "Please verify height and weight."
            )

    # ---------------------------------------------------------
    # Fasting glucose
    # ---------------------------------------------------------

    glucose = data.get("fasting_glucose")

    if glucose is not None:
        if glucose < 0 or glucose > 600:
            errors.append(
                "Fasting blood glucose must be between 0 and 600 mg/dL."
            )

    # ---------------------------------------------------------
    # HbA1c
    # ---------------------------------------------------------

    hba1c = data.get("hba1c")

    if hba1c is not None:
        if hba1c < 0 or hba1c > 20:
            errors.append(
                "HbA1c must be between 0% and 20%."
            )

    # ---------------------------------------------------------
    # Blood pressure
    # ---------------------------------------------------------

    systolic = data.get("systolic_bp")
    diastolic = data.get("diastolic_bp")

    if systolic is not None:
        if systolic < 50 or systolic > 300:
            errors.append(
                "Systolic blood pressure must be between 50 and 300 mmHg."
            )

    if diastolic is not None:
        if diastolic < 30 or diastolic > 200:
            errors.append(
                "Diastolic blood pressure must be between 30 and 200 mmHg."
            )

    # ---------------------------------------------------------
    # Blood pressure consistency
    # ---------------------------------------------------------

    if systolic is not None and diastolic is not None:

        if diastolic >= systolic:
            errors.append(
                "Diastolic blood pressure should be lower than systolic "
                "blood pressure. Please verify the values."
            )

    # ---------------------------------------------------------
    # Family history
    # ---------------------------------------------------------

    if data.get("family_history") == "Unknown":
        warnings.append(
            "Family history is unknown. This information may be useful "
            "for a more complete assessment."
        )

    # ---------------------------------------------------------
    # Lifestyle information
    # ---------------------------------------------------------

    if data.get("physical_activity") == "Unknown":
        warnings.append(
            "Physical activity information is unavailable."
        )

    # ---------------------------------------------------------
    # Medication information
    # ---------------------------------------------------------

    medications = data.get("medications", "").strip()

    if not medications:
        warnings.append(
            "No current medications were provided."
        )

    # ---------------------------------------------------------
    # Medical history
    # ---------------------------------------------------------

    medical_history = data.get("medical_history", "").strip()

    if not medical_history:
        warnings.append(
            "No previous medical conditions were provided."
        )

    # ---------------------------------------------------------
    # Validation result
    # ---------------------------------------------------------

    is_valid = len(errors) == 0

    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "calculated_bmi": bmi,
    }