from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from data_ingestion import extract_text_from_pdf, split_text
from retrieval import create_vector_store, create_retriever
from rag_chain import build_rag_chain

VECTOR_STORE = None

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PDF RAG Backend")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    context: list[str] = []


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
        
        # Explicitly fetch the documents to return to the frontend for visualization
        docs = retriever.invoke(payload.question)
        retrieved_chunks = [doc.page_content for doc in docs]
        
        rag_chain = build_rag_chain(retriever)
        answer = rag_chain.invoke(payload.question)

        return QueryResponse(
            question=payload.question,
            answer=answer,
            context=retrieved_chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
