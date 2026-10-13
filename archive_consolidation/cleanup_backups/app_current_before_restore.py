import streamlit as st

from clinical_validation import validate_patient_data
from clinical_assessment import generate_risk_assessment
from evidence_verifier import verify_assessment

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="T2D-EviGuide",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CLINICAL PROTOTYPE UI STYLE
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
    background-color: #f4f7fb !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #f4f7fb !important;
}

[data-testid="stHeader"] {
    background-color: #f4f7fb !important;
}

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
        max-width: 1250px;
    }

    .main-title {
        background: linear-gradient(
            90deg,
            #1565c0,
            #5e35b1
        );
        padding: 18px 24px;
        border-radius: 14px;
        color: white;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .main-title h1 {
        margin: 0;
        font-size: 30px;
    }

    .main-title p {
        margin: 5px 0 0 0;
        font-size: 14px;
        opacity: 0.92;
    }

    h2 {
        color: #16324f;
        margin-top: 16px !important;
        margin-bottom: 8px !important;
    }

    h3 {
        color: #315a7d;
        margin-top: 10px !important;
        margin-bottom: 6px !important;
    }

    .element-container {
        margin-bottom: 0.25rem;
    }

    .stSelectbox label,
    .stNumberInput label,
    .stTextInput label,
    .stTextArea label,
    .stFileUploader label {
        font-weight: 600;
        color: #34495e;
    }

    .stSelectbox > div > div,
    .stNumberInput > div > div,
    .stTextInput > div > div,
    .stTextArea textarea {
        border-radius: 8px;
    }

    .stButton > button {
        border-radius: 9px;
        min-height: 40px;
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        background: white;
        padding: 10px 14px;
        border-radius: 10px;
        border: 1px solid #dbe5ef;
    }

    .streamlit-expanderHeader {
        background: #eef4fa;
        border-radius: 8px;
        font-weight: 600;
    }

    .stAlert {
        border-radius: 9px;
    }

    hr {
        margin-top: 10px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)