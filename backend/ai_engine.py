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
11. Do not claim that a source supports a statement unless the supplied
    evidence text supports that statement.
12. Never invent a risk score or imply that a validated risk calculator
    was applied unless its calculated result was supplied.

Return a complete, concise assessment with these headings:
- Summary
- Relevant Risk Factors
- Evidence-Based Findings
- Limitations and Uncertainty
- Clinical Review Needed

Finish every section. Do not stop halfway through a sentence.
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
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())

        return "\n".join(parts)

    return ""


def _call_openrouter(messages, max_tokens):
    """Send one request to OpenRouter and return its JSON response."""

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


def _get_finish_reason(result):
    """Return the provider's completion reason, if available."""

    choices = result.get("choices") or []

    if not choices:
        return "unknown"

    return choices[0].get("finish_reason") or "unknown"


def _looks_incomplete(answer, finish_reason):
    """
    Detect provider-reported length truncation and obvious unfinished output.

    This is a heuristic, not a guarantee that every response is complete.
    """

    if not answer:
        return True

    if finish_reason == "length":
        return True

    text = answer.rstrip()
    if not text:
        return True

    # An unfinished final sentence is a warning sign.
    if text.endswith((" the", " a", " an", " and", " or", " because",
                      " with", " of", " for", " to", " is", " are")):
        return True

    # A response that ends in the middle of a Markdown heading is suspicious.
    if text.endswith("#"):
        return True

    return False


def _build_evidence_text(evidence):
    """Format the supplied evidence without inventing source metadata."""

    evidence_parts = []

    for index, item in enumerate(evidence or [], start=1):
        if not isinstance(item, dict):
            continue

        evidence_number = item.get("evidence_number", index)

        evidence_parts.append(
            f"""
Evidence {evidence_number}
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

    return "\n".join(evidence_parts)


def ask_llm(question, evidence):
    """Generate a concise, evidence-grounded clinical assessment."""

    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is missing. Check your project's .env file."
        )

    evidence_text = _build_evidence_text(evidence)

    user_prompt = f"""
Clinical question and patient information:
{question}

Retrieved medical evidence:
{evidence_text}

Write a complete, concise clinical information assessment.

Requirements:
- Include all five headings specified in the system instructions.
- Use only the supplied patient information and retrieved evidence.
- Cite evidence-based claims using the supplied [Evidence N] identifiers.
- Do not invent missing values, diagnoses, scores, statistics, or references.
- Identify uncertainty and missing information.
- End with a complete sentence.
- If evidence is insufficient, say so.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # First attempt.
    result = _call_openrouter(messages, max_tokens=2000)
    answer = _extract_text(result)
    finish_reason = _get_finish_reason(result)

    if answer and not _looks_incomplete(answer, finish_reason):
        return answer

    # Retry with a shorter response requirement if output is empty or truncated.
    retry_messages = [
        {
            "role": "system",
            "content": (
                "You are an evidence-grounded clinical information assistant. "
                "Do not invent facts, diagnoses, scores, statistics, or "
                "references. Do not prescribe. Distinguish risk assessment "
                "from diagnosis. Use only supplied patient information and "
                "evidence. Cite supported claims as [Evidence N]."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Patient information and clinical question:\n{question}\n\n"
                f"Retrieved evidence:\n{evidence_text}\n\n"
                "Write a brief but COMPLETE assessment with these headings: "
                "Summary; Relevant Risk Factors; Evidence-Based Findings; "
                "Limitations and Uncertainty; Clinical Review Needed. "
                "Use short bullets. Complete every section and every sentence. "
                "Do not invent unsupported facts or references."
            ),
        },
    ]

    retry_result = _call_openrouter(retry_messages, max_tokens=1600)
    retry_answer = _extract_text(retry_result)
    retry_finish_reason = _get_finish_reason(retry_result)

    if retry_answer and not _looks_incomplete(
        retry_answer, retry_finish_reason
    ):
        return retry_answer

    raise RuntimeError(
        "OpenRouter did not return a complete assessment after two attempts. "
        f"Model: {retry_result.get('model', MODEL_NAME)}. "
        f"First finish reason: {finish_reason}. "
        f"Retry finish reason: {retry_finish_reason}. "
        "Check the configured model and its output-token limits."
    )
