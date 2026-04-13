import os
import openai
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return openai.OpenAI(api_key=api_key)

def summarize_document(text):
    client = get_openai_client()
    if not client: return "OpenAI API Key not configured. Please add it in settings or .env file."
    
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a legal AI assistant. Summarize the following document accurately, highlighting key topics and obligations."},
                      {"role": "user", "content": text[:15000]}]  # truncate to fit model context safely
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def extract_insights(text):
    client = get_openai_client()
    if not client: return "OpenAI API Key not configured."
    
    prompt = f"Analyze the following document and identify 3 potential risks or improvements:\n\n{text[:15000]}"
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an expert AI risk assessor for documents. Provide bulleted insights."},
                      {"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def compare_clauses(clause1, clause2):
    client = get_openai_client()
    if not client: return "API Key missing"
    
    prompt = f"Doc 1 Clause: {clause1}\n\nDoc 2 Clause: {clause2}\n\nAnalyze the differences. State if it is slightly modified or meaning difference. Highlight the specific changes concisely."
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a strict, precise document comparison AI."},
                      {"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_differences(text1, text2):
    client = get_openai_client()
    if not client: return "API Key missing"
    
    prompt = f"Compare these two document excerpts and list what was ADDED, REMOVED, and MODIFIED.\n\nDoc1:\n{text1[:5000]}\n\nDoc2:\n{text2[:5000]}"
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a comparison engine. Output a strict JSON-like structured format or clear sections: ADDED:, REMOVED:, MODIFIED:."},
                      {"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def rag_query(query, retrieved_contexts):
    client = get_openai_client()
    if not client: return "Error: API Key missing"
    
    context_str = "\n---\n".join(retrieved_contexts)
    prompt = f"Answer the user's query based ONLY on the provided context.\n\nContext:\n{context_str}\n\nQuery: {query}"
    
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You answer user questions intelligently relying on provided document excerpts."},
                      {"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
