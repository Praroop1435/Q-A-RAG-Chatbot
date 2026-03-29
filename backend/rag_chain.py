from typing import List

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnableLambda,
    RunnablePassthrough
)
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


def build_rag_chain(retriever):
    llm = HuggingFaceEndpoint(
        repo_id="deepseek-ai/DeepSeek-V3.2",
        task="text-generation",
        temperature=0.2,
        max_new_tokens=1024
    )  # type: ignore
    model = ChatHuggingFace(llm=llm)

    prompt = PromptTemplate(
        template="""You are a careful and helpful expert document analyst.

You are given excerpts from a PDF document. The text may be fragmented, conversational, or example-driven.

Your task:
- Answer the question using ONLY the information present in the document excerpts.
- You MAY synthesize, summarize, or group ideas that appear across multiple excerpts.
- You MUST NOT introduce topics, problems, or concepts that are not evidenced in the context.
- If the context only partially answers the question, state what IS covered and acknowledge what is missing.
- If the context truly contains no relevant information, say "The document does not contain information about this topic."

RULES:
1. Base your answer STRICTLY on the provided context. Never use outside knowledge.
2. When quoting or referencing specific parts, be precise.
3. Structure longer answers with bullet points for readability.
4. Do NOT hallucinate facts, figures, names, or dates not present in the context.
5. Be concise, factual, and grounded in the document context.

---
DOCUMENT CONTEXT:
{context}
---

USER QUESTION: {question}

ANSWER:""",
        input_variables=["context", "question"]
    )

    def format_docs(docs: List[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    parallel = RunnableParallel({
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    })

    return parallel | prompt | model | StrOutputParser()
