"""
Configuration module for Book Creator
Centralized feature flags and settings management
"""
import os
from typing import Dict, Any

class Config:
    """Central configuration class for Book Creator"""
    
    # Feature Flags
    RAG_ENABLED: bool = True
    ENHANCED_LOGGING: bool = True
    PDF_GENERATION: bool = True
    
    # API Settings
    API_TIMEOUT: int = 300
    MAX_RETRIES: int = 3
    
    # RAG Settings
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 6
    
    # Generation Settings
    DEFAULT_TARGET_PAGES: int = 10
    DEFAULT_WORDS_PER_CHAPTER: int = 2000
    MAX_CHAPTERS: int = 50
    
    # File Paths
    BOOK_DIR: str = "book"
    EXPORTS_DIR: str = "exports" 
    UPLOADS_DIR: str = "uploads"
    RAG_DB_DIR: str = "rag/db"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def load_from_env(cls) -> None:
        """Load configuration from environment variables"""
        cls.RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
        cls.ENHANCED_LOGGING = os.getenv("ENHANCED_LOGGING", "true").lower() == "true"
        cls.PDF_GENERATION = os.getenv("PDF_GENERATION", "true").lower() == "true"
        
        cls.API_TIMEOUT = int(os.getenv("API_TIMEOUT", "300"))
        cls.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        
        cls.RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
        cls.RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
        cls.RAG_TOP_K = int(os.getenv("RAG_TOP_K", "6"))
        
        cls.DEFAULT_TARGET_PAGES = int(os.getenv("DEFAULT_TARGET_PAGES", "10"))
        cls.DEFAULT_WORDS_PER_CHAPTER = int(os.getenv("DEFAULT_WORDS_PER_CHAPTER", "2000"))
        cls.MAX_CHAPTERS = int(os.getenv("MAX_CHAPTERS", "50"))
        
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith('_') and not callable(getattr(cls, attr))
        }

# Load configuration from environment on import
Config.load_from_env() 