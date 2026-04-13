import bcrypt
import streamlit as st
from auth.database import get_connection

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(email: str, password: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    hashed = hash_password(password)
    try:
        c.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, hashed))
        conn.commit()
        return True
    except Exception as e:
        # e.g., sqlite3.IntegrityError when email exists
        return False
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> dict:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()

    if user and verify_password(password, user[2]):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user[0]
        st.session_state['email'] = user[1]
        return {"success": True, "user_id": user[0]}
    
    return {"success": False, "message": "Invalid email or password"}

def logout_user():
    for key in ['logged_in', 'user_id', 'email']:
        if key in st.session_state:
            del st.session_state[key]
