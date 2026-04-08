import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import sys


'''
This is a simple-RAG implementation using the US FISS FoodKeeper dataset. 
The dataset contains information about various food items, including their storage, cooking, and safety guidelines.

What happens here is that we load the dataset, create embeddings for the content of each document (which can be a combination of search_text and content fields), 
and then when we get a query, we convert the query to an embedding and calculate the cosine similarity between the query embedding and the document embeddings to find the most relevant documents.

The top-k most relevant ones are returned as context for the LLM to answer queriees.

'''


class FoodKeeperRAG:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  ## Model for generating embeddings
        self.documents = None  ## To store the original documents (with content and metadata)
        self.embeddings = None  ## To store the generated embeddings for the documents
        self.is_loaded = False  ## Flag to check if data is loaded and embeddings are generated

    def load(self):
        '''loading the food_keepers data and creating embeddings'''

        if self.is_loaded:
            return

        ## First loading a embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        ## Loading all the docs
        all_docs = []

        dataset_dir = r'C:\Users\khare\Desktop\LLM_FINAL_PROJ\LLM-Project\Dataset_for_RAG'

        for filename in ['rag_cooking.jsonl', 'rag_storage.jsonl', 'rag_safety.jsonl']:
            file_path = os.path.join(dataset_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():  # Check if the line is not empty
                            all_docs.append(json.loads(line))


        self.documents = all_docs
        # print(f"Loaded {len(self.documents)} documents for FoodKeeper RAG.")


        ## Creating embeddings for all the documents
        contents = [f"{doc.get('search_text', '')} {doc.get('content', '')}" for doc in self.documents]        
        self.embeddings = self.model.encode(contents)
        # print("Generated embeddings for FoodKeeper RAG.")
        self.is_loaded = True


    def search(self, query, top_k=3):
        '''Search for relevant documents based on the query'''
        if not self.is_loaded:
            self.load()
        
        query_embedding = self.model.encode([query]) ## Convert query to embedding
        similarities =   np.dot(self.embeddings, query_embedding.T).flatten()  ## Cosine similarity between query embedding and document embeddings
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []

        for idx in top_k_indices:
            results.append({
                'food_name': self.documents[idx]['food_name'],
                'content': self.documents[idx]['content'],
                'type': self.documents[idx].get('type', 'unknown'),  ## type can be cooking, storage or safety (based on the document type in the dataset), defaulting to 'unknown' if not specified
                'score': float(similarities[idx])  ## Adding similarity score for reference
            })

        return results
    

    def get_context(self, query, top_k=3):
        '''Get the content of the top-k relevant documents for the query'''

        results = self.search(query, top_k)

        if not results:
            return "No relevant information found in FoodKeeper RAG."
        
        context_parts = []
        for r in results:
            context_parts.append(f"[{r['type'].upper()}] {r['food_name']}: {r['content']}, score: {r['score']:.4f}")

        return "\n\n---\n\n".join(context_parts)


_rag_instance = None

def get_rag():
    """Get the singleton RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = FoodKeeperRAG()
    return _rag_instance




## Testing a simple rag retrieval

if __name__ == "__main__":
    rag = get_rag()
    query = "How to store Shrimp"
    context = rag.get_context(query, top_k=3)
    print("Context retrieved from FoodKeeper RAG:")
    print(context)
    