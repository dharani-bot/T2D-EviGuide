from backend.rag_engine import build_evidence_package
from backend.ai_engine import ask_llm


question = (
    "What clinical measurements are relevant "
    "when assessing glycemic status?"
)


evidence = build_evidence_package(
    question,
    top_k=3
)


if not evidence:

    print(
        "Insufficient relevant evidence retrieved."
    )

else:

    answer = ask_llm(
        question,
        evidence
    )

    print("\n===== LLM RESPONSE =====\n")
    print(answer)