import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Use a specific model from your OpenRouter account.
# You can override this in .env using OPENROUTER_MODEL.
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "openrouter/free")


def ask_llm(question, evidence):
    """Generate an evidence-grounded clinical assessment using OpenRouter."""

    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is missing. Check your project's .env file."
        )

    # Prepare retrieved evidence
    evidence_parts = []

    for index, item in enumerate(evidence or [], start=1):
        evidence_parts.append(
            f"""
Evidence {item.get('evidence_number', index)}
Title: {item.get('title', 'Not provided')}
Source: {item.get('source', 'Not provided')}
Year: {item.get('year', 'Not provided')}
Category: {item.get('category', 'Not provided')}
PMID: {item.get('pmid', 'Not provided')}
DOI: {item.get('doi', 'Not provided')}
Evidence text:
{item.get('text', '')}
"""
        )

    evidence_text = "\n".join(evidence_parts)

    system_prompt = """
You are an evidence-grounded clinical information assistant for an
academic healthcare informatics research prototype.

Rules:
1. Use only the supplied patient information and retrieved evidence.
2. Do not invent clinical facts, diagnoses, references, PMIDs, or DOIs.
3. Distinguish risk assessment from diagnosis.
4. Do not claim the patient has a disease unless the supplied information
   explicitly supports that statement.
5. Do not prescribe medication or recommend starting, stopping, or changing it.
6. Do not provide medication dosages.
7. Cite important evidence-based claims using [Evidence N].
8. Clearly identify missing information and uncertainty.
9. If evidence is insufficient, say so explicitly.
10. Use concise, professional clinical language.
11. This research prototype is not clinically validated and does not replace
    assessment by a qualified healthcare professional.
"""

    user_prompt = f"""
Clinical question and patient information:
{question}

Retrieved medical evidence:
{evidence_text}

Provide a concise, structured, evidence-grounded assessment.
Use only the supplied information. Do not invent missing values or diagnoses.
Cite relevant claims with the evidence numbers provided above.
If evidence is insufficient, state that clearly.
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1200,
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=90,
        )
    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Could not connect to OpenRouter: {error}"
        ) from error

    if not response.ok:
        raise RuntimeError(
            f"OpenRouter API error (HTTP {response.status_code}): "
            f"{response.text[:1000]}"
        )

    try:
        result = response.json()
    except ValueError as error:
        raise RuntimeError(
            "OpenRouter returned an invalid JSON response."
        ) from error

    choices = result.get("choices") or []
    if not choices:
        raise RuntimeError(
            f"OpenRouter returned no choices. Response: {result}"
        )

    choice = choices[0]
    message = choice.get("message") or {}
    content = message.get("content")

    # Some models return content as a list of text blocks.
    if isinstance(content, list):
        text_parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        content = "\n".join(part for part in text_parts if part.strip())

    if isinstance(content, str) and content.strip():
        return content.strip()

    # Do not treat hidden reasoning as the clinical assessment.
    finish_reason = choice.get("finish_reason", "unknown")
    error_details = choice.get("error") or result.get("error")

    raise RuntimeError(
        "The selected OpenRouter model returned no usable assessment text. "
        f"Model: {result.get('model', MODEL_NAME)}. "
        f"Finish reason: {finish_reason}. "
        f"Details: {error_details or 'No additional error details provided'}. "
        "Try another available model in your OpenRouter settings."
    )
