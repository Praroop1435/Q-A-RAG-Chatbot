import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="PDF Q&A System", page_icon="📄")

st.title("📄 PDF Q&A System (Gemini RAG)")

if "ingested" not in st.session_state:
    st.session_state.ingested = False

st.sidebar.header("Upload Document")
uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    if st.sidebar.button("Process Document"):
        with st.spinner("Processing PDF and creating vector embeddings..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{BACKEND_URL}/ingest", files=files)
                
                if response.status_code == 200:
                    st.sidebar.success("Document successfully processed and indexed!")
                    st.session_state.ingested = True
                else:
                    st.sidebar.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.sidebar.error(f"Failed to connect to backend: {e}")

st.header("Ask Questions")
question = st.text_input("Enter your question about the uploaded document:")

if st.button("Submit Question"):
    if not st.session_state.ingested:
        st.warning("Please upload and process a document first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating answer..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/query",
                    json={"question": question}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.info("Answer:")
                    st.write(data["answer"])
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
