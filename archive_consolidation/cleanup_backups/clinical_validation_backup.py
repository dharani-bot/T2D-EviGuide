from typing import Dict, List, Any


def validate_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs data-quality validation for the T2D-EviGuide
    patient assessment form.

    This function checks:
    - required fields
    - reasonable numerical boundaries
    - internal consistency
    - selected categorical values
    - availability of important clinical information

    It does NOT diagnose disease or independently determine
    diabetes risk.
    """

    errors: List[str] = []
    warnings: List[str] = []

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
            errors.append(f"{label} is required.")

    # =========================================================
    # AGE
    # =========================================================

    age = data.get("age")

    if age is not None:

        if age < 1 or age > 120:
            errors.append(
                "Age must be between 1 and 120 years."
            )

    # =========================================================
    # HEIGHT
    # =========================================================

    height = data.get("height")

    if height is not None:

        if height < 50 or height > 250:
            errors.append(
                "Height must be between 50 and 250 cm."
            )

    # =========================================================
    # WEIGHT
    # =========================================================

    weight = data.get("weight")

    if weight is not None:

        if weight <= 0 or weight > 300:
            errors.append(
                "Weight must be greater than 0 and no more than 300 kg."
            )

    # =========================================================
    # BMI
    # =========================================================

    bmi = None

    if (
        height is not None
        and weight is not None
        and height > 0
    ):

        height_m = height / 100

        bmi = weight / (height_m ** 2)

        if bmi < 10 or bmi > 100:

            warnings.append(
                "The calculated BMI is outside the expected "
                "range. Please verify height and weight."
            )

    # =========================================================
    # WAIST CIRCUMFERENCE
    # =========================================================

    waist = data.get("waist_circumference")

    if waist is not None:

        if waist != "" and (
            waist < 30 or waist > 250
        ):

            errors.append(
                "Waist circumference must be between "
                "30 and 250 cm."
            )

    # =========================================================
    # FASTING GLUCOSE
    # =========================================================

    glucose = data.get("fasting_glucose")

    if glucose is not None:

        if glucose < 0 or glucose > 600:

            errors.append(
                "Fasting blood glucose must be between "
                "0 and 600 mg/dL."
            )

    # =========================================================
    # HbA1c
    # =========================================================

    hba1c = data.get("hba1c")

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

    for field, details in lipid_fields.items():

        label, minimum, maximum, unit = details

        value = data.get(field)

        if value is not None:

            if value != "" and (
                value < minimum or value > maximum
            ):

                errors.append(
                    f"{label} must be between "
                    f"{minimum} and {maximum} {unit}."
                )

    # =========================================================
    # BLOOD PRESSURE
    # =========================================================

    systolic = data.get("systolic_bp")
    diastolic = data.get("diastolic_bp")

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

    activity_duration = data.get(
        "activity_duration"
    )

    if activity_duration is not None:

        if activity_duration != "" and (
            activity_duration < 0
            or activity_duration > 600
        ):

            errors.append(
                "Physical activity duration must be "
                "between 0 and 600 minutes."
            )

    # =========================================================
    # SEDENTARY TIME
    # =========================================================

    sedentary_hours = data.get(
        "sedentary_hours"
    )

    if sedentary_hours is not None:

        if sedentary_hours != "" and (
            sedentary_hours < 0
            or sedentary_hours > 24
        ):

            errors.append(
                "Sedentary time must be between "
                "0 and 24 hours per day."
            )

    # =========================================================
    # SLEEP
    # =========================================================

    sleep_duration = data.get(
        "sleep_duration"
    )

    if sleep_duration is not None:

        if sleep_duration != "" and (
            sleep_duration < 0
            or sleep_duration > 24
        ):

            errors.append(
                "Sleep duration must be between "
                "0 and 24 hours per day."
            )

    # =========================================================
    # FAMILY HISTORY
    # =========================================================

    if data.get("family_history") == "Unknown":

        warnings.append(
            "Family history of diabetes is unknown. "
            "This information may be useful for a more "
            "complete assessment."
        )

    # =========================================================
    # PHYSICAL ACTIVITY
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

    smoking = data.get("smoking")

    if smoking in (
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

    alcohol = data.get("alcohol")

    if alcohol in (
        None,
        "",
        "Unknown"
    ):

        warnings.append(
            "Alcohol consumption information "
            "is unavailable."
        )

    # =========================================================
    # MEDICAL HISTORY
    # =========================================================

    medical_history = data.get(
        "medical_history",
        ""
    )

    if isinstance(
        medical_history,
        str
    ):

        if not medical_history.strip():

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

    if isinstance(
        medications,
        str
    ):

        if not medications.strip():

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

    if not isinstance(
        additional_notes,
        str
    ):

        errors.append(
            "Additional clinical notes must be text."
        )

    # =========================================================
    # REPORT / DOCUMENT INFORMATION
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
    # FINAL RESULT
    # =========================================================

    is_valid = len(errors) == 0

    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "calculated_bmi": bmi,
    }