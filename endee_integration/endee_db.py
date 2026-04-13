import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import uuid

class EndeeVectorDB:
    """ Mock for Endee Vector Database using numpy for storing embeddings locally.
    In a real-world scenario, this abstraction would wrap the Endee SDK or REST API.
    """
    def __init__(self):
        self.collections = {} # map collection_name -> list of dict(id, text, vector, metadata)
        
    def store(self, collection_name, texts, embeddings, metadatas=None):
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        
        for i, text in enumerate(texts):
            doc = {
                "id": str(uuid.uuid4()),
                "text": text,
                "vector": embeddings[i],
                "metadata": metadatas[i] if metadatas else {}
            }
            self.collections[collection_name].append(doc)

    def search(self, collection_name, query_vector, top_k=3):
        if collection_name not in self.collections or not self.collections[collection_name]:
            return []
        
        docs = self.collections[collection_name]
        db_vectors = [d["vector"] for d in docs]
        
        # Calculate cosine similarities
        sims = cosine_similarity([query_vector], db_vectors)[0]
        
        # Get top k indices sorted descending
        top_indices = np.argsort(sims)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "score": float(sims[idx]),
                "text": docs[idx]["text"],
                "metadata": docs[idx]["metadata"]
            })
        return results

    def clear(self, collection_name):
        if collection_name in self.collections:
            self.collections[collection_name] = []

# Global instance for the session
endee_db = EndeeVectorDB()
