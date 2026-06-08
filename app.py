"""
Streamlit query interface for the IUI Unofficial Guide RAG system.
Run with: streamlit run app.py
"""
import streamlit as st
from vectorstore import get_collection
from rag import answer

st.set_page_config(page_title="IUI Unofficial Guide", page_icon="🎓", layout="centered")
st.title("🎓 IUI Unofficial Guide")
st.caption("Ask questions about CS/STEM professors and student life at Indiana University Indianapolis.")
st.markdown("*Answers are grounded in collected student reviews — the system will cite its sources.*")

@st.cache_resource(show_spinner="Loading knowledge base...")
def load_collection():
    return get_collection()

collection = load_collection()

query = st.text_input("Your question", placeholder="e.g. Is Yuni Xia a good professor for discrete math?")

if st.button("Ask", type="primary") and query.strip():
    with st.spinner("Searching and generating answer..."):
        result = answer(query, collection=collection)

    st.subheader("Answer")
    st.write(result["answer"])

    with st.expander("Retrieved chunks (context used)"):
        for i, chunk in enumerate(result["chunks"], 1):
            st.markdown(f"**Chunk {i}** — `{chunk['filename']}`")
            st.write(chunk["text"])
            st.markdown(f"[Source]({chunk['source_url']})")
            st.divider()
