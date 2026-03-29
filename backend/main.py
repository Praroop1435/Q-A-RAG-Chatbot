from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from data_ingestion import extract_text_from_pdf, split_text
from retrieval import create_vector_store, create_retriever
from rag_chain import build_rag_chain

VECTOR_STORE = None

app = FastAPI(title="PDF RAG Backend")


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    answer: str


class IngestResponse(BaseModel):
    filename: str
    chunks: int
    message: str


@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    global VECTOR_STORE
    try:
        if not file.filename or not file.filename.endswith(".pdf"):
            raise HTTPException(400, "Only PDF files are supported.")

        content = await file.read()
        text = extract_text_from_pdf(content)

        if not text.strip():
            raise HTTPException(400, "Could not extract text from the PDF.")

        chunks = split_text(text)
        VECTOR_STORE = create_vector_store(chunks)

        return IngestResponse(
            filename=file.filename,
            chunks=len(chunks),
            message="PDF ingested and indexed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest):
    if VECTOR_STORE is None:
        raise HTTPException(400, "No document ingested yet. Please upload a PDF first.")

    try:
        retriever = create_retriever(VECTOR_STORE)
        rag_chain = build_rag_chain(retriever)
        answer = rag_chain.invoke(payload.question)

        return QueryResponse(
            question=payload.question,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
