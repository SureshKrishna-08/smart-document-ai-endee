import PyPDF2
import docx
import re

def extract_text_from_file(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return _extract_from_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return _extract_from_docx(uploaded_file)
    elif name.endswith(".txt"):
        return str(uploaded_file.read(), "utf-8")
    else:
        return "Unsupported format"

def _extract_from_pdf(file_obj):
    pdf = PyPDF2.PdfReader(file_obj)
    text = ""
    for page in pdf.pages:
        t = page.extract_text()
        if t: text += t + "\n"
    return text

def _extract_from_docx(file_obj):
    doc = docx.Document(file_obj)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def chunk_text(text, chunk_size=500, overlap=50):
    """Fallback structural chunking for RAG."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def clause_chunking(text):
    """Intelligent parsing attempting to split by paragraph/clause."""
    # Split on double newlines
    clauses = re.split(r'\n\s*\n', text)
    valid_clauses = [c.strip() for c in clauses if len(c.strip()) > 20]
    if len(valid_clauses) < 2 and len(text) > 1000:
        # Fallback if no clean newlines
        return chunk_text(text, chunk_size=100, overlap=0)
    return valid_clauses
