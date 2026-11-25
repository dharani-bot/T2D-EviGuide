# T2D-EviGuide

## Early Disease Prediction Using AI and Multimodal Clinical Data

### 1. Project Overview

**T2D-EviGuide** is an academic healthcare informatics research prototype exploring the application of Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and multimodal clinical information for evidence-grounded Type 2 Diabetes (T2D) risk assessment.

The system integrates patient-provided clinical information with retrieved medical literature to generate structured, explainable clinical assessment summaries.

The primary objective is to explore how AI-assisted evidence retrieval and clinical information processing can support healthcare decision-making workflows while maintaining transparency, evidence traceability, and clinical safety.

This project is developed as part of an MSc Healthcare Informatics and Data Analytics research initiative.

### 2. Project Objectives

- Explore the application of LLMs in healthcare information processing.
- Integrate patient demographic, anthropometric, laboratory, lifestyle, dietary, and medical history information.
- Implement RAG for retrieving relevant medical literature.
- Generate structured clinical assessment summaries using retrieved evidence.
- Introduce clinical data validation and safety guardrails.
- Improve transparency through evidence citation verification.
- Explore the potential of AI-assisted clinical decision-support workflows.

### 3. Key Features

**Patient Information Management**
- Patient demographic information.
- Anthropometric measurements.
- Laboratory investigations.
- Vital signs.
- Lifestyle and dietary information.
- Medical history and medication information.
- Clinical document upload.

**Clinical Data Validation**
- Required-field checks.
- Numeric data validation.
- Clinically reasonable input boundaries.
- BMI calculation and blood pressure consistency checks.
- Identification of missing clinical information.

**Evidence Retrieval**
- Medical literature processing and text chunking.
- Semantic evidence retrieval.
- Lexical relevance matching.
- Language-aware retrieval.
- Article metadata preservation.

**AI-Based Assessment**
- LLM-powered clinical assessment generation.
- Patient-context integration.
- Evidence-grounded interpretation.
- Structured clinical summaries.
- Identification of uncertainty and missing information.

**Clinical Safety and Evidence Verification**
- Clinical safety guardrails.
- Distinction between risk assessment and diagnosis.
- Restrictions against unsupported prescribing recommendations.
- Evidence citation correspondence checks.
- Reference traceability.

### 4. Technology Stack

| Category | Technology |
|---|---|
| Programming language | Python |
| User interface | Streamlit |
| Data processing | Pandas, NumPy |
| Visualization | Matplotlib |
| Language model integration | OpenRouter API |
| AI architecture | Large Language Models (LLMs) |
| Retrieval architecture | Retrieval-Augmented Generation (RAG) |
| Vector database | ChromaDB |
| Embedding model | sentence-transformers/all-MiniLM-L6-v2 |
| Language detection | Langdetect |
| HTTP communication | Requests |
| Environment configuration | Python-dotenv |
| Literature processing | Python-based text processing |

### 5. System Architecture

The application follows an evidence-grounded clinical information processing workflow.

```text
                  PATIENT INPUT
                       |
                       v
                Streamlit Interface
                     (app.py)
                       |
                       v
              Clinical Data Validation
              (clinical_validation.py)
                       |
                       v
              Clinical Assessment Module
              (clinical_assessment.py)
                       |
              +--------+---------+
              |                  |
              v                  v
       Patient Context       Evidence Retrieval
                                  |
                                  v
                           backend/rag_engine.py
                                  |
                         +--------+--------+
                         |                 |
                         v                 v
                    ChromaDB         Semantic Search
                  Vector Store       + Lexical Matching
                         |
                         v
                 Retrieved Evidence
                         |
                         v
                 backend/ai_engine.py
                         |
                         v
                  OpenRouter LLM
                         |
                         v
               Generated Assessment
                         |
                         v
              Clinical Safety Checks
                         |
                         v
               Evidence Verification
                         |
                         v
                 Final AI Assessment
```

### 6. Evidence Retrieval Implementation

The RAG pipeline processes medical literature and makes relevant information available to the LLM.

**Evidence processing workflow:**

1. Medical literature files are processed.
2. Text is cleaned and divided into smaller evidence chunks.
3. Relevant metadata is extracted and preserved.
4. Sentence Transformer embeddings are generated.
5. Embeddings and associated evidence are stored in ChromaDB.
6. Relevant evidence is retrieved using semantic and lexical matching.
7. Retrieved evidence is incorporated into the LLM assessment workflow.

**Embedding Model:**

`sentence-transformers/all-MiniLM-L6-v2`

**ChromaDB Collection:**

`t2d_evidence`

**Vector Database Location:**

`data/vector_db/`

**Evidence Chunk File:**

`data/chunks.json`

### 7. Current Evidence Processing Results

The current evidence-processing run produced the following results:

| Metric | Result |
|---|---:|
| Literature files identified | 10 |
| Sources producing usable chunks | 3 |
| AACE 2026 T2D | 117 chunks |
| T2D Diagnosis Review 2026 | 99 chunks |
| USPSTF 2021 Screening | 14 chunks |
| Duplicate chunks removed | 24 |
| Final evidence chunks | **206** |

Six generic ADA abstracts were excluded, and one source contained no usable content.

These figures describe the current local evidence-processing run and may change as the literature collection is expanded.

### 8. Project Structure

```text
T2D-EviGuide/
|
|-- app.py
|-- clinical_validation.py
|-- clinical_assessment.py
|-- clinical_guardrails.py
|-- clinical_guardrails_v2.py
|-- evidence_verifier.py
|-- evidence_policy.py
|
|-- backend/
|   |-- __init__.py
|   |-- ai_engine.py
|   |-- rag_engine.py
|   |-- clinical_engine.py
|   |-- evidence_engine.py
|   |-- literature_engine.py
|   |-- safety_engine.py
|
|-- data/
|   |-- cleaned/
|   |-- processed/
|   |-- chunks.json (generated locally)
|   |-- vector_db/ (generated locally)
|
|-- tests/
|-- reports/
|-- Figures/
|-- archive_consolidation/
|
|-- text_chunker.py
|-- literature_manager.py
|-- literature_processor.py
|-- literature_search.py
|-- llm_client.py
|-- vector_store.py
|
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- README.md

*Note: The structure highlights the principal application components. Additional research, literature-processing, evaluation, and supporting scripts are also maintained in the repository.*

### 9. Installation and Setup

#### Prerequisites

- Python 3.10 or a compatible supported Python version.
- Git.
- An OpenRouter API key.
- Internet connectivity for API communication and initial model downloads.

#### Step 1: Clone the repository

```bash
git clone https://github.com/dharani-bot/T2D-EviGuide.git
cd T2D-EviGuide
```

#### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate it using Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

#### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

#### Step 4: Configure environment variables

Create a `.env` file in the project root.

Add the following configuration:

```env
OPENROUTER_API_KEY=your_api_key_here
```

An optional model configuration is also supported:

```env
OPENROUTER_MODEL=openrouter/free
```

Never upload the actual `.env` file or API key to GitHub.

#### Step 5: Generate evidence chunks

Run:

```bash
python text_chunker.py
```

This processes the available cleaned literature files and generates:

`data/chunks.json`

#### Step 6: Build the vector database

Run:

```bash
python -c "from backend.rag_engine import build_vector_store; build_vector_store()"
```

This generates document embeddings and stores the evidence in the persistent ChromaDB collection.

**Important:** Running this command again deletes and recreates the existing `t2d_evidence` collection. It should be used when rebuilding the evidence database.

#### Step 7: Launch the application

```bash
python -m streamlit run app.py
```

Streamlit will provide a local application address in the terminal.

### 10. Clinical Safety and Research Limitations

T2D-EviGuide is an academic research prototype and has not been clinically validated.

The system:

- Does not independently diagnose Type 2 Diabetes.
- Does not calculate a validated disease probability.
- Does not replace established clinical assessment procedures.
- Does not autonomously prescribe or recommend medication changes.
- Depends on the quality and availability of supplied patient information and retrieved literature.
- Requires independent review of AI-generated interpretations.

The evidence verification module checks whether generated evidence citations correspond to retrieved sources. It does not establish medical truth, clinical accuracy, or semantic support for individual claims.

AI-generated outputs must not be treated as a substitute for professional medical judgment.

Only synthetic, de-identified, or otherwise appropriately authorized information should be used during research and testing.

### 11. Future Development Scope

Potential future enhancements include:

- Expansion of the medical literature collection.
- Improved evidence quality assessment.
- Broader biomarker and clinical indicator coverage.
- Enhanced clinical document processing.
- More comprehensive evidence verification.
- Improved explainability and assessment traceability.
- Systematic evaluation of retrieval quality and AI-generated outputs.
- Further testing of clinical safety and data validation mechanisms.

### 12. Project Information

**Project:** T2D-EviGuide

**Research Framework:** Early Disease Prediction Using AI and Multimodal Clinical Data

**Domain:** Healthcare Informatics and Data Analytics

**Primary Use Case:** Type 2 Diabetes

**Implementation Approach:** LLM + RAG + Medical Literature

**Application Type:** Academic Research Prototype

---

*Developed for academic research and educational purposes. Not intended for autonomous diagnosis, treatment, or prescribing.*