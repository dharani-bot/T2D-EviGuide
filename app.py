
import streamlit as st
from datetime import datetime

# ============================================================
# DiaEvidence AI
# Evidence-Grounded Type 2 Diabetes Risk Assessment
# Academic research prototype — not a diagnostic system
# ============================================================

st.set_page_config(
    page_title="DiaEvidence AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------- BACKEND IMPORTS ---------------------

try:
    from clinical_assessment import run_clinical_assessment
    ASSESSMENT_IMPORT_ERROR = None
except Exception as exc:
    run_clinical_assessment = None
    ASSESSMENT_IMPORT_ERROR = str(exc)

try:
    from medical_report_parser import parse_uploaded_report
    PARSER_IMPORT_ERROR = None
except Exception as exc:
    parse_uploaded_report = None
    PARSER_IMPORT_ERROR = str(exc)

# ----------------------- SESSION STATE -----------------------

DEFAULTS = {
    "workflow_stage": "Patient",
    "patient": {},
    "assessment_result": None,
    "parsed_report": None,
    "report_signature": None,
    "literature_sources": [],
    "evaluation_checks": {},
}

for key, default in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default

STAGES = [
    ("Patient", "👤 Patient"),
    ("Report", "📄 Report"),
    ("Validate", "🧪 Validate"),
    ("Retrieve", "🔎 Retrieve"),
    ("Synthesize", "🧠 Synthesize"),
    ("Verify", "🛡️ Verify"),
]

FIELD_LABELS = {
    "age": "Age",
    "sex": "Sex",
    "family_history": "Family history of diabetes",
    "hba1c": "HbA1c (%)",
    "fasting_glucose": "Fasting glucose (mg/dL)",
    "blood_glucose": "Blood glucose (mg/dL)",
    "systolic_bp": "Systolic blood pressure (mmHg)",
    "diastolic_bp": "Diastolic blood pressure (mmHg)",
    "total_cholesterol": "Total cholesterol (mg/dL)",
}

IMPORTABLE_FIELDS = {
    "age",
    "hba1c",
    "fasting_glucose",
    "blood_glucose",
    "systolic_bp",
    "diastolic_bp",
    "total_cholesterol",
    "height_cm",
    "weight_kg",
    "bmi",
}

# ----------------------------- CSS ---------------------------

st.markdown(
    """
    <style>
    /* =========================================================
       DiaEvidence AI — refined dark clinical theme
       Navy canvas, blue-gray surfaces, restrained teal accents
       ========================================================= */

    :root {
        color-scheme: dark;
        --dia-bg: #08131f;
        --dia-surface: #101f2e;
        --dia-surface-2: #142638;
        --dia-border: #263d50;
        --dia-text: #edf5fb;
        --dia-muted: #b1c1d0;
        --dia-teal: #20d2c4;
        --dia-teal-dark: #0c8f8b;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: var(--dia-bg) !important;
        color: var(--dia-text) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(8, 19, 31, 0.94) !important;
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    label, .stCaption {
        color: var(--dia-text);
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] {
        line-height: 1.65;
    }

    [data-testid="stCaptionContainer"],
    .stCaption {
        color: var(--dia-muted) !important;
    }

    /* Brand hero */
    .hero {
        background: linear-gradient(115deg, #102337 0%, #12384a 62%, #10504f 100%);
        color: var(--dia-text);
        padding: 27px 30px;
        border: 1px solid #29485b;
        border-radius: 18px;
        margin-bottom: 20px;
        width: 100%;
        box-sizing: border-box;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.16);
    }

    .hero-title {
        color: #f4fbff;
        font-size: 2.25rem;
        font-weight: 760;
        line-height: 1.25;
        letter-spacing: -0.035em;
        margin-bottom: 10px;
    }

    .hero p {
        color: #d2e4ee;
        font-size: 1rem;
        line-height: 1.6;
        margin: 6px 0;
    }

    .hero p:last-child {
        color: #9fc5d1;
        font-size: 0.9rem;
    }

    /* Sticky workflow bar remains in document flow and does not cover fields */
    .st-key-workflow_bar {
        position: sticky !important;
        top: 0.25rem !important;
        z-index: 99 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        background: rgba(8, 19, 31, 0.97) !important;
        backdrop-filter: blur(12px);
        padding: 12px 10px !important;
        margin: 10px 0 24px 0 !important;
        border: 1px solid #20394b !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
    }

    .st-key-workflow_bar [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        align-items: stretch !important;
    }

    .st-key-workflow_bar [data-testid="column"] {
        min-width: 0 !important;
    }

    .st-key-workflow_bar button {
        width: 100% !important;
        min-height: 46px !important;
        padding: 8px 4px !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 650 !important;
        white-space: normal !important;
        line-height: 1.3 !important;
        transition: border-color 0.15s ease, background 0.15s ease;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0b1927 !important;
        border-right: 1px solid #203548;
    }

    section[data-testid="stSidebar"] > div {
        background: #0b1927 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] label {
        color: #d9e7f1 !important;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 9px;
        padding: 0.35rem 0.5rem;
    }

    /* Inputs and selection controls */
    input, textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: var(--dia-text) !important;
        caret-color: var(--dia-teal) !important;
    }

    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    [data-baseweb="select"] > div,
    [data-testid="stNumberInput"] [data-baseweb="input"] > div {
        background: #102132 !important;
        border-color: #344c60 !important;
        border-radius: 10px !important;
    }

    [data-baseweb="select"] *,
    [data-baseweb="popover"] *,
    [role="listbox"] * {
        color: var(--dia-text);
    }

    [data-baseweb="input"] > div:focus-within,
    [data-baseweb="textarea"] > div:focus-within,
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--dia-teal) !important;
        box-shadow: 0 0 0 1px var(--dia-teal) !important;
    }

    [data-testid="stFileUploader"] section {
        background: #0e1d2b !important;
        border: 1px dashed #3a596b !important;
        border-radius: 12px !important;
    }

    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span {
        color: var(--dia-muted);
    }

    /* Buttons */
    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        border-radius: 10px !important;
        font-weight: 650 !important;
        min-height: 2.55rem;
        transition: all 0.15s ease-in-out;
    }

    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stFormSubmitButton"] button[kind="primary"] {
        background: linear-gradient(100deg, #0daea8, #20d2c4) !important;
        color: #04151c !important;
        border: 1px solid #20d2c4 !important;
    }

    div[data-testid="stButton"] button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
        background: #35e1d3 !important;
        border-color: #35e1d3 !important;
        box-shadow: 0 5px 16px rgba(32, 210, 196, 0.17);
    }

    div[data-testid="stButton"] button[kind="secondary"],
    div[data-testid="stFormSubmitButton"] button[kind="secondary"] {
        background: #142638 !important;
        color: #e5f0f7 !important;
        border: 1px solid #344c60 !important;
    }

    div[data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: var(--dia-teal) !important;
        color: #ffffff !important;
    }

    /* Forms, metrics, expanders and tables */
    div[data-testid="stForm"],
    div[data-testid="stMetric"],
    [data-testid="stExpander"] {
        background: var(--dia-surface) !important;
        border: 1px solid var(--dia-border) !important;
        border-radius: 13px !important;
    }

    div[data-testid="stForm"] {
        padding: 18px !important;
    }

    div[data-testid="stMetric"] {
        padding: 15px !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--dia-muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--dia-text) !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--dia-border);
        border-radius: 10px;
        overflow: hidden;
    }

    [data-testid="stDataFrame"] *,
    [data-testid="stTable"] * {
        color: var(--dia-text);
    }

    /* Alerts: muted surfaces, accessible contrast */
    div[data-testid="stAlert"] {
        border-radius: 11px !important;
        border: 1px solid #344b5d;
    }

    [data-testid="stAlert"] p {
        color: inherit !important;
    }

    hr {
        border-color: #263b4d !important;
    }

    /* Responsive layouts */
    @media (max-width: 1100px) {
        .hero {
            padding: 22px;
        }

        .hero-title {
            font-size: 1.9rem;
        }

        .st-key-workflow_bar {
            top: 0.2rem !important;
            padding: 8px 6px !important;
        }

        .st-key-workflow_bar [data-testid="stHorizontalBlock"] {
            gap: 4px !important;
        }

        .st-key-workflow_bar button {
            font-size: 0.7rem !important;
            min-height: 48px !important;
            padding: 5px 2px !important;
        }
    }

    @media (max-width: 650px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .hero {
            padding: 18px;
            border-radius: 13px;
        }

        .hero-title {
            font-size: 1.55rem;
        }

        .hero p {
            font-size: 0.88rem;
        }

        .st-key-workflow_bar {
            margin-bottom: 18px !important;
            padding: 6px 3px !important;
        }

        .st-key-workflow_bar [data-testid="stHorizontalBlock"] {
            gap: 2px !important;
        }

        .st-key-workflow_bar button {
            font-size: 0.58rem !important;
            min-height: 50px !important;
            padding: 3px 1px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------- HELPERS ------------------------

def go_to_stage(stage):
    st.session_state.workflow_stage = stage
    st.rerun()


def is_missing(value):
    return value is None or value == ""


def get_missing_fields():
    patient = st.session_state.patient
    missing = []

    for key, label in FIELD_LABELS.items():
        value = patient.get(key)

        if is_missing(value):
            missing.append(label)

    return missing


def display_value(value):
    if value is None or value == "":
        return "Not provided"
    return str(value)


def display_data(value):
    if isinstance(value, (dict, list, tuple)):
        st.json(value)
    else:
        st.write(value)


def normalize_key(key):
    key = str(key).strip().lower()
    key = key.replace(" ", "_").replace("-", "_")

    aliases = {
        "hb_a1c": "hba1c",
        "hba1c_percent": "hba1c",
        "glucose_fasting": "fasting_glucose",
        "fasting_blood_glucose": "fasting_glucose",
        "systolic": "systolic_bp",
        "diastolic": "diastolic_bp",
        "cholesterol": "total_cholesterol",
    }

    return aliases.get(key, key)


def extract_report_values(parsed):
    """Extract candidate numeric values from common parser outputs."""
    if not isinstance(parsed, dict):
        return {}

    source = parsed.get("data")

    if not isinstance(source, dict):
        source = parsed.get("values")

    if not isinstance(source, dict):
        source = parsed

    values = {}

    for key, value in source.items():
        normalized = normalize_key(key)

        if normalized not in IMPORTABLE_FIELDS:
            continue

        if isinstance(value, (int, float)):
            values[normalized] = value

    return values


# ------------------------- DASHBOARD HEADER ------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🩺 DiaEvidence AI</div>
        <p><b>Evidence-Grounded Type 2 Diabetes Risk Assessment</b></p>
        <p>
            🧬 Multimodal Clinical Data
            &nbsp; · &nbsp; 🔎 Evidence Retrieval
            &nbsp; · &nbsp; 🧠 AI Synthesis
            &nbsp; · &nbsp; 🛡️ Verification
        </p>
        <p>Academic Research Prototype | Clinician Review Required</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "⚕️ This academic prototype does not diagnose diabetes or provide "
    "a validated prediction of future diabetes. Outputs require "
    "appropriate clinical review."
)

# ----------------------- SIDEBAR NAVIGATION ------------------

with st.sidebar:
    st.title("🩺 DiaEvidence AI")

    page = st.radio(
        "Navigate",
        [
            "🏥 Assessment",
            "📚 Evidence Explorer",
            "📊 Evaluation",
            "📖 Literature",
            "ℹ️ About",
        ],
        key="main_navigation",
    )

# ============================================================
# WORKFLOW NAVIGATION
# ============================================================

def workflow_bar():
    with st.container(key="workflow_bar"):
        columns = st.columns(6)

        for index, (stage_id, label) in enumerate(STAGES):
            with columns[index]:
                active = st.session_state.workflow_stage == stage_id

                if st.button(
                    f"{index + 1}. {label}",
                    key=f"stage_button_{stage_id}",
                    type="primary" if active else "secondary",
                    use_container_width=True,
                ):
                    go_to_stage(stage_id)

# ============================================================
# STAGE 1: PATIENT
# ============================================================

def patient_stage():
    st.header("👤 1. Patient Information")

    st.write(
        "Enter the available patient information. Save to continue "
        "automatically to the Report stage."
    )

    old = st.session_state.patient

    with st.form("patient_form"):
        left, right = st.columns(2)

        with left:
            age = st.number_input(
                "Age (years)",
                min_value=0,
                max_value=120,
                value=int(old.get("age") or 0),
            )

            sex_options = [
                "Not specified",
                "Female",
                "Male",
                "Other / not recorded",
            ]
            previous_sex = old.get("sex")
            sex_index = (
                sex_options.index(previous_sex)
                if previous_sex in sex_options else 0
            )
            sex = st.selectbox(
                "Sex recorded in source data",
                sex_options,
                index=sex_index,
            )

            family_options = ["Unknown", "No", "Yes"]
            previous_family = old.get("family_history")
            family_index = (
                family_options.index(previous_family)
                if previous_family in family_options else 0
            )
            family_history = st.selectbox(
                "Family history of diabetes",
                family_options,
                index=family_index,
            )

            height = st.number_input(
                "Height (cm)",
                min_value=0.0,
                max_value=250.0,
                value=float(old.get("height_cm") or 0.0),
                step=0.5,
            )

            weight = st.number_input(
                "Weight (kg)",
                min_value=0.0,
                max_value=400.0,
                value=float(old.get("weight_kg") or 0.0),
                step=0.5,
            )

        with right:
            hba1c = st.number_input(
                "HbA1c (%)",
                min_value=0.0,
                max_value=30.0,
                value=float(old.get("hba1c") or 0.0),
                step=0.1,
            )

            fasting = st.number_input(
                "Fasting glucose (mg/dL)",
                min_value=0.0,
                max_value=2000.0,
                value=float(old.get("fasting_glucose") or 0.0),
                step=1.0,
            )

            glucose = st.number_input(
                "Blood glucose (mg/dL)",
                min_value=0.0,
                max_value=2000.0,
                value=float(old.get("blood_glucose") or 0.0),
                step=1.0,
            )

            systolic = st.number_input(
                "Systolic blood pressure (mmHg)",
                min_value=0,
                max_value=400,
                value=int(old.get("systolic_bp") or 0),
            )

            diastolic = st.number_input(
                "Diastolic blood pressure (mmHg)",
                min_value=0,
                max_value=300,
                value=int(old.get("diastolic_bp") or 0),
            )

            cholesterol = st.number_input(
                "Total cholesterol (mg/dL)",
                min_value=0.0,
                max_value=2000.0,
                value=float(old.get("total_cholesterol") or 0.0),
                step=1.0,
            )

        context = st.text_area(
            "Additional clinical context (optional)",
            value=old.get("additional_context") or "",
            help="Avoid entering names, addresses, or medical record numbers.",
        )

        submitted = st.form_submit_button(
            "💾 Save Patient and Continue",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        patient = {
            "age": age if age > 0 else None,
            "sex": sex if sex != "Not specified" else None,
            "family_history": (
                family_history if family_history != "Unknown" else None
            ),
            "height_cm": height if height > 0 else None,
            "weight_kg": weight if weight > 0 else None,
            "hba1c": hba1c if hba1c > 0 else None,
            "fasting_glucose": fasting if fasting > 0 else None,
            "blood_glucose": glucose if glucose > 0 else None,
            "systolic_bp": systolic if systolic > 0 else None,
            "diastolic_bp": diastolic if diastolic > 0 else None,
            "total_cholesterol": (
                cholesterol if cholesterol > 0 else None
            ),
            "additional_context": context.strip() or None,
        }

        if height > 0 and weight > 0:
            patient["bmi"] = round(
                weight / ((height / 100) ** 2), 1
            )
        else:
            patient["bmi"] = None

        st.session_state.patient = patient
        st.session_state.assessment_result = None
        go_to_stage("Report")

# ============================================================
# STAGE 2: REPORT
# ============================================================

def report_stage():
    st.header("📄 2. Medical Report")

    st.write(
        "Upload a report if available. You can also continue without "
        "a report and review the information entered manually."
    )

    report_choice = st.radio(
        "Do you have a report to upload?",
        ["Yes, upload a report", "No report available"],
        horizontal=True,
        key="report_choice",
    )

    if report_choice == "No report available":
        st.session_state.parsed_report = None
        st.session_state.report_signature = None
        go_to_stage("Validate")
        return

    if parse_uploaded_report is None:
        st.error("The report parser could not be imported.")
        st.code(str(PARSER_IMPORT_ERROR))
        st.info(
            "You can select 'No report available' to continue "
            "with manually entered information."
        )
        return

    uploaded = st.file_uploader(
        "Upload PDF, CSV, or TXT",
        type=["pdf", "csv", "txt"],
        key="medical_report",
    )

    if uploaded is None:
        st.info(
            "Choose a file to continue. You can select 'No report available' "
            "above if you do not have a report."
        )
        return

    signature = (uploaded.name, uploaded.size)

    if signature != st.session_state.report_signature:
        try:
            with st.spinner("📄 Extracting report information..."):
                uploaded.seek(0)
                parsed = parse_uploaded_report(uploaded)

            st.session_state.parsed_report = parsed
            st.session_state.report_signature = signature

            values = extract_report_values(parsed)

            if values:
                updated = dict(st.session_state.patient)
                updated.update(values)
                st.session_state.patient = updated
                st.session_state.assessment_result = None

            # Continue to validation after parsing.
            go_to_stage("Validate")

        except Exception as exc:
            st.error(f"Report processing failed: {exc}")
            st.info(
                "Check the file format and verify extracted values "
                "against the original report."
            )
            return

    st.subheader("📋 Parsed Report Output")

    if st.session_state.parsed_report is not None:
        display_data(st.session_state.parsed_report)

    st.warning(
        "Automatically extracted values can be incomplete or incorrect. "
        "Review them against the original report before proceeding."
    )

    if st.button("➡️ Continue to Validation"):
        go_to_stage("Validate")

# ============================================================
# STAGE 3: VALIDATE
# ============================================================

def validate_stage():
    st.header("🧪 3. Data Validation")

    patient = st.session_state.patient

    if not patient:
        st.error("No patient information has been saved.")
        if st.button("Open Patient Stage"):
            go_to_stage("Patient")
        return

    missing = get_missing_fields()
    total = len(FIELD_LABELS)
    completed = total - len(missing)

    first, second, third = st.columns(3)
    first.metric("Checklist fields completed", f"{completed}/{total}")
    second.metric("Missing fields", len(missing))
    third.metric("Completeness", f"{completed / total:.0%}")

    if missing:
        st.error("⚠️ The following fields have not been entered:")

        for label in missing:
            st.markdown(f"- **{label}**")

        if st.button("✏️ Complete Missing Fields"):
            go_to_stage("Patient")
    else:
        st.success("All checklist fields have values.")

    st.subheader("📋 Current Patient Data")

    rows = [
        {
            "Field": key.replace("_", " ").title(),
            "Value": display_value(value),
        }
        for key, value in patient.items()
    ]

    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.warning(
        "Check units, report dates, fasting status, and source accuracy. "
        "Completeness does not guarantee clinical accuracy."
    )

    if st.button("Continue to Evidence Retrieval", type="primary"):
        go_to_stage("Retrieve")

# ============================================================
# STAGE 4: RETRIEVE
# ============================================================

def retrieve_stage():
    st.header("🔎 4. Evidence Retrieval and Assessment")

    if not st.session_state.patient:
        st.warning("Save patient information before running an assessment.")
        if st.button("Open Patient Stage"):
            go_to_stage("Patient")
        return

    if run_clinical_assessment is None:
        st.error("The assessment backend could not be imported.")
        st.code(str(ASSESSMENT_IMPORT_ERROR))
        return

    missing = get_missing_fields()

    if missing:
        st.warning("Missing fields: " + ", ".join(missing))

    st.write(
        "Run the existing clinical assessment pipeline. Review the output "
        "as research information rather than a diagnosis."
    )

    if st.button(
        "🔎 Run Evidence-Grounded Assessment",
        type="primary",
        use_container_width=True,
    ):
        try:
            with st.spinner(
                "Retrieving evidence and generating assessment..."
            ):
                result = run_clinical_assessment(
                    st.session_state.patient,
                    top_k=3,
                )

            st.session_state.assessment_result = result

            if isinstance(result, dict) and result.get("success") is False:
                st.error(
                    str(result.get("error", "The assessment was unsuccessful."))
                )
            else:
                st.success("Assessment completed.")

        except Exception as exc:
            st.session_state.assessment_result = {
                "success": False,
                "error": str(exc),
            }
            st.error(f"Assessment failed: {exc}")

    if st.session_state.assessment_result is not None:
        if st.button("Continue to Synthesis", type="primary"):
            go_to_stage("Synthesize")

# ============================================================
# STAGE 5: SYNTHESIZE
# ============================================================

def synthesize_stage():
    st.header("🧠 5. Assessment Summary")

    result = st.session_state.assessment_result

    if result is None:
        st.info("Run the assessment in the Retrieve stage first.")
        if st.button("Open Retrieve Stage"):
            go_to_stage("Retrieve")
        return

    st.subheader("What do these results mean?")

    st.write(
        "This summary comes from an academic research prototype. "
        "It is not a confirmed diagnosis and cannot reliably predict "
        "whether an individual will develop diabetes in the future."
    )

    if isinstance(result, dict):
        assessment = result.get("assessment")

        if assessment is not None:
            st.subheader("Assessment Findings")
            display_data(assessment)
        else:
            st.info(
                "The backend did not return a separate 'assessment' field. "
                "Inspect the full response below."
            )

        if result.get("error"):
            st.error(str(result["error"]))

        with st.expander("View Full Technical Response"):
            display_data(result)
    else:
        display_data(result)

    st.subheader("Recommended Next Steps")

    st.write(
        "Review the original laboratory report and relevant clinical "
        "history with a qualified healthcare professional. Do not make "
        "healthcare decisions based on this prototype alone."
    )

    if st.button("Continue to Verification", type="primary"):
        go_to_stage("Verify")

# ============================================================
# STAGE 6: VERIFY
# ============================================================

def verify_stage():
    st.header("🛡️ 6. Evidence Verification")

    result = st.session_state.assessment_result

    if result is None:
        st.info("Run the assessment in the Retrieve stage first.")
        if st.button("Open Retrieve Stage"):
            go_to_stage("Retrieve")
        return

    if isinstance(result, dict):
        st.subheader("📚 Retrieved Evidence")

        evidence = result.get("evidence")

        if evidence is not None:
            display_data(evidence)
        else:
            st.info(
                "The backend did not return a separate evidence field."
            )

        st.subheader("🔍 Verification Results")

        verification = result.get(
            "verification",
            result.get("verification_result"),
        )

        if verification is not None:
            display_data(verification)
        else:
            st.info(
                "No separate verification field was found in the response. "
                "Claims and sources should be reviewed manually."
            )

        with st.expander("View Full Backend Response"):
            display_data(result)
    else:
        display_data(result)

    st.caption(
        "Evidence verification should check whether each important claim "
        "is supported by an appropriate, traceable source."
    )

# ============================================================
# ASSESSMENT WORKFLOW ROUTER
# ============================================================

def assessment_page():
    workflow_bar()

    stage = st.session_state.workflow_stage

    if stage == "Patient":
        patient_stage()
    elif stage == "Report":
        report_stage()
    elif stage == "Validate":
        validate_stage()
    elif stage == "Retrieve":
        retrieve_stage()
    elif stage == "Synthesize":
        synthesize_stage()
    elif stage == "Verify":
        verify_stage()

# ============================================================
# EVIDENCE EXPLORER PAGE
# ============================================================

def evidence_explorer_page():
    st.header("📚 Evidence Explorer")

    result = st.session_state.assessment_result

    if result is None:
        st.info("Run an assessment to view its evidence.")
        return

    if isinstance(result, dict):
        evidence = result.get("evidence")

        if evidence is not None:
            display_data(evidence)
        else:
            st.info("No separate evidence field was returned.")
            display_data(result)
    else:
        display_data(result)

# ============================================================
# EVALUATION PAGE
# ============================================================

def evaluation_page():
    st.header("📊 Evaluation Checklist")

    st.write(
        "Use this checklist to document workflow review. These checks "
        "do not establish clinical validity."
    )

    checklist = [
        "Missing values reviewed",
        "Units and fasting status checked",
        "Extracted values compared with the original report",
        "Evidence sources recorded",
        "Claims compared with supporting evidence",
        "Uncertainty and limitations documented",
        "Clinician review requirement displayed",
    ]

    for index, label in enumerate(checklist):
        key = f"evaluation_check_{index}"

        st.session_state.evaluation_checks[key] = st.checkbox(
            label,
            value=st.session_state.evaluation_checks.get(key, False),
            key=key,
        )

    completed = sum(
        bool(st.session_state.evaluation_checks.get(
            f"evaluation_check_{i}", False
        ))
        for i in range(len(checklist))
    )

    st.metric("Checklist items completed", f"{completed}/{len(checklist)}")
    st.progress(completed / len(checklist))

# ============================================================
# LITERATURE PAGE
# ============================================================

def literature_page():
    st.header("📖 Literature")

    st.write(
        "Record literature sources used to support your research prototype."
    )

    with st.form("literature_form"):
        title = st.text_input("Source title")
        url = st.text_input("DOI or URL")
        notes = st.text_area("Relevance and limitations")

        submitted = st.form_submit_button("➕ Add Source")

    if submitted:
        if not title.strip() and not url.strip():
            st.warning("Enter a source title or URL.")
        else:
            st.session_state.literature_sources.append(
                {
                    "title": title.strip(),
                    "url": url.strip(),
                    "notes": notes.strip(),
                    "added_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )
            st.success("Source added for this session.")

    if st.session_state.literature_sources:
        st.subheader("Saved Sources")
        st.dataframe(
            st.session_state.literature_sources,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No literature sources have been added in this session.")

    st.caption("These entries are stored for the current session only.")

# ============================================================
# ABOUT PAGE
# ============================================================

def about_page():
    st.header("ℹ️ About DiaEvidence AI")

    st.write(
        "DiaEvidence AI is an academic research prototype for structured "
        "clinical data entry, medical report parsing, evidence retrieval, "
        "and transparent presentation of assessment outputs."
    )

    st.subheader("Key Components")

    st.markdown(
        """
        - Patient information entry
        - Optional medical report upload
        - Missing-data review
        - Evidence-grounded assessment pipeline
        - Assessment summary
        - Evidence verification review
        """
    )

    st.subheader("Limitations")

    st.markdown(
        """
        - This is not a validated prediction model or diagnostic device.
        - It cannot guarantee future health outcomes.
        - Report extraction may be incomplete or incorrect.
        - Missing data and incorrect units can affect results.
        - Avoid uploading direct personal identifiers.
        - A qualified healthcare professional should review relevant findings.
        """
    )

    st.caption(
        "DiaEvidence AI | Academic Research Prototype | "
        "Evidence-Grounded Clinical Decision Support"
    )

# ============================================================
# MAIN PAGE ROUTER
# ============================================================

if page == "🏥 Assessment":
    assessment_page()

elif page == "📚 Evidence Explorer":
    evidence_explorer_page()

elif page == "📊 Evaluation":
    evaluation_page()

elif page == "📖 Literature":
    literature_page()

elif page == "ℹ️ About":
    about_page()
