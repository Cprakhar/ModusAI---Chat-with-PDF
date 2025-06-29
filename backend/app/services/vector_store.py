import chromadb
from chromadb import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import re

class VectorStore:
    def __init__(self, persist_directory: str = "chroma_db", embedding_model: str = "all-MiniLM-L6-v2"):
        self.persist_directory = persist_directory
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.embedding_model = embedding_model
        self.embedder = SentenceTransformer(embedding_model)

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name)

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        texts = [chunk['text'] for chunk in chunks]
        return self.embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist()

    def add_chunks(self, collection_name: str, chunks: List[Dict[str, Any]]):
        collection = self.get_or_create_collection(collection_name)
        embeddings = self.embed_chunks(chunks)
        ids = [chunk['chunk_id'] for chunk in chunks]
        metadatas = [chunk['metadata'] | {"page": chunk['page']} for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def add_chunks_batch(self, collection_name: str, chunks: List[Dict[str, Any]], batch_size: int = 100):
        """
        Add chunks in batches for large documents.
        """
        for i in range(0, len(chunks), batch_size):
            self.add_chunks(collection_name, chunks[i:i+batch_size])

    def query(self, collection_name: str, query_text: str, n_results: int = 5, filters: Optional[Dict[str, Any]] = None, similarity_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        collection = self.get_or_create_collection(collection_name)
        query_embedding = self.embedder.encode([query_text], show_progress_bar=False, convert_to_numpy=True).tolist()
        # ChromaDB expects None, not empty dict, for no filters
        chroma_filters = filters if filters else None
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results * 2,  # get more for threshold filtering
            where=chroma_filters
        )
        # Optionally filter by similarity threshold
        scored_results = []
        for i, (id_, doc, meta, dist) in enumerate(zip(results["ids"][0], results["documents"][0], results["metadatas"][0], results["distances"][0])):
            if similarity_threshold is None or dist <= similarity_threshold:
                scored_results.append({
                    "id": id_,
                    "text": doc,
                    "metadata": meta,
                    "distance": dist
                })
        # Sort by distance (ascending)
        scored_results = sorted(scored_results, key=lambda x: x['distance'])
        return scored_results[:n_results]

    def keyword_search(self, collection_name: str, query_text: str, n_results: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Simple keyword search over documents in the collection.
        Returns top n_results with the most keyword overlap.
        """
        collection = self.get_or_create_collection(collection_name)
        # ChromaDB expects None, not empty dict, for no filters
        chroma_filters = filters if filters else None
        all_docs = collection.get()
        query_keywords = set(re.findall(r'\w+', query_text.lower()))
        scored = []
        for doc, meta, id_ in zip(all_docs['documents'], all_docs['metadatas'], all_docs['ids']):
            doc_keywords = set(re.findall(r'\w+', doc.lower()))
            overlap = len(query_keywords & doc_keywords)
            scored.append({
                'id': id_,
                'text': doc,
                'metadata': meta,
                'keyword_score': overlap
            })
        # Sort by keyword overlap (descending)
        scored = sorted(scored, key=lambda x: x['keyword_score'], reverse=True)
        return scored[:n_results]

    def hybrid_query(self, collection_name: str, query_text: str, n_results: int = 5, filters: Optional[Dict[str, Any]] = None, similarity_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Hybrid search: combine semantic and keyword search, re-rank by combined score.
        """
        # ChromaDB expects None, not empty dict, for no filters
        chroma_filters = filters if filters else None
        semantic_results = self.query(collection_name, query_text, n_results * 2, chroma_filters, similarity_threshold)
        keyword_results = self.keyword_search(collection_name, query_text, n_results * 2, chroma_filters)
        # Build a dict for fast lookup
        keyword_scores = {r['id']: r['keyword_score'] for r in keyword_results}
        # Combine: boost semantic results with keyword overlap
        for r in semantic_results:
            r['keyword_score'] = keyword_scores.get(r['id'], 0)
            r['hybrid_score'] = 1.0 + r['keyword_score']  # Simple: semantic + keyword
        # Sort by hybrid score
        ranked = sorted(semantic_results, key=lambda x: x['hybrid_score'], reverse=True)
        return ranked[:n_results]

    def list_collections(self) -> List[str]:
        return [col.name for col in self.client.list_collections()]

    def delete_collection(self, name: str):
        self.client.delete_collection(name)
