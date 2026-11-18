\# T2D-EviGuide

\### Early Disease Prediction Using AI and Multimodal Clinical Data



\*\*T2D-EviGuide\*\* is a research prototype exploring the use of Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and medical literature to support evidence-grounded Type 2 Diabetes assessment.



\## Key Features



\- Patient clinical and demographic data entry

\- Clinical data validation

\- Evidence retrieval from medical literature

\- Semantic search using Sentence Transformers and ChromaDB

\- AI-generated clinical assessments

\- Evidence verification and reference traceability

\- Clinical decision-support summaries



\## Technology Stack



\- Python

\- Streamlit

\- Large Language Models (LLMs)

\- Retrieval-Augmented Generation (RAG)

\- ChromaDB

\- Sentence Transformers

\- OpenRouter API

\- PubMed and PMC literature retrieval



\## Project Setup



\### 1. Clone the repository



```bash

git clone https://github.com/dharani-bot/T2D-EviGuide.git

cd T2D-EviGuide

```



\### 2. Create a virtual environment



```bash

python -m venv .venv

```



Activate it in Windows PowerShell:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Configure the API key



Create a `.env` file in the project root and configure the OpenRouter API key using the variable expected by `llm\_client.py`.



Never upload your `.env` file or API key to GitHub.



\### 5. Generate evidence chunks



```bash

python text\_chunker.py

```



This processes the cleaned literature files and generates `data/chunks.json`.



\### 6. Build the vector database



```bash

python -c "from backend.rag\_engine import build\_vector\_store; build\_vector\_store()"

```



This generates the ChromaDB evidence collection locally.



\### 7. Run the application



```bash

python -m streamlit run app.py

```



\## Evidence Preparation



The current literature corpus contains:



\- 10 cleaned literature files

\- 236 generated evidence chunks

\- Full-text and abstract-based literature records

\- ChromaDB collection: `t2d\_evidence`



Generated chunks and vector database files are excluded from GitHub and should be recreated locally using the commands above.



\## Research and Safety Disclaimer



T2D-EviGuide is an academic research prototype developed for healthcare informatics learning and research.



It is not a clinically validated diagnostic system and must not be used as an autonomous diagnostic or prescribing tool. AI-generated assessments require independent clinical review. The system does not replace professional medical judgment.

