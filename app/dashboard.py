import pandas as pd
import requests
import streamlit as st

API_URL = st.sidebar.text_input("API URL", "http://api:8000")
st.set_page_config(page_title="Document Operations", page_icon="📄", layout="wide")
st.title("AI-Assisted Document Operations")
st.caption("Extraction, confidence scoring, exception handling, and human review")

uploaded = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
if uploaded and st.button("Process document", type="primary"):
    response = requests.post(f"{API_URL}/documents", files={"file": (uploaded.name, uploaded.getvalue())}, timeout=60)
    if response.ok:
        st.success("Document processed")
    else:
        st.error(response.text)

try:
    items = requests.get(f"{API_URL}/documents", timeout=10).json()
except requests.RequestException:
    st.warning("API is unavailable. Start the Docker stack first.")
    st.stop()

if items:
    frame = pd.DataFrame(items)
    c1, c2, c3 = st.columns(3)
    c1.metric("Documents", len(frame))
    c2.metric("Needs review", int((frame.status == "needs_review").sum()))
    c3.metric("Average confidence", f"{frame.confidence.mean():.0%}")
    st.bar_chart(frame.document_type.value_counts())

    pending = frame[frame.status == "needs_review"]
    if not pending.empty:
        st.subheader("Human review queue")
        selected = st.selectbox("Document", pending.id, format_func=lambda x: pending.loc[pending.id == x, "filename"].iloc[0])
        row = pending[pending.id == selected].iloc[0]
        st.json(row.extracted_data)
        note = st.text_input("Reviewer note")
        a, b = st.columns(2)
        if a.button("Approve"):
            requests.post(f"{API_URL}/documents/{selected}/review", json={"decision": "approved", "note": note}, timeout=10)
            st.rerun()
        if b.button("Reject"):
            requests.post(f"{API_URL}/documents/{selected}/review", json={"decision": "rejected", "note": note}, timeout=10)
            st.rerun()
    st.subheader("Document registry")
    st.dataframe(frame[["id", "filename", "document_type", "status", "confidence", "created_at"]], use_container_width=True)
else:
    st.info("Upload the first sample document to begin.")
