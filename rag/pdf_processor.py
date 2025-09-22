"""
PDF and document processing for RAG system
"""
import fitz  # PyMuPDF
import PyPDF2
from docx import Document
from pathlib import Path
import re
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process various document formats for RAG ingestion"""
    
    def __init__(self):
        self.supported_formats = {'.pdf', '.docx', '.txt', '.md'}
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF with page information"""
        try:
            # Try PyMuPDF first (better for complex PDFs)
            doc = fitz.open(pdf_path)
            chunks = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():
                    chunks.append({
                        'text': text.strip(),
                        'page': page_num + 1,
                        'source': pdf_path.name,
                        'type': 'pdf'
                    })
            
            doc.close()
            logger.info(f"Extracted {len(chunks)} pages from PDF: {pdf_path.name}")
            return chunks
            
        except Exception as e:
            logger.warning(f"PyMuPDF failed for {pdf_path.name}: {e}")
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    chunks = []
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        if text.strip():
                            chunks.append({
                                'text': text.strip(),
                                'page': page_num + 1,
                                'source': pdf_path.name,
                                'type': 'pdf'
                            })
                    
                    logger.info(f"Extracted {len(chunks)} pages from PDF (PyPDF2): {pdf_path.name}")
                    return chunks
                    
            except Exception as e2:
                logger.error(f"Both PDF extraction methods failed for {pdf_path.name}: {e2}")
                return []
    
    def extract_text_from_docx(self, docx_path: Path) -> List[Dict[str, Any]]:
        """Extract text from DOCX file"""
        try:
            doc = Document(docx_path)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text.strip())
            
            # Combine all text
            full_text = '\n\n'.join(text_parts)
            
            return [{
                'text': full_text,
                'page': 1,
                'source': docx_path.name,
                'type': 'docx'
            }]
            
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX {docx_path.name}: {e}")
            return []
    
    def extract_text_from_txt(self, txt_path: Path) -> List[Dict[str, Any]]:
        """Extract text from plain text file"""
        try:
            text = txt_path.read_text(encoding='utf-8')
            return [{
                'text': text,
                'page': 1,
                'source': txt_path.name,
                'type': 'txt'
            }]
        except Exception as e:
            logger.error(f"Failed to read text file {txt_path.name}: {e}")
            return []
    
    def extract_text_from_markdown(self, md_path: Path) -> List[Dict[str, Any]]:
        """Extract text from markdown file"""
        try:
            text = md_path.read_text(encoding='utf-8')
            return [{
                'text': text,
                'page': 1,
                'source': md_path.name,
                'type': 'markdown'
            }]
        except Exception as e:
            logger.error(f"Failed to read markdown file {md_path.name}: {e}")
            return []
    
    def process_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a document and return text chunks"""
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return []
        
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif suffix == '.docx':
            return self.extract_text_from_docx(file_path)
        elif suffix == '.txt':
            return self.extract_text_from_txt(file_path)
        elif suffix == '.md':
            return self.extract_text_from_markdown(file_path)
        else:
            logger.warning(f"Unsupported file format: {suffix}")
            return []
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(start + chunk_size - 100, start)
                sentence_end = text.rfind('.', search_start, end)
                if sentence_end > search_start:
                    end = sentence_end + 1
                else:
                    # Look for paragraph breaks
                    para_end = text.rfind('\n\n', search_start, end)
                    if para_end > search_start:
                        end = para_end + 2
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks

def main():
    """Test the document processor"""
    processor = DocumentProcessor()
    
    # Test with a sample file if it exists
    test_files = [
        Path("rag/db/sample.pdf"),
        Path("uploads/sample.md"),
        Path("book/chapters/01-introduction.md")
    ]
    
    for test_file in test_files:
        if test_file.exists():
            print(f"\nProcessing: {test_file}")
            chunks = processor.process_document(test_file)
            for i, chunk in enumerate(chunks):
                print(f"Chunk {i+1}: {chunk['text'][:100]}...")
            break
    else:
        print("No test files found. Place a PDF or other document in rag/db/ to test.")

if __name__ == "__main__":
    main()
