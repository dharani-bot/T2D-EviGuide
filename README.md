# T2D-EviGuide

### Early Disease Prediction Using AI and Multimodal Clinical Data

T2D-EviGuide is an academic research prototype exploring the use of Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and multimodal clinical information to support evidence-grounded Type 2 Diabetes assessment.

The project focuses on retrieving relevant medical literature, interpreting patient clinical information, and generating explainable, evidence-supported clinical summaries.

## Key Features

- Patient demographic and clinical data collection
- Clinical data validation
- Evidence retrieval from medical literature
- Semantic and lexical evidence search
- Language-aware evidence retrieval
- AI-generated clinical assessment summaries
- Evidence verification and reference traceability
- Clinical safety guardrails
- Research-oriented decision-support workflow

## Technology Stack

- Python
- Streamlit
- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG)
- ChromaDB
- Sentence Transformers
- Langdetect
- OpenRouter API
- PubMed and PubMed Central literature sources

## Project Structure

```text
T2D-EviGuide/
│
├── app.py
├── clinical_assessment.py
├── clinical_validation.py
├── clinical_guardrails_v2.py
├── evidence_verifier.py
├── text_chunker.py
├── literature_manager.py
├── literature_processor.py
├── literature_search.py
├── llm_client.py
├── vector_store.py
│
├── backend/
├── data/
├── tests/
├── reports/
├── Figures/
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

Additional evaluation scripts and historical backups are maintained separately.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/dharani-bot/T2D-EviGuide.git
cd T2D-EviGuide
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the API key

Create a `.env` file in the project root.

Add:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Never upload your `.env` file or API key to GitHub.

### 5. Generate evidence chunks

```bash
python text_chunker.py
```

This processes the available literature records and generates the evidence chunks used by the retrieval pipeline.

### 6. Build the vector database

```bash
python -c "from backend.rag_engine import build_vector_store; build_vector_store()"
```

This creates the local ChromaDB evidence collection.

### 7. Run the application

```bash
python -m streamlit run app.py
```

## Evidence Retrieval Workflow

1. Medical literature is collected and processed.
2. Relevant text is divided into evidence chunks.
3. Sentence Transformer embeddings support semantic retrieval.
4. ChromaDB stores and retrieves evidence.
5. Language-aware retrieval prioritises evidence matching the query language.
6. Retrieved evidence is supplied to the LLM.
7. Clinical guardrails and evidence verification support safer assessment summaries.

## Research and Safety Disclaimer

T2D-EviGuide is an academic healthcare informatics research prototype.

It is not a clinically validated diagnostic system. It must not be used for autonomous diagnosis, treatment decisions, or prescribing.

AI-generated assessments require independent clinical review. The prototype does not replace qualified healthcare professionals or professional medical judgment.