from typing import Dict, List, Any


def validate_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    T2D-EviGuide Clinical Data Validation Module.

    Performs data-quality checks before an AI assessment.

    Checks:
    - Required fields
    - Numeric data types
    - Clinically reasonable input boundaries
    - BMI calculation
    - Blood pressure consistency
    - Missing clinical information
    - Lifestyle and dietary information
    - Uploaded document availability

    This module does NOT diagnose diabetes,
    calculate disease probabilities, or determine
    clinical risk independently.
    """

    errors: List[str] = []
    warnings: List[str] = []

    # =========================================================
    # HELPER FUNCTIONS
    # =========================================================

    def get_numeric_value(field):
        """
        Safely retrieve numeric values.
        Returns None for missing or invalid values.
        """

        value = data.get(field)

        if value is None or value == "":
            return None

        try:
            return float(value)

        except (TypeError, ValueError):
            errors.append(
                f"{field.replace('_', ' ').capitalize()} "
                "must contain a valid numeric value."
            )
            return None

    # =========================================================
    # REQUIRED FIELDS
    # =========================================================

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

            errors.append(
                f"{label} is required."
            )

    # =========================================================
    # NUMERIC FIELD EXTRACTION
    # =========================================================

    age = get_numeric_value("age")
    height = get_numeric_value("height")
    weight = get_numeric_value("weight")

    waist = get_numeric_value("waist_circumference")

    glucose = get_numeric_value("fasting_glucose")
    hba1c = get_numeric_value("hba1c")

    total_cholesterol = get_numeric_value(
        "total_cholesterol"
    )

    hdl = get_numeric_value("hdl")
    ldl = get_numeric_value("ldl")

    triglycerides = get_numeric_value(
        "triglycerides"
    )

    systolic = get_numeric_value("systolic_bp")
    diastolic = get_numeric_value("diastolic_bp")

    activity_duration = get_numeric_value(
        "activity_duration"
    )

    sedentary_hours = get_numeric_value(
        "sedentary_hours"
    )

    sleep_duration = get_numeric_value(
        "sleep_duration"
    )

    # =========================================================
    # AGE VALIDATION
    # =========================================================

    if age is not None:

        if not age.is_integer():

            errors.append(
                "Age must be a whole number."
            )

        if age < 1 or age > 120:

            errors.append(
                "Age must be between 1 and 120 years."
            )

    # =========================================================
    # HEIGHT VALIDATION
    # =========================================================

    if height is not None:

        if height < 50 or height > 250:

            errors.append(
                "Height must be between 50 and 250 cm."
            )

    # =========================================================
    # WEIGHT VALIDATION
    # =========================================================

    if weight is not None:

        if weight <= 0 or weight > 300:

            errors.append(
                "Weight must be greater than 0 "
                "and no more than 300 kg."
            )

    # =========================================================
    # BMI CALCULATION
    # =========================================================

    calculated_bmi = None

    if (
        height is not None
        and weight is not None
        and height > 0
        and weight > 0
        and height <= 250
        and height >= 50
        and weight <= 300
    ):

        height_m = height / 100

        calculated_bmi = round(
            weight / (height_m ** 2),
            2
        )

        if calculated_bmi < 10 or calculated_bmi > 100:

            warnings.append(
                "Calculated BMI is outside the expected "
                "range. Please verify height and weight."
            )

    # =========================================================
    # WAIST CIRCUMFERENCE
    # =========================================================

    if waist is not None:

        if waist < 30 or waist > 250:

            errors.append(
                "Waist circumference must be between "
                "30 and 250 cm."
            )

    # =========================================================
    # FASTING GLUCOSE
    # =========================================================

    if glucose is not None:

        if glucose < 0 or glucose > 600:

            errors.append(
                "Fasting blood glucose must be between "
                "0 and 600 mg/dL."
            )

    # =========================================================
    # HbA1c
    # =========================================================

    if hba1c is not None:

        if hba1c < 0 or hba1c > 20:

            errors.append(
                "HbA1c must be between 0% and 20%."
            )

    # =========================================================
    # LIPID PROFILE
    # =========================================================

    lipid_fields = {
        "total_cholesterol": (
            "Total cholesterol",
            0,
            1000,
            "mg/dL"
        ),

        "hdl": (
            "HDL cholesterol",
            0,
            500,
            "mg/dL"
        ),

        "ldl": (
            "LDL cholesterol",
            0,
            1000,
            "mg/dL"
        ),

        "triglycerides": (
            "Triglycerides",
            0,
            2000,
            "mg/dL"
        ),
    }

    lipid_values = {
        "total_cholesterol": total_cholesterol,
        "hdl": hdl,
        "ldl": ldl,
        "triglycerides": triglycerides,
    }

    for field, details in lipid_fields.items():

        label, minimum, maximum, unit = details

        value = lipid_values[field]

        if value is not None:

            if value < minimum or value > maximum:

                errors.append(
                    f"{label} must be between "
                    f"{minimum} and {maximum} {unit}."
                )

    # =========================================================
    # BLOOD PRESSURE
    # =========================================================

    if systolic is not None:

        if systolic < 50 or systolic > 300:

            errors.append(
                "Systolic blood pressure must be between "
                "50 and 300 mmHg."
            )

    if diastolic is not None:

        if diastolic < 30 or diastolic > 200:

            errors.append(
                "Diastolic blood pressure must be between "
                "30 and 200 mmHg."
            )

    # =========================================================
    # BLOOD PRESSURE CONSISTENCY
    # =========================================================

    if (
        systolic is not None
        and diastolic is not None
        and 50 <= systolic <= 300
        and 30 <= diastolic <= 200
    ):

        if diastolic >= systolic:

            errors.append(
                "Diastolic blood pressure should be lower "
                "than systolic blood pressure. "
                "Please verify the values."
            )

    # =========================================================
    # PHYSICAL ACTIVITY DURATION
    # =========================================================

    if activity_duration is not None:

        if activity_duration < 0 or activity_duration > 600:

            errors.append(
                "Physical activity duration must be "
                "between 0 and 600 minutes."
            )

    # =========================================================
    # SEDENTARY TIME
    # =========================================================

    if sedentary_hours is not None:

        if sedentary_hours < 0 or sedentary_hours > 24:

            errors.append(
                "Sedentary time must be between "
                "0 and 24 hours per day."
            )

    # =========================================================
    # SLEEP DURATION
    # =========================================================

    if sleep_duration is not None:

        if sleep_duration < 0 or sleep_duration > 24:

            errors.append(
                "Sleep duration must be between "
                "0 and 24 hours per day."
            )

    # =========================================================
    # FAMILY HISTORY
    # =========================================================

    if data.get("family_history") in (
        None,
        "",
        "Unknown"
    ):

        warnings.append(
            "Family history of diabetes is unknown "
            "or unavailable."
        )

    # =========================================================
    # PHYSICAL ACTIVITY INFORMATION
    # =========================================================

    if data.get("physical_activity") in (
        None,
        "",
        "Unknown"
    ):

        warnings.append(
            "Physical activity information is unavailable."
        )

    # =========================================================
    # DIETARY INFORMATION
    # =========================================================

    dietary_fields = {

        "fruit_vegetable_intake":
            "Fruit and vegetable intake",

        "whole_grain_intake":
            "Whole grain intake",

        "sugary_drinks":
            "Sugary beverage consumption",

        "sweets_added_sugar":
            "Sweets and added sugar consumption",

        "fried_food":
            "Fried/high-fat food consumption",

        "processed_food":
            "Processed/packaged food consumption",

    }

    for field, label in dietary_fields.items():

        value = data.get(field)

        if value in (None, "", "Unknown"):

            warnings.append(
                f"{label} information is unavailable."
            )

    # =========================================================
    # SMOKING
    # =========================================================

    if data.get("smoking") in (
        None,
        "",
        "Unknown"
    ):

        warnings.append(
            "Smoking status is unavailable."
        )

    # =========================================================
    # ALCOHOL
    # =========================================================

    if data.get("alcohol") in (
        None,
        "",
        "Unknown"
    ):

        warnings.append(
            "Alcohol consumption information is unavailable."
        )

    # =========================================================
    # MEDICAL HISTORY
    # =========================================================

    medical_history = data.get(
        "medical_history",
        ""
    )

    if (
        not isinstance(medical_history, str)
        or not medical_history.strip()
    ):

        warnings.append(
            "No additional medical history was provided."
        )

    # =========================================================
    # MEDICATIONS
    # =========================================================

    medications = data.get(
        "medications",
        ""
    )

    if (
        not isinstance(medications, str)
        or not medications.strip()
    ):

        warnings.append(
            "No current medications were provided."
        )

    # =========================================================
    # ADDITIONAL NOTES
    # =========================================================

    additional_notes = data.get(
        "additional_notes",
        ""
    )

    if not isinstance(additional_notes, str):

        errors.append(
            "Additional clinical notes must be text."
        )

    # =========================================================
    # DOCUMENT UPLOAD INFORMATION
    # =========================================================

    uploaded_reports = data.get(
        "uploaded_reports"
    )

    if not uploaded_reports:

        warnings.append(
            "No medical report or clinical document "
            "was uploaded."
        )

    # =========================================================
    # FINAL VALIDATION RESULT
    # =========================================================

    is_valid = len(errors) == 0

    return {

        "is_valid": is_valid,

        "errors": errors,

        "warnings": warnings,

        "calculated_bmi": calculated_bmi,

    }