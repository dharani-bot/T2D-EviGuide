import os
import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free router for initial testing
MODEL_NAME = "openrouter/free"


def ask_llm(question, evidence):
    """
    Send a clinical question and retrieved evidence to an LLM.

    The LLM is instructed to:
    - use only supplied evidence
    - avoid unsupported medical claims
    - distinguish risk assessment from diagnosis
    - avoid medication prescribing/changing instructions
    - identify the evidence supporting important claims
    """

    # Check API key
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is not configured. "
            "Check your .env file."
        )

    # ---------------------------------------------------------
    # Build evidence context
    # ---------------------------------------------------------

    evidence_text = ""

    for item in evidence:
        evidence_text += (
            f"\nEvidence {item['evidence_number']}\n"
            f"Title: {item['title']}\n"
            f"Source: {item['source']}\n"
            f"Year: {item['year']}\n"
            f"Category: {item['category']}\n"
            f"PMID: {item['pmid']}\n"
            f"DOI: {item['doi']}\n"
            f"Evidence text:\n{item['text']}\n"
            f"\n"
        )

    # ---------------------------------------------------------
    # System prompt
    # ---------------------------------------------------------

    system_prompt = """
You are an evidence-grounded clinical information assistant
for an academic healthcare informatics prototype.

Your task is to interpret the supplied clinical question using
ONLY the retrieved medical evidence provided by the system.

Rules:

1. Do not invent medical facts.
2. Do not invent citations, studies, PMIDs, or DOIs.
3. Do not use medical knowledge that is not supported by the
   supplied evidence.
4. If the supplied evidence is insufficient, explicitly state:
   "The retrieved evidence is insufficient to support this
   conclusion."
5. Distinguish early risk assessment from clinical diagnosis.
6. Do not claim that the patient has diabetes unless the supplied
   evidence and patient information explicitly support that
   conclusion.
7. Do not prescribe medications.
8. Do not recommend starting, stopping, or changing medication.
9. Do not provide dosage instructions.
10. Every important factual clinical claim should reference the
    relevant evidence number, such as [Evidence 1].
11. Clearly identify uncertainty or missing information.
12. Use concise, professional clinical language.
13. This is a clinical decision-support prototype and does not
    replace assessment by a qualified healthcare professional.
"""

    # ---------------------------------------------------------
    # User prompt
    # ---------------------------------------------------------

    user_prompt = f"""
Clinical question:

{question}

Retrieved medical evidence:

{evidence_text}

Using ONLY the retrieved evidence above, provide a concise
evidence-grounded response.

For each important clinical claim, include the supporting
evidence number, for example:

[Evidence 1]

If the evidence does not adequately support a conclusion,
say so explicitly rather than guessing.
"""

    # ---------------------------------------------------------
    # OpenRouter API request
    # ---------------------------------------------------------

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                "temperature": 0.1,
            },
            timeout=60,
        )

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Could not connect to OpenRouter: {error}"
        ) from error

    # ---------------------------------------------------------
    # Handle API errors
    # ---------------------------------------------------------

    if not response.ok:
        print("\n===== OPENROUTER ERROR =====")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        print("============================\n")

        response.raise_for_status()

    # ---------------------------------------------------------
    # Parse successful response
    # ---------------------------------------------------------

    try:
        result = response.json()
    except ValueError as error:
        raise RuntimeError(
            "OpenRouter returned an invalid JSON response."
        ) from error

    # Check that a response was actually returned
    if "choices" not in result or not result["choices"]:
        raise RuntimeError(
            f"OpenRouter response did not contain a valid choice: "
            f"{result}"
        )

    message = result["choices"][0].get("message", {})

    answer = message.get("content")

    if not answer:
        raise RuntimeError(
            f"OpenRouter returned no text content: {result}"
        )

    return answer
    
    

