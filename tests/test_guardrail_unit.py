import unittest

from clinical_guardrails import check_clinical_guardrails
from clinical_guardrails_v2 import check_clinical_guardrails_v2


class TestClinicalGuardrails(unittest.TestCase):

    def test_detects_hba1c_igt_terminology(self):
        result = check_clinical_guardrails(
            "HbA1c indicates impaired glucose tolerance."
        )
        self.assertTrue(result["hba1c_igt"])

    def test_detects_inpatient_fasting_claim(self):
        result = check_clinical_guardrails(
            "The inpatient fasting glucose was reviewed."
        )
        self.assertTrue(result["fasting"])

    def test_detects_threshold_language(self):
        result = check_clinical_guardrails(
            "The result is above the threshold."
        )
        self.assertTrue(result["threshold"])

    def test_detects_diagnostic_overreach(self):
        result = check_clinical_guardrails(
            "This confirms diabetes."
        )
        self.assertTrue(result["diagnostic_language"])


class TestClinicalGuardrailsV2(unittest.TestCase):

    def setUp(self):
        self.patient_data = {
            "hba1c": 7.1,
            "blood_glucose": 206.0,
            "fasting_glucose": None,
            "ogtt_2h_glucose": None,
            "glucose_measurement_type": "inpatient",
        }

    def test_detects_hba1c_igt_terminology(self):
        result = check_clinical_guardrails_v2(
            "HbA1c indicates impaired glucose tolerance.",
            self.patient_data,
        )
        self.assertTrue(result["hba1c_igt"])

    def test_detects_unconfirmed_fasting_value(self):
        result = check_clinical_guardrails_v2(
            "Fasting glucose was 110 mg/dL.",
            self.patient_data,
        )
        self.assertTrue(result["fasting"])

    def test_detects_inappropriate_threshold_application(self):
        result = check_clinical_guardrails_v2(
            "The inpatient glucose exceeds the fasting threshold.",
            self.patient_data,
        )
        self.assertTrue(result["threshold"])

    def test_detects_diagnostic_overreach(self):
        result = check_clinical_guardrails_v2(
            "This confirms diabetes.",
            self.patient_data,
        )
        self.assertTrue(result["diagnostic_language"])

    def test_accepts_explicit_measurement_limitation(self):
        result = check_clinical_guardrails_v2(
            "Fasting status is unknown. These findings do not "
            "establish a diagnosis.",
            self.patient_data,
        )
        self.assertFalse(result["fasting"])
        self.assertFalse(result["diagnostic_language"])
        self.assertFalse(result["threshold"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
