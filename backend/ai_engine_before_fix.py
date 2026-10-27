import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL_NAME = os.getenv("OPENROUTER_MODEL", "openrouter/free")


SYSTEM_PROMPT = """
You are an evidence-grounded clinical information assistant for an
academic healthcare informatics research prototype.

Rules:
1. Use only the supplied patient information and retrieved evidence.
2. Never invent clinical facts, diagnoses, references, PMIDs, or DOIs.
3. Distinguish risk assessment from diagnosis.
4. Do not prescribe medication or recommend starting, stopping, or changing it.
5. Do not provide medication dosages.
6. Cite relevant evidence-based claims using [Evidence N].
7. Identify missing information and uncertainty.
8. If evidence is insufficient, state so explicitly.
9. Use concise, professional clinical language.
10. This prototype is not clinically validated and does not replace
    assessment by a qualified healthcare professional.

Return a concise assessment with these headings:
- Summary
- Relevant Risk Factors
- Evidence-Based Findings
- Limitations and Uncertainty
- Clinical Review Needed
"""


def _extract_text(result):
    """Extract visible answer text from an OpenRouter response."""

    choices = result.get("choices") or []

    if not choices:
        return ""

    message = choices[0].get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    text = block.get("text", "")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())

        return "\n".join(parts)

    return ""


def _call_openrouter(messages, max_tokens):
    """Send one request to OpenRouter."""

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": max_tokens,
        },
        timeout=90,
    )

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

    return result


def ask_llm(question, evidence):
    """Generate a concise, evidence-grounded clinical assessment."""

    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is missing. Check your project's .env file."
        )

    evidence_parts = []

    for index, item in enumerate(evidence or [], start=1):
        if not isinstance(item, dict):
            continue

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

    user_prompt = f"""
Clinical question and patient information:
{question}

Retrieved medical evidence:
{evidence_text}

Provide a concise clinical information assessment.
Use only the supplied information and evidence.
Cite relevant claims using the supplied evidence numbers.
Do not invent missing values, diagnoses, or references.
Clearly state uncertainty and the need for professional review.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # First attempt: allow more room for the assessment.
    result = _call_openrouter(messages, max_tokens=2000)
    answer = _extract_text(result)

    if answer:
        return answer

    finish_reason = (
        (result.get("choices") or [{}])[0].get(
            "finish_reason", "unknown"
        )
    )

    # Retry once with a shorter prompt if the first response is empty.
    retry_messages = [
        {
            "role": "system",
            "content": (
                "Provide a short, evidence-grounded clinical assessment. "
                "Do not invent facts or references. Do not prescribe. "
                "Distinguish risk from diagnosis. Mention uncertainty and "
                "professional review. Cite supplied evidence as [Evidence N]."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Patient information and question:\n{question}\n\n"
                f"Retrieved evidence:\n{evidence_text}\n\n"
                "Return a brief assessment with findings, evidence, "
                "limitations, and clinical review needed."
            ),
        },
    ]

    retry_result = _call_openrouter(retry_messages, max_tokens=2000)
    retry_answer = _extract_text(retry_result)

    if retry_answer:
        return retry_answer

    retry_finish_reason = (
        (retry_result.get("choices") or [{}])[0].get(
            "finish_reason", "unknown"
        )
    )

    raise RuntimeError(
        "OpenRouter returned no usable assessment text after two attempts. "
        f"Model: {retry_result.get('model', MODEL_NAME)}. "
        f"First finish reason: {finish_reason}. "
        f"Retry finish reason: {retry_finish_reason}. "
        "Check the model's availability, output limits, and OpenRouter "
        "response details."
    )