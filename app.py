from flask import Flask, request, jsonify
from flask_cors import CORS
from auth.auth import register_user, authenticate_user
from backend.db_history import get_user_history, save_comparison
from utils.doc_parser import _extract_from_pdf, _extract_from_docx, clause_chunking
from embeddings.embedder import Embedder
from endee_integration.endee_db import endee_db
from backend.ai_analyzer import analyze_differences, extract_insights, summarize_document, rag_query
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}) # Explicitly allow frontend origin

# Initialize embedder globally (it's heavy, so load once)
embedder = Embedder()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    res = authenticate_user(email, password)
    if res["success"]:
        return jsonify(res), 200
    return jsonify({"error": res["message"]}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if register_user(email, password):
        return jsonify({"success": True}), 201
    return jsonify({"error": "Registration failed, email might exist."}), 400

@app.route('/api/history/<int:user_id>', methods=['GET'])
def history(user_id):
    docs = get_user_history(user_id)
    return jsonify(docs)

@app.route('/api/compare', methods=['POST'])
def compare():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "Must provide file1 and file2"}), 400
        
    user_id = request.form.get('user_id')
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    # Simple extraction
    def extract(f):
        if f.filename.endswith('.pdf'): return _extract_from_pdf(f)
        elif f.filename.endswith('.docx'): return _extract_from_docx(f)
        else: return f.read().decode('utf-8')
        
    text1 = extract(file1)
    text2 = extract(file2)
    
    chunks1 = clause_chunking(text1)
    chunks2 = clause_chunking(text2)
    
    emb1 = embedder.embed(chunks1)
    emb2 = embedder.embed(chunks2)
    
    collection_id = f"cmp_{user_id}"
    endee_db.clear(collection_id)
    endee_db.store(collection_id, chunks1, emb1, [{"source": file1.filename}] * len(chunks1))
    endee_db.store(collection_id, chunks2, emb2, [{"source": file2.filename}] * len(chunks2))
    
    best_scores = []
    for v1 in emb1:
        results = endee_db.search(collection_id, v1, top_k=1)
        if results:
            best_scores.append(results[0]["score"])
    avg_sim = float(np.mean(best_scores) * 100) if best_scores else 0.0
    
    summary = summarize_document(text2)
    diffs = analyze_differences(text1, text2)
    insights = extract_insights(text2)
    
    # Save comparison history
    try:
        save_comparison(user_id, file1.filename, file2.filename, avg_sim, summary, {"diff": diffs})
    except Exception as e:
        print("Failed to save history:", e)
    
    return jsonify({
        "similarity": avg_sim,
        "summary": summary,
        "diffs": diffs,
        "insights": insights
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    query = data.get('query')
    
    collection_id = f"cmp_{user_id}"
    if collection_id not in endee_db.collections or not endee_db.collections[collection_id]:
        return jsonify({"error": "No documents uploaded to database yet."}), 400
        
    q_vec = embedder.embed_single(query)
    results = endee_db.search(collection_id, q_vec, top_k=3)
    
    contexts = []
    for res in results:
        contexts.append(f"[{res['metadata'].get('source', 'Doc')}] {res['text']}")
    
    answer = rag_query(query, contexts)
    return jsonify({"answer": answer, "contexts": contexts})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
