import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'smartdoc_history.db')

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_history_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doc1_name TEXT NOT NULL,
            doc2_name TEXT NOT NULL,
            similarity_score REAL NOT NULL,
            ai_summary TEXT,
            differences_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_comparison(user_id, doc1_name, doc2_name, similarity_score, ai_summary, differences):
    """
    differences is expected to be a dictionary or list, which will be json.dumps'd
    """
    diff_json = json.dumps(differences)
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO comparisons (user_id, doc1_name, doc2_name, similarity_score, ai_summary, differences_json)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, doc1_name, doc2_name, similarity_score, ai_summary, diff_json))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, doc1_name, doc2_name, similarity_score, created_at, ai_summary
        FROM comparisons
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    for r in rows:
        history.append({
            "id": r[0],
            "doc1_name": r[1],
            "doc2_name": r[2],
            "similarity_score": r[3],
            "created_at": r[4],
            "ai_summary": r[5]
        })
    return history

init_history_db()
