import streamlit as st
import json
from auth.auth import register_user, authenticate_user
from backend.db_history import get_user_history, save_comparison
from utils.doc_parser import extract_text_from_file, clause_chunking
from embeddings.embedder import Embedder
from endee_integration.endee_db import endee_db
from backend.ai_analyzer import analyze_differences, extract_insights, summarize_document, rag_query
import numpy as np
import time

@st.cache_resource
def get_embedder():
    return Embedder()

def render_login_signup():
    st.markdown("<h1 class='login-header'>SmartDoc AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='login-subheader'>Intelligent Document Comparator & Analyzer</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="metric-card" style="padding: 1.5rem;">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            l_email = st.text_input("Neon ID (Email)", key="l_email")
            l_password = st.text_input("Passcode", type="password", key="l_password")
            if st.button("Initialize Uplink"):
                res = authenticate_user(l_email, l_password)
                if res["success"]:
                    st.success("Access Granted.")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid Credentials.")
        
        with tab2:
            s_email = st.text_input("New Neon ID", key="s_email")
            s_password = st.text_input("Access Code", type="password", key="s_password")
            s_confirm = st.text_input("Verify Code", type="password", key="s_confirm")
            if st.button("Create Access Node"):
                if s_password != s_confirm:
                    st.error("Codes do not match")
                else:
                    if register_user(s_email, s_password):
                        st.success("Node constructed! You may now login.")
                    else:
                        st.error("ID already established in the grid.")
        st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard():
    st.markdown("<h2>Dashboard Overview</h2>", unsafe_allow_html=True)
    history = get_user_history(st.session_state['user_id'])
    
    # TOP CARDS
    col1, col2, col3 = st.columns(3)
    avg_sim = sum([h['similarity_score'] for h in history]) / len(history) if history else 0
    with col1:
        st.markdown(f'''
            <div class="metric-card">
                <h2>{len(history)}</h2>
                <p>Total Comparisons</p>
            </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
            <div class="metric-card" style="border-color: rgba(0,217,245,0.5);">
                <h2 style="background: linear-gradient(to right, #00D9F5, #FF6FD8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{avg_sim:.0f}%</h2>
                <p>Avg Similarity</p>
            </div>
        ''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''
            <div class="metric-card" style="border-color: rgba(255,111,216,0.5);">
                <h2 style="background: linear-gradient(to right, #FF6FD8, #00F5A0); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{len(history)*2}</h2>
                <p>Documents Analyzed</p>
            </div>
        ''', unsafe_allow_html=True)

    # MAIN SECTION
    st.markdown("<br><h3>Neural Activity Feed</h3>", unsafe_allow_html=True)
    
    if history:
        feed_html = ""
        for item in history[:5]:
            date_str = item['created_at'][:16]
            feed_html += f'''
            <div class="timeline-item">
                <div class="timeline-date">{date_str}</div>
                <div class="timeline-content">
                    Analyzed <b>{item['doc1_name']}</b> and <b>{item['doc2_name']}</b> 
                    <span style="color:#00F5A0; float:right;">{item['similarity_score']:.1f}% Match</span>
                </div>
            </div>
            '''
        st.markdown(feed_html, unsafe_allow_html=True)
    else:
        st.info("No neural activity detected. Proceed to Upload & Compare.")

def render_upload_compare():
    st.markdown("<h2>Upload & Compare Interface</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Feed documents into the Endee Vector grid.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        doc1 = st.file_uploader("Original Blueprint (v1)", type=["pdf", "docx", "txt"])
    with col2:
        doc2 = st.file_uploader("Modified Blueprint (v2)", type=["pdf", "docx", "txt"])
    
    if doc1 and doc2:
        if st.button("Initiate Synchronization & AI Diff"):
            with st.spinner("AI Thinking... Computing geometric embeddings in EndeeDB..."):
                text1 = extract_text_from_file(doc1)
                text2 = extract_text_from_file(doc2)
                
                chunks1 = clause_chunking(text1)
                chunks2 = clause_chunking(text2)
                
                st.session_state['doc1_name'] = doc1.name
                st.session_state['doc2_name'] = doc2.name
                
                embedder = get_embedder()
                emb1 = embedder.embed(chunks1)
                emb2 = embedder.embed(chunks2)
                
                collection_id = f"cmp_{st.session_state['user_id']}"
                endee_db.clear(collection_id)
                endee_db.store(collection_id, chunks1, emb1, [{"source": doc1.name}] * len(chunks1))
                endee_db.store(collection_id, chunks2, emb2, [{"source": doc2.name}] * len(chunks2))
                
                best_scores = []
                for v1 in emb1:
                    results = endee_db.search(collection_id, v1, top_k=1)
                    if results: best_scores.append(results[0]["score"])
                avg_sim = np.mean(best_scores) * 100 if best_scores else 0
                st.session_state['sim_score'] = avg_sim
                
                summary = summarize_document(text2)
                diffs = analyze_differences(text1, text2)
                insights = extract_insights(text2)
                
                st.session_state['ai_summary'] = summary
                st.session_state['ai_diff'] = diffs
                st.session_state['ai_insights'] = insights
                
                save_comparison(st.session_state['user_id'], doc1.name, doc2.name, avg_sim, summary, {"diff": diffs})
                st.rerun()

    if 'sim_score' in st.session_state:
        st.markdown("<hr style='border: 1px solid rgba(0, 245, 160, 0.3);'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>Synchronization Complete: <span style='color:#00F5A0;'>{st.session_state['sim_score']:.1f}%</span></h3>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["AI Logic Differences", "Risk/Insights", "Auto Summary"])
        with tab1:
            st.markdown("<div class='metric-card' style='text-align:left;'>", unsafe_allow_html=True)
            diff_text = st.session_state['ai_diff']
            if "ADDED" in diff_text or "REMOVED" in diff_text:
                st.markdown(diff_text.replace("ADDED", "<span class='added-text'>ADDED</span>")
                                  .replace("REMOVED", "<span class='removed-text'>REMOVED</span>")
                                  .replace("MODIFIED", "<span class='modified-text'>MODIFIED</span>"), unsafe_allow_html=True)
            else:
                st.markdown(diff_text)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab2:
            st.markdown("<div class='metric-card' style='text-align:left; border-color: rgba(0,217,245,0.3);'>", unsafe_allow_html=True)
            st.markdown(st.session_state['ai_insights'])
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab3:
            st.markdown("<div class='metric-card' style='text-align:left; border-color: rgba(255,111,216,0.3);'>", unsafe_allow_html=True)
            st.markdown(st.session_state['ai_summary'])
            st.markdown("</div>", unsafe_allow_html=True)

def render_chat():
    st.markdown("<h2>AI Chat Interface</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Retrieve exact clauses from Endee Memory Banks.</p>", unsafe_allow_html=True)
    
    collection_id = f"cmp_{st.session_state['user_id']}"
    if collection_id not in endee_db.collections or not endee_db.collections[collection_id]:
        st.warning("Memory Banks empty. Please upload documents first.")
        return
        
    query = st.text_input("Enter Query:")
    if st.button("Transmit"):
        if query:
            with st.spinner("Accessing Endee DB..."):
                embedder = get_embedder()
                q_vec = embedder.embed_single(query)
                results = endee_db.search(collection_id, q_vec, top_k=3)
                
                contexts = [f"[{r['metadata'].get('source', 'Doc')}] {r['text']}" for r in results]
                answer = rag_query(query, contexts)
            
            st.markdown(f"<div class='metric-card' style='text-align:left;'><p style='color:#00F5A0; font-size:1.2rem; font-weight:800;'>AI Response</p><p style='color:#FFF;'>{answer}</p></div>", unsafe_allow_html=True)
            
            with st.expander("View Deep Node Contexts"):
                for c in contexts:
                    st.write(f"- {c}")

def render_history():
    st.markdown("<h2>Memory Logs</h2>", unsafe_allow_html=True)
    history = get_user_history(st.session_state['user_id'])
    
    if not history:
        st.info("No chronological data available.")
        return
        
    for item in history:
        st.markdown(f'''
        <div class="metric-card" style="text-align:left; border-color: rgba(255,255,255,0.1); margin-bottom: 20px; padding: 1.5rem;">
            <h4 style="margin:0;">{item['doc1_name']} vs {item['doc2_name']} <span style="font-size:1rem; color:#00D9F5;">({item['similarity_score']:.1f}%)</span></h4>
            <span class="timeline-date">{item['created_at']}</span>
            <p style="color:#FFF; font-size: 0.95rem; margin-top: 10px;">{item['ai_summary'][:300]}...</p>
        </div>
        ''', unsafe_allow_html=True)
