"""
Enhanced RAG ingestion system with PDF and document support
"""
from pathlib import Path
import json
import sys
from sentence_transformers import SentenceTransformer
import chromadb
from .pdf_processor import DocumentProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize models and database
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
client = chromadb.PersistentClient(path="rag/db")
col = client.get_or_create_collection("book")
processor = DocumentProcessor()

def ingest_file(file_path: Path, chunk_size: int = 1000, overlap: int = 200):
    """Ingest a single file into the RAG system"""
    logger.info(f"Processing file: {file_path}")
    
    # Process the document
    document_chunks = processor.process_document(file_path)
    
    if not document_chunks:
        logger.warning(f"No content extracted from {file_path}")
        return 0
    
    total_chunks = 0
    
    for doc_chunk in document_chunks:
        text = doc_chunk['text']
        source = doc_chunk['source']
        page = doc_chunk.get('page', 1)
        doc_type = doc_chunk.get('type', 'unknown')
        
        # Further chunk the text if it's too long
        text_chunks = processor.chunk_text(text, chunk_size, overlap)
        
        for i, chunk_text in enumerate(text_chunks):
            if not chunk_text.strip():
                continue
                
            # Generate embedding
            embedding = model.encode([chunk_text], normalize_embeddings=True)[0].tolist()
            
            # Create unique ID
            chunk_id = f"{source}_{page}_{i}"
            
            # Create metadata
            metadata = {
                "source": source,
                "filename": source,
                "page": page,
                "chunk_index": i,
                "type": doc_type,
                "title": f"{source} - Page {page}",
                "citeKey": f"{source}_p{page}_{i}"
            }
            
            # Store in ChromaDB
            col.upsert(
                ids=[chunk_id],
                documents=[chunk_text],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            
            total_chunks += 1
    
    logger.info(f"Ingested {total_chunks} chunks from {file_path}")
    return total_chunks

def ingest_directory(directory_path: Path, chunk_size: int = 1000, overlap: int = 200):
    """Ingest all supported files from a directory"""
    if not directory_path.exists():
        logger.error(f"Directory does not exist: {directory_path}")
        return 0
    
    total_chunks = 0
    supported_files = []
    
    # Find all supported files
    for file_path in directory_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in processor.supported_formats:
            supported_files.append(file_path)
    
    logger.info(f"Found {len(supported_files)} supported files in {directory_path}")
    
    for file_path in supported_files:
        try:
            chunks = ingest_file(file_path, chunk_size, overlap)
            total_chunks += chunks
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")
    
    return total_chunks

def clear_collection():
    """Clear all data from the collection"""
    try:
        # Get all IDs and delete them
        results = col.get()
        if results['ids']:
            col.delete(ids=results['ids'])
            logger.info(f"Cleared {len(results['ids'])} documents from collection")
        else:
            logger.info("Collection is already empty")
    except Exception as e:
        logger.error(f"Failed to clear collection: {e}")

def get_collection_stats():
    """Get statistics about the collection"""
    try:
        results = col.get()
        total_docs = len(results['ids'])
        
        # Count by source
        sources = {}
        for metadata in results['metadatas']:
            source = metadata.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_documents": total_docs,
            "sources": sources,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

def main():
    """Main ingestion function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ingest.py <file_or_directory> [chunk_size] [overlap]")
        print("  python ingest.py --clear  # Clear collection")
        print("  python ingest.py --stats  # Show collection stats")
        return
    
    if sys.argv[1] == "--clear":
        clear_collection()
        return
    
    if sys.argv[1] == "--stats":
        stats = get_collection_stats()
        print(f"Collection stats: {json.dumps(stats, indent=2)}")
        return
    
    path = Path(sys.argv[1])
    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    overlap = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    
    if path.is_file():
        total_chunks = ingest_file(path, chunk_size, overlap)
    elif path.is_dir():
        total_chunks = ingest_directory(path, chunk_size, overlap)
    else:
        logger.error(f"Path does not exist: {path}")
        return
    
    print(f"Successfully ingested {total_chunks} chunks")
    
    # Show final stats
    stats = get_collection_stats()
    print(f"Collection now contains {stats['total_documents']} documents")

if __name__ == "__main__":
    main()
