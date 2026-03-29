import streamlit as st
import requests
import time

BACKEND_URL = "http://localhost:8000"

# --- Page Configuration ---
st.set_page_config(
    page_title="LLM Engine (Streamlit Edition)", 
    page_icon="🖥️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- Dark Monochrome Aesthetic via Custom CSS ---
st.markdown("""
<style>
/* Base background, text color & font to match anjan.site */
[data-testid="stAppViewContainer"] {
    background-color: #000000;
    color: #fafafa;
    font-family: 'Courier New', Courier, monospace;
}
[data-testid="stSidebar"] {
    background-color: #0a0a0a;
    border-right: 1px solid #262626;
}
[data-testid="stHeader"] {
    background-color: transparent;
}
/* Override inputs & buttons */
div.stButton > button {
    background-color: #0a0a0a;
    color: #FAFAFA;
    border: 1px solid #262626;
    border-radius: 4px;
    font-family: monospace;
    transition: all 0.3s;
    width: 100%;
}
div.stButton > button:hover {
    background-color: #1a1a1a;
    border-color: #555555;
    color: #ffffff;
}
/* Style Chat Inputs and Text Fields */
[data-baseweb="input"] {
    background-color: #0a0a0a !important;
    border: 1px solid #262626 !important;
    color: #fafafa !important;
}
/* Metrics */
[data-testid="stMetricValue"] {
    font-size: 1.5rem;
    color: #FAFAFA;
}
[data-testid="stMetricLabel"] {
    font-family: monospace;
    color: #a3a3a3;
    letter-spacing: 1px;
    font-size: 0.8rem;
    text-transform: uppercase;
}
/* Chat bubbbles */
[data-testid="chatAvatarIcon-user"] {
    background-color: #262626;
}
[data-testid="chatAvatarIcon-assistant"] {
    background-color: #1a1a1a;
}
/* Dividers: Hatched Pattern (anjan.site style) */
hr {
    border: 0;
    height: 4px;
    background-image: repeating-linear-gradient(
        45deg,
        #262626,
        #262626 1px,
        transparent 1px,
        transparent 8px
    );
    margin: 1.5rem 0;
}
/* Remove explicit top padding to make it truly wide and flush */
.block-container {
    padding-top: 3rem;
    padding-bottom: 0rem;
    max-width: 95%;
}
</style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ingested" not in st.session_state:
    st.session_state.ingested = False
if "doc_chunks" not in st.session_state:
    st.session_state.doc_chunks = 0

# --- Layout Grid ---
col_left, col_right = st.columns([1, 2.5], gap="large")

with col_left:
    st.markdown("### 🖥️ LLM ENGINE")
    st.caption("Streamlit Edge Deployment")
    st.markdown("---")
    
    st.markdown("##### KNOWLEDGE SOURCE")
    uploaded_file = st.file_uploader("Upload Context", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file and not st.session_state.ingested:
        if st.button("Index Document Engine"):
            with st.spinner("Extracting & Vectorizing..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    res = requests.post(f"{BACKEND_URL}/ingest", files=files)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.ingested = True
                        st.session_state.doc_chunks = data.get("chunks", 0)
                        st.success("Indexed.")
                        st.rerun()
                    else:
                        st.error(f"Failed: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error("Backend offline.")
    elif st.session_state.ingested:
        st.success(f"✓ Encoded: {uploaded_file.name if uploaded_file else 'Document'}")
        if st.button("Reset Knowledge Base"):
            st.session_state.ingested = False
            st.session_state.messages = []
            st.session_state.doc_chunks = 0
            st.rerun()
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("##### SYSTEM TELEMETRY")
    st.metric(label="FastAPI Backend", value="ONLINE 🟢")
    if st.session_state.ingested:
        st.metric(label="Vector DB Chunks", value=f"{st.session_state.doc_chunks}")
        
    st.markdown("---")

with col_right:
    st.markdown("##### INTERACTIVE TERMINAL")
    
    # Render messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Feature: RAG visualizer
            if msg.get("context") and len(msg["context"]) > 0:
                with st.expander(f"View {len(msg['context'])} Retrieved Snippets"):
                    for idx, chunk in enumerate(msg["context"]):
                        st.caption(f"**Chunk {idx+1}**")
                        st.markdown(f"> {chunk}")

    if not st.session_state.ingested:
        st.info("Awaiting knowledge injection. Please upload and index a PDF on the left.")
    else:
        # Pushing the input lower using some empty space
        st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Input Area at bottom
    if prompt := st.chat_input("Execute semantic query...", disabled=not st.session_state.ingested):
        
        # Display user query
        st.session_state.messages.append({"role": "user", "content": prompt, "context": []})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Display assistant computing
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("`system.retrieval: Vectorizing intent and scanning database...`")
            
            try:
                res = requests.post(f"{BACKEND_URL}/query", json={"question": prompt})
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    context = data.get("context", [])
                    
                    # Streaming typing effect visually
                    def stream_text(text):
                        for word in text.split(" "):
                            yield word + " "
                            time.sleep(0.02)
                            
                    message_placeholder.write_stream(stream_text(answer))
                    
                    if context:
                        with st.expander(f"View {len(context)} Retrieved Snippets"):
                            for idx, chunk in enumerate(context):
                                st.caption(f"**Chunk {idx+1}**")
                                st.markdown(f"> {chunk}")
                                
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "context": context
                    })
                else:
                    message_placeholder.error(f"Error: {res.text}")
            except Exception as e:
                message_placeholder.error("Backend connection failed.")
