"""
DDU AI Assistant - Streamlit Interactive Interface
Provides a quick, interactive web UI for testing the RAG engine directly with Streamlit.
"""

import os
import sys
import streamlit as st

# Add workspace root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from embeddings.indexer import ChromaIndexer
from backend.services.suggestion_service import SuggestionService
from backend.services.document_service import DocumentService
from backend.services.rag_service import RAGService
from backend.models.schemas import ChatRequest

st.set_page_config(
    page_title="DDU AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium look
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0b3c5d;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .source-box {
        background-color: #f1f5f9;
        border-left: 4px solid #328cc1;
        padding: 0.8rem;
        border-radius: 6px;
        margin-top: 0.5rem;
        font-size: 0.88rem;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #e0f2fe;
        color: #0369a1;
        margin-right: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_services():
    indexer = ChromaIndexer(
        persist_dir="./vectordb",
        collection_name="ddu_knowledge_base",
        data_dir="./data",
        uploads_dir="./data/raw_uploads"
    )
    suggestion_service = SuggestionService(config_path="./data/suggestions_config.json")
    document_service = DocumentService(indexer=indexer)
    rag_service = RAGService(indexer=indexer, suggestion_service=suggestion_service)

    # Initial check
    stats = indexer.get_stats()
    if stats["total_chunks"] == 0:
        indexer.rebuild_index()

    return indexer, suggestion_service, document_service, rag_service


indexer, suggestion_service, document_service, rag_service = init_services()

# Sidebar: Knowledge Base & Admin Controls
with st.sidebar:
    st.image("https://img.icons8.com/color/96/university.png", width=64)
    st.markdown("### DDU Knowledge Admin")
    
    stats = document_service.get_stats()
    st.metric("Total Indexed Chunks", stats.get("total_chunks", 0))
    st.metric("Indexed Documents", stats.get("total_documents", 0))
    
    st.markdown("---")
    st.markdown("#### Upload PDF / Knowledge File")
    uploaded_file = st.file_uploader("Upload Policy or Notice PDF", type=["pdf", "txt", "md"])
    if uploaded_file is not None:
        if st.button("Index Document", type="primary"):
            # Save file to uploads dir
            dest = os.path.join("./data/raw_uploads", uploaded_file.name)
            with open(dest, "wb") as f:
                f.write(uploaded_file.getbuffer())
            with st.spinner("Embedding and updating ChromaDB..."):
                res = indexer.ingest_single_file(dest)
                if res.get("success"):
                    st.success(f"Added {res.get('chunks_added')} chunks!")
                    st.rerun()
                else:
                    st.error(res.get("error"))

    if st.button("🔄 Rebuild Entire Index"):
        with st.spinner("Rebuilding ChromaDB index..."):
            indexer.rebuild_index()
            st.success("Vector DB Rebuilt!")
            st.rerun()


# Main Chat Interface
st.markdown('<div class="main-title">🎓 Dharmsinh Desai University (DDU) AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Instant, accurate answers with verified source citations for students, parents, and applicants.</div>', unsafe_allow_html=True)

# Guided Quick Actions
suggestions_data = suggestion_service.get_welcome_suggestions()
with st.expander("✨ Guided Topics & Quick Actions (Click to explore)", expanded=False):
    cols = st.columns(4)
    for idx, cat in enumerate(suggestions_data.primary_categories):
        col = cols[idx % 4]
        if col.button(f"{cat.icon} {cat.name}", key=f"cat_btn_{cat.id}"):
            st.session_state["selected_cat"] = cat.id

if "selected_cat" in st.session_state:
    cat_id = st.session_state["selected_cat"]
    subtopics = suggestion_service.get_subtopics_for_category(cat_id)
    st.info(f"Showing quick questions for **{cat_id.replace('_', ' ').title()}**:")
    sub_cols = st.columns(2)
    for idx, sub in enumerate(subtopics):
        if sub_cols[idx % 2].button(f"👉 {sub.label}", key=f"sub_{cat_id}_{idx}"):
            st.session_state["pending_query"] = sub.query

# Initialize session messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 Verified Sources & Citations"):
                for src in msg["sources"]:
                    st.markdown(f"**Document**: `{src['source']}` | **Category**: `{src['category']}` | **Match Score**: `{int(src['similarity_score'] * 100)}%`")
                    st.caption(f"Snippet: {src['snippet']}")

# Handle user input
user_query = st.chat_input("Ask about admissions, 75% attendance rule, fees, placements, scholarships...")
if "pending_query" in st.session_state and st.session_state["pending_query"]:
    user_query = st.session_state["pending_query"]
    st.session_state["pending_query"] = None

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Consulting DDU Knowledge Base..."):
            request = ChatRequest(query=user_query)
            response = rag_service.answer_query(request)
            
            st.markdown(response.answer)
            
            if response.sources:
                with st.expander(f"📚 Verified Sources ({len(response.sources)} citations)"):
                    for src in response.sources:
                        st.markdown(f"• **{src.source}** (Page {src.page or 1}) - *Category: {src.category}*")
                        st.caption(f'"{src.snippet}"')
            
            st.caption(f"⚡ Latency: {response.latency_ms}ms | Category: {response.category} | Confidence: {response.confidence}")
            
            if response.follow_up_suggestions:
                st.markdown("**Suggested Follow-ups:**")
                f_cols = st.columns(len(response.follow_up_suggestions))
                for f_idx, s in enumerate(response.follow_up_suggestions):
                    if f_cols[f_idx].button(s, key=f"follow_up_{len(st.session_state.messages)}_{f_idx}"):
                        st.session_state["pending_query"] = s
                        st.rerun()

            st.session_state.messages.append({
                "role": "assistant",
                "content": response.answer,
                "sources": [s.model_dump() for s in response.sources]
            })
