import faiss
from sentence_transformers import SentenceTransformer

class Embed:
    def __init__(self, index_path=None):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)  # 384 dimensions for MiniLM model
        if index_path:
            self.index = faiss.read_index(index_path)

    def add_to_index(self, texts):
        embeddings = self.model.encode(texts)
        self.index.add(embeddings)
    
    def save_index(self, path):
        faiss.write_index(self.index, path)
    
    def search(self, query, top_k=5):
        query_embedding = self.model.encode([query])
        D, I = self.index.search(query_embedding, top_k)
        return I, D
