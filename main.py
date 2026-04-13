import streamlit as st
from frontend.app_pages import render_login_signup, render_dashboard, render_upload_compare, render_chat, render_history

st.set_page_config(page_title="SmartDoc AI", page_icon="📄", layout="wide")

def load_css():
    try:
        with open('frontend/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def load_particles():
    try:
        with open('frontend/particles.html', 'r') as f:
            st.components.v1.html(f.read(), height=0, width=0) # Hidden iframe running absolute fixed canvas
    except FileNotFoundError:
        pass
        
import streamlit.components.v1 as components

load_css()
load_particles()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    render_login_signup()
else:
    st.sidebar.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🤖 SmartDoc</h1>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<div style='text-align:center; color:#00D9F5;'>Welcome, <b>{st.session_state.get('email', 'User').split('@')[0]}</b></div><br>", unsafe_allow_html=True)
    
    page = st.sidebar.radio("Navigation", ["Dashboard", "Upload & Compare", "Chat with Documents", "History"])
    st.sidebar.markdown('<br><hr style="border: 1px solid rgba(0,245,160,0.2);">', unsafe_allow_html=True)
    if st.sidebar.button("Logout"):
        from auth.auth import logout_user
        logout_user()
        st.rerun()

    if page == "Dashboard":
        render_dashboard()
    elif page == "Upload & Compare":
        render_upload_compare()
    elif page == "Chat with Documents":
        render_chat()
    elif page == "History":
        render_history()
