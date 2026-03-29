<div align="center">
  <h1>📚 SmartDoc RAG: Enterprise PDF Intelligence</h1>
  <p>
    An end-to-end, privacy-focused Retrieval-Augmented Generation (RAG) system for unlocking insights from PDF documents.
  </p>
  
  [![Python version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
  [![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain.com/)
  [![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=flat&logo=huggingface&logoColor=black)](https://huggingface.co/)
</div>

---

## 🚀 Overview

**SmartDoc RAG** is a highly efficient, full-stack document Q&A application designed to ingest PDF files, process text embeddings locally, and synthesize accurate answers using state-of-the-art Large Language Models. 

By leveraging **local embedding models** (`BAAI/bge-base-en-v1.5`) running on CPU/Apple MPS and the **HuggingFace Inference API** for LLM generation (`Meta Llama 3.2`), this architecture achieves robust performance with **zero infrastructure and embedding API costs**.

## ✨ Key Features

- **Blazing Fast Ingestion:** Utilizes `PyMuPDF (fitz)` for rapid, high-fidelity text extraction from PDF byte streams.
- **Privacy-First Embeddings:** Document embeddings are generated 100% locally via `sentence-transformers` avoiding external data leakage during the vectorization phase.
- **In-Memory Vector Search:** Implemented **FAISS** for highly scalable, sub-millisecond similarity search bridging queries and context windows.
- **Strict Guardrails:** The LLM prompt template enforces strict hallucination guardrails, mandating the agent precisely cite or acknowledge missing contexts natively.
- **Production-Ready Backend:** Async **FastAPI** backbone utilizing **Pydantic** `BaseModel` schemas for strict type safety and input validation.
- **Interactive UI:** A highly intuitive **Streamlit** frontend allowing effortless document uploads and chat interfaces.

---

## 🛠️ Architecture

1. **Ingestion (`/ingest`)**: Upload PDF ➔ Parse with `PyMuPDF` ➔ Chunk via `LangChain RecursiveCharacterTextSplitter`.
2. **Vectorization**: Transform chunks to dense vectors using `HuggingFaceEmbeddings` ➔ Index in `FAISS`.
3. **Retrieval (`/query`)**: Vectorize user query ➔ K-Nearest Neighbor similarity search ➔ Inject context.
4. **Generation**: `ChatHuggingFace` model processes Prompt + Context ➔ Formats grounded answer.

---

## ⚙️ Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Backend API** | FastAPI, Uvicorn | Async I/O handling, automatic OpenAPI docs, sheer speed. |
| **Frontend** | Streamlit | Rapid prototyping of AI workflows and robust native file uploading. |
| **Orchestrator** | LangChain Core | LCEL (LangChain Expression Language) for modular, parallel chain execution. |
| **Embeddings** | HuggingFace (`BGE`) | Top-tier open-source embeddings, executed locally for cost-efficiency. |
| **Vector DB** | FAISS | Lightweight, highly optimized in-memory vector similarity search. |
| **Package Manager**| `uv` | Rust-based Python package manager for lightning-fast environment resolution. |

---

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) package manager installed.

### 1. Installation
Clone the repository and sync the dependencies instantly:
```bash
git clone https://github.com/yourusername/qa-rag.git
cd qa-rag
uv sync # Installs all dependencies locked in uv.lock
```

### 2. Environment Setup
Create a `.env` file in the root directory and add your free HuggingFace API Token:
```env
HUGGINGFACEHUB_API_TOKEN=hf_your_token_here
```

### 3. Run the Backend Server
Start the FastAPI server (Runs on port `8000`):
```bash
uv run uvicorn backend.main:app --reload
```
*(You can view the interactive API docs at `http://localhost:8000/docs`)*

### 4. Run the Frontend UI
In a separate terminal, launch the Streamlit interface (Runs on port `8501`):
```bash
uv run streamlit run frontend/main.py
```

---

## 👤 Developer Notes

This project was built to demonstrate proficiency in:
- Connecting disparate Microservices (FastAPI & Streamlit).
- Advanced **Prompt Engineering** techniques (Anti-hallucination logic, partial-context acknowledgment).
- **RAG Architecture Pattern** implementations.
- API design and strict data validation using **Pydantic**.
