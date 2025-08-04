import sys
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import processor
from src.processor import process_all

def create_embeddings():
    chunks = process_all()
    print(f"Processing {len(chunks)} text chunks...")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)
    print(f"Created embeddings with dimension: {embeddings.shape[1]}")
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    # Save embeddings
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vector_store_path = os.path.join(base_dir, 'embeddings', 'vector_store')
    os.makedirs(vector_store_path, exist_ok=True)
    
    faiss.write_index(index, os.path.join(vector_store_path, 'faiss_index.bin'))
    
    with open(os.path.join(vector_store_path, 'chunks.txt'), 'w', encoding='utf-8') as f:
        f.write("\n".join(chunks))
    
    print(f"Saved embeddings to {vector_store_path}")

if __name__ == "__main__":
    create_embeddings()