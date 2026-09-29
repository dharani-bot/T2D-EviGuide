from typing import Dict, List, Any


def validate_patient_data(
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Performs basic clinical data-quality validation.

    This function checks whether entered values are:
    - present where required
    - within reasonable input boundaries
    - internally consistent
    - sufficiently described for downstream assessment

    It does NOT diagnose disease or determine medical risk.
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
        "blood_glucose": "Blood glucose",
        "fasting_status": "Glucose measurement status",
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
    # AGE VALIDATION
    # =========================================================

    age = data.get("age")

    if age is not None:

        try:

            age = float(age)

            if age < 1 or age > 120:

                errors.append(
                    "Age must be between 1 and 120 years."
                )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                "Age must be a valid number."
            )


    # =========================================================
    # HEIGHT VALIDATION
    # =========================================================

    height = data.get("height")

    if height is not None:

        try:

            height = float(height)

            if height < 50 or height > 250:

                errors.append(
                    "Height must be between 50 and 250 cm."
                )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                "Height must be a valid number."
            )


    # =========================================================
    # WEIGHT VALIDATION
    # =========================================================

    weight = data.get("weight")

    if weight is not None:

        try:

            weight = float(weight)

            if weight <= 0 or weight > 300:

                errors.append(
                    "Weight must be greater than 0 "
                    "and no more than 300 kg."
                )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                "Weight must be a valid number."
            )


    # =========================================================
    # BMI CALCULATION
    # =========================================================

    bmi = None

    if (
        height is not None
        and weight is not None
    ):

        try:

            height_m = float(height) / 100
            weight_value = float(weight)

            if height_m > 0:

                bmi = round(
                    weight_value
                    / (height_m ** 2),
                    1
                )

                if bmi < 10 or bmi > 100:

                    warnings.append(
                        "The calculated BMI is outside "
                        "the expected range. Please verify "
                        "height and weight."
                    )

        except (
            TypeError,
            ValueError,
            ZeroDivisionError
        ):

            pass


    # =========================================================
    # BLOOD GLUCOSE
    # =========================================================

    glucose = data.get(
        "blood_glucose"
    )

    if glucose is not None:

        try:

            glucose = float(glucose)

            if glucose < 0 or glucose > 600:

                errors.append(
                    "Blood glucose must be between "
                    "0 and 600 mg/dL."
                )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                "Blood glucose must be a valid number."
            )


    # =========================================================
    # GLUCOSE MEASUREMENT STATUS
    # =========================================================

    fasting_status = data.get(
        "fasting_status"
    )

    allowed_glucose_statuses = [
        "Fasting",
        "Random",
        "Non-fasting",
        "2-hour OGTT",
        "Unknown"
    ]

    if fasting_status not in allowed_glucose_statuses:

        errors.append(
            "Glucose measurement status must be "
            "Fasting, Random, Non-fasting, "
            "2-hour OGTT, or Unknown."
        )


    if fasting_status == "Unknown":

        warnings.append(
            "Glucose measurement status is unknown. "
            "The glucose value should not be interpreted "
            "using a fasting-specific threshold."
        )


    # =========================================================
    # HbA1c
    # =========================================================

    hba1c = data.get(
        "hba1c"
    )

    if hba1c is not None:

        try:

            hba1c = float(hba1c)

            if hba1c < 0 or hba1c > 20:

                errors.append(
                    "HbA1c must be between 0% and 20%."
                )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                "HbA1c must be a valid number."
            )


    # =========================================================
    # TOTAL CHOLESTEROL
    # =========================================================

    cholesterol = data.get(
        "total_cholesterol"
    )

    if cholesterol is not None:

        try:

            cholesterol = float(
                cholesterol
            )

            if cholesterol < 0 or cholesterol > 1000:

                errors.append(
                    "Total cholesterol must be between "
                    "0 and 1000 mg/dL."
                )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                "Total cholesterol must be a valid number."
            )


    # =========================================================
    # BLOOD PRESSURE
    # =========================================================

    systolic = data.get(
        "systolic_bp"
    )

    diastolic = data.get(
        "diastolic_bp"
    )


    if systolic is not None:

        try:

            systolic = float(
                systolic
            )

            if systolic < 50 or systolic > 300:

                errors.append(
                    "Systolic blood pressure must be "
                    "between 50 and 300 mmHg."
                )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                "Systolic blood pressure must be "
                "a valid number."
            )


    if diastolic is not None:

        try:

            diastolic = float(
                diastolic
            )

            if diastolic < 30 or diastolic > 200:

                errors.append(
                    "Diastolic blood pressure must be "
                    "between 30 and 200 mmHg."
                )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                "Diastolic blood pressure must be "
                "a valid number."
            )


    # =========================================================
    # BLOOD PRESSURE CONSISTENCY
    # =========================================================

    if (
        systolic is not None
        and diastolic is not None
    ):

        try:

            if float(diastolic) >= float(systolic):

                errors.append(
                    "Diastolic blood pressure should be "
                    "lower than systolic blood pressure. "
                    "Please verify the values."
                )

        except (
            TypeError,
            ValueError
        ):

            pass


    # =========================================================
    # FAMILY HISTORY
    # =========================================================

    family_history = data.get(
        "family_history"
    )

    allowed_family_history = [
        "Yes",
        "No",
        "Unknown"
    ]

    if family_history not in allowed_family_history:

        errors.append(
            "Family history must be Yes, No, or Unknown."
        )

    elif family_history == "Unknown":

        warnings.append(
            "Family history is unknown. This information "
            "may be useful for a more complete assessment."
        )


    # =========================================================
    # PHYSICAL ACTIVITY
    # =========================================================

    physical_activity = data.get(
        "physical_activity"
    )

    allowed_activity = [
        "Low",
        "Moderate",
        "High",
        "Unknown"
    ]

    if physical_activity not in allowed_activity:

        errors.append(
            "Physical activity must be Low, Moderate, "
            "High, or Unknown."
        )

    elif physical_activity == "Unknown":

        warnings.append(
            "Physical activity information is unavailable."
        )


    # =========================================================
    # SMOKING
    # =========================================================

    smoking = data.get(
        "smoking"
    )

    allowed_smoking = [
        "Never",
        "Former",
        "Current",
        "Unknown"
    ]

    if smoking not in allowed_smoking:

        errors.append(
            "Smoking status must be Never, Former, "
            "Current, or Unknown."
        )

    elif smoking == "Unknown":

        warnings.append(
            "Smoking status is unknown."
        )


    # =========================================================
    # DIETARY INTAKE
    # =========================================================

    dietary_intake = data.get(
        "dietary_intake",
        {}
    )


    if dietary_intake is None:

        dietary_intake = {}


    if not isinstance(
        dietary_intake,
        dict
    ):

        errors.append(
            "Dietary intake information must be "
            "stored as structured data."
        )

        dietary_intake = {}


    # ---------------------------------------------------------
    # Dietary variables
    # ---------------------------------------------------------

    dietary_fields = {

        "meal_pattern": "Meal pattern",

        "fruit_vegetable_intake":
            "Fruit and vegetable intake",

        "whole_grain_intake":
            "Whole-grain intake",

        "sugary_beverage_intake":
            "Sugary beverage intake",

        "processed_food_intake":
            "Processed food intake",

        "added_sugar_intake":
            "Added sugar intake",
    }


    allowed_dietary_levels = [
        "Low",
        "Moderate",
        "High",
        "None",
        "Unknown"
    ]


    for field, label in dietary_fields.items():

        value = dietary_intake.get(
            field
        )

        if value is None or value == "":

            warnings.append(
                f"{label} information is unavailable."
            )

        elif (
            field != "meal_pattern"
            and value not in allowed_dietary_levels
        ):

            errors.append(
                f"{label} contains an invalid category."
            )


    # ---------------------------------------------------------
    # Free-text dietary information
    # ---------------------------------------------------------

    dietary_pattern = dietary_intake.get(
        "dietary_pattern",
        ""
    )

    other_dietary_information = dietary_intake.get(
        "other_information",
        ""
    )


    if not str(
        dietary_pattern
    ).strip():

        warnings.append(
            "No dietary pattern description was provided."
        )


    # =========================================================
    # MEDICAL HISTORY
    # =========================================================

    medical_history = data.get(
        "medical_history",
        ""
    )


    if not str(
        medical_history
    ).strip():

        warnings.append(
            "No previous medical conditions were provided."
        )


    # =========================================================
    # MEDICATION INFORMATION
    # =========================================================

    medications = data.get(
        "medications",
        ""
    )


    if not str(
        medications
    ).strip():

        warnings.append(
            "No current medications were provided."
        )


    # =========================================================
    # DATA COMPLETENESS
    # =========================================================

    tracked_fields = [
        "age",
        "sex",
        "weight",
        "height",
        "blood_glucose",
        "fasting_status",
        "hba1c",
        "systolic_bp",
        "diastolic_bp",
        "family_history",
        "physical_activity",
        "smoking",
        "medical_history",
        "medications",
    ]


    available_count = 0


    for field in tracked_fields:

        value = data.get(
            field
        )

        if (
            value is not None
            and str(value).strip() != ""
            and str(value).strip().lower()
            != "unknown"
        ):

            available_count += 1


    # Dietary information is assessed separately because
    # several dietary fields can be independently missing.

    dietary_fields_present = 0

    for field in dietary_fields:

        value = dietary_intake.get(
            field
        )

        if (
            value is not None
            and str(value).strip() != ""
            and str(value).strip().lower()
            != "unknown"
        ):

            dietary_fields_present += 1


    total_tracked_fields = (
        len(tracked_fields)
        + len(dietary_fields)
    )


    total_available_fields = (
        available_count
        + dietary_fields_present
    )


    completeness_percentage = round(
        (
            total_available_fields
            / total_tracked_fields
        ) * 100,
        1
    )


    # =========================================================
    # FINAL VALIDATION STATUS
    # =========================================================

    is_valid = (
        len(errors) == 0
    )


    return {

        "is_valid": is_valid,

        "errors": errors,

        "warnings": warnings,

        "calculated_bmi": bmi,

        "data_completeness": (
            completeness_percentage
        ),

        "available_fields": (
            total_available_fields
        ),

        "total_tracked_fields": (
            total_tracked_fields
        ),

        "dietary_fields_available": (
            dietary_fields_present
        ),

    }