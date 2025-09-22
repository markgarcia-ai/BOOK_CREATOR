import chromadb
import sys
from typing import List, Dict, Any
from pathlib import Path

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="rag/db")
col = client.get_or_create_collection("book")

def fact_pack(query: str, k: int = 6) -> List[Dict[str, Any]]:
    """
    Retrieve fact packs for a query
    Returns list of fact pack items with citations
    """
    try:
        res = col.query(query_texts=[query], n_results=k)
        docs = res["documents"][0] if res["documents"] else []
        metas = res["metadatas"][0] if res["metadatas"] else []
        distances = res["distances"][0] if res["distances"] else []
        
        fact_packs = []
        for i, (doc, meta, distance) in enumerate(zip(docs, metas, distances)):
            # Calculate confidence from distance (lower distance = higher confidence)
            confidence = max(0.1, 1.0 - distance)
            
            # Extract citation key
            cite_key = meta.get("citeKey") or meta.get("source", f"source_{i}")
            
            # Extract source information
            source = {
                "title": meta.get("title") or meta.get("source", "Unknown Source"),
                "url": meta.get("url"),
                "page": meta.get("page"),
                "filename": meta.get("filename")
            }
            
            fact_packs.append({
                "text": doc,
                "citeKey": cite_key,
                "source": source,
                "confidence": round(confidence, 2)
            })
        
        return fact_packs
    except Exception as e:
        print(f"Error in fact_pack retrieval: {e}")
        return []

def search(q: str, k: int = 5) -> List[tuple]:
    """Legacy search function for backward compatibility"""
    fact_packs = fact_pack(q, k)
    return [(fp["text"], fp["source"]["title"]) for fp in fact_packs]

def get_collection_stats() -> Dict[str, Any]:
    """Get statistics about the RAG collection"""
    try:
        count = col.count()
        return {
            "document_count": count,
            "collection_name": "book",
            "status": "active"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        results = fact_pack(query)
        for i, fp in enumerate(results, 1):
            print(f"\n--- Fact Pack {i} ---")
            print(f"Text: {fp['text'][:200]}...")
            print(f"Source: {fp['source']['title']}")
            print(f"Confidence: {fp['confidence']}")
            print(f"Citation: {fp['citeKey']}")
    else:
        print("Usage: python retrieve.py <query>")
