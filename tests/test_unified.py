#!/usr/bin/env python3
"""
Unified Test Suite for Book Creator
Consolidates all testing functionality
"""

import unittest
import requests
import time
import sys
import os
from pathlib import Path
import json
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class BookCreatorTestSuite(unittest.TestCase):
    """Unified test suite for Book Creator"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.base_url = "http://127.0.0.1:8000"
        cls.session = requests.Session()
        cls.test_timeout = 60
        cls.features = {}
        cls.config = {}
        
        # Test server connection
        if not cls._test_server_connection():
            raise unittest.SkipTest("Server not available")
        
        # Get server features
        cls._load_server_info()
    
    @classmethod
    def _test_server_connection(cls) -> bool:
        """Test if server is running"""
        try:
            response = cls.session.get(f"{cls.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    @classmethod
    def _load_server_info(cls):
        """Load server features and configuration"""
        try:
            response = cls.session.get(f"{cls.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                cls.features = data.get("features", {})
                cls.config = data.get("config", {})
        except:
            pass
    
    def test_server_health(self):
        """Test server health endpoint"""
        response = self.session.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("version", data)
        self.assertIn("features", data)
    
    def test_configuration_endpoint(self):
        """Test configuration endpoint"""
        response = self.session.get(f"{self.base_url}/config")
        self.assertEqual(response.status_code, 200)
        
        config = response.json()
        self.assertIsInstance(config, dict)
        self.assertIn("RAG_ENABLED", config)
        self.assertIn("ENHANCED_LOGGING", config)
    
    def test_styles_endpoint(self):
        """Test book styles endpoint"""
        response = self.session.get(f"{self.base_url}/styles")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("styles", data)
        self.assertIsInstance(data["styles"], list)
        self.assertGreater(len(data["styles"]), 0)
    
    def test_outline_generation(self):
        """Test outline generation"""
        request_data = {
            "topic": "Test Topic",
            "target_audience": "Test audience", 
            "style": "informative",
            "target_pages": 5
        }
        
        response = self.session.post(
            f"{self.base_url}/generate-outline",
            json=request_data,
            timeout=self.test_timeout
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("outline", data)
        
        outline = data["outline"]
        self.assertIn("chapters", outline)
        self.assertIsInstance(outline["chapters"], list)
    
    def test_simple_workflow(self):
        """Test simple workflow"""
        request_data = {
            "topic": "Test Simple Workflow",
            "chapters": 3,
            "words_per_chapter": 500
        }
        
        response = self.session.post(
            f"{self.base_url}/simple-workflow",
            json=request_data,
            timeout=self.test_timeout
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get("success"))
    
    def test_agent_workflow(self):
        """Test reasoning agent"""
        request_data = {
            "goal": "Generate a simple test outline",
            "max_steps": 3,
            "model": "claude-3-5-sonnet-20241022"
        }
        
        response = self.session.post(
            f"{self.base_url}/agent/run",
            json=request_data,
            timeout=self.test_timeout
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("result", data)
        self.assertIn("trace", data)
    
    def test_book_generation_basic(self):
        """Test basic book generation"""
        request_data = {
            "title": "Test Book",
            "target_audience": "Test audience",
            "style": "informative", 
            "target_pages": 3,
            "chapters": 2,
            "book_style": "modern",
            "use_rag": False
        }
        
        response = self.session.post(
            f"{self.base_url}/generate-book",
            json=request_data,
            timeout=120  # Longer timeout for book generation
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("title", data)
        self.assertIn("chapters", data)
        self.assertIn("files", data)
        
        files = data["files"]
        self.assertIn("markdown", files)
        self.assertIn("html", files)
    
    @unittest.skipUnless(os.getenv("TEST_RAG", "false").lower() == "true", "RAG tests disabled")
    def test_rag_functionality(self):
        """Test RAG functionality (if enabled)"""
        if not self.features.get("rag_enabled", False):
            self.skipTest("RAG not enabled")
        
        # Test RAG stats
        response = self.session.get(f"{self.base_url}/rag/stats")
        self.assertEqual(response.status_code, 200)
        
        stats = response.json()
        self.assertIn("document_count", stats)
        
        # Test RAG query
        response = self.session.post(
            f"{self.base_url}/rag/query",
            data={"query": "test query", "k": 3}
        )
        self.assertEqual(response.status_code, 200)
    
    @unittest.skipUnless(os.getenv("TEST_RAG", "false").lower() == "true", "RAG tests disabled")
    def test_rag_enhanced_generation(self):
        """Test RAG-enhanced book generation"""
        if not self.features.get("rag_enabled", False):
            self.skipTest("RAG not enabled")
        
        request_data = {
            "title": "Test RAG Book",
            "target_audience": "Test audience",
            "style": "technical",
            "target_pages": 3,
            "chapters": 2,
            "book_style": "academic",
            "use_rag": True,
            "rag_query": "test machine learning"
        }
        
        response = self.session.post(
            f"{self.base_url}/generate-book",
            json=request_data,
            timeout=120
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertTrue(data.get("rag_enhanced", False))
    
    def test_custom_styles(self):
        """Test custom style generation"""
        request_data = {
            "title": "Custom Style Test Book",
            "target_audience": "Test audience",
            "style": "informative",
            "target_pages": 3,
            "chapters": 2,
            "book_style": "modern",
            "font_family": "Arial",
            "line_height": "1.5",
            "color_scheme": "blue",
            "use_rag": False
        }
        
        response = self.session.post(
            f"{self.base_url}/generate-book",
            json=request_data,
            timeout=120
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get("success"))
    
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid endpoint
        response = self.session.get(f"{self.base_url}/invalid-endpoint")
        self.assertEqual(response.status_code, 404)
        
        # Test invalid request data
        response = self.session.post(
            f"{self.base_url}/generate-outline",
            json={"invalid": "data"}
        )
        self.assertIn(response.status_code, [400, 422])  # Bad request or validation error
    
    def test_performance_outline(self):
        """Test outline generation performance"""
        start_time = time.time()
        
        request_data = {
            "topic": "Performance Test Topic",
            "target_audience": "General audience",
            "style": "informative",
            "target_pages": 10
        }
        
        response = self.session.post(
            f"{self.base_url}/generate-outline",
            json=request_data,
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 30)  # Should complete within 30 seconds
        
        data = response.json()
        self.assertTrue(data.get("success"))

class ImportTestSuite(unittest.TestCase):
    """Test imports and dependencies"""
    
    def test_backend_imports(self):
        """Test backend module imports"""
        try:
            from backend import llm, planner, writer, tools, settings
            from backend.book_styles import get_style, list_styles
            from backend.config import Config
        except ImportError as e:
            self.fail(f"Backend import failed: {e}")
    
    def test_optional_rag_imports(self):
        """Test optional RAG imports"""
        try:
            from rag import retrieve, ingest
            from rag.pdf_processor import DocumentProcessor
        except ImportError:
            # RAG imports are optional
            pass
    
    def test_required_dependencies(self):
        """Test required dependencies"""
        required_modules = [
            "anthropic", "fastapi", "uvicorn", "typer", 
            "rich", "pydantic", "requests"
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError as e:
                self.fail(f"Required dependency {module} not available: {e}")

class FileSystemTestSuite(unittest.TestCase):
    """Test file system operations"""
    
    def setUp(self):
        """Set up test directories"""
        self.root_dir = Path(__file__).parent.parent
        self.book_dir = self.root_dir / "book"
        self.exports_dir = self.root_dir / "exports"
    
    def test_directory_structure(self):
        """Test required directory structure"""
        required_dirs = [
            "backend", "scripts", "book", "exports", 
            "prompts", "rag"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.root_dir / dir_name
            self.assertTrue(dir_path.exists(), f"Directory {dir_name} not found")
            self.assertTrue(dir_path.is_dir(), f"{dir_name} is not a directory")
    
    def test_required_files(self):
        """Test required files exist"""
        required_files = [
            "backend/__init__.py",
            "backend/main.py", 
            "backend/llm.py",
            "backend/config.py",
            "scripts/cli.py",
            "requirements.txt",
            "README.md"
        ]
        
        for file_path in required_files:
            full_path = self.root_dir / file_path
            self.assertTrue(full_path.exists(), f"Required file {file_path} not found")
    
    def test_exports_directory_writable(self):
        """Test exports directory is writable"""
        test_file = self.exports_dir / "test_write.txt"
        try:
            test_file.write_text("test")
            self.assertTrue(test_file.exists())
            test_file.unlink()  # Clean up
        except Exception as e:
            self.fail(f"Cannot write to exports directory: {e}")

def run_tests(test_type: str = "all", verbose: bool = False):
    """Run tests with specified configuration"""
    
    # Configure test verbosity
    verbosity = 2 if verbose else 1
    
    # Create test suites
    loader = unittest.TestLoader()
    
    if test_type == "all":
        # Run all tests
        suites = [
            loader.loadTestsFromTestCase(BookCreatorTestSuite),
            loader.loadTestsFromTestCase(ImportTestSuite),
            loader.loadTestsFromTestCase(FileSystemTestSuite)
        ]
        suite = unittest.TestSuite(suites)
    elif test_type == "api":
        suite = loader.loadTestsFromTestCase(BookCreatorTestSuite)
    elif test_type == "imports":
        suite = loader.loadTestsFromTestCase(ImportTestSuite)
    elif test_type == "filesystem":
        suite = loader.loadTestsFromTestCase(FileSystemTestSuite)
    else:
        raise ValueError(f"Unknown test type: {test_type}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Book Creator Test Suite")
    parser.add_argument("--type", choices=["all", "api", "imports", "filesystem"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--rag", action="store_true", help="Include RAG tests")
    
    args = parser.parse_args()
    
    # Set environment variable for RAG tests
    if args.rag:
        os.environ["TEST_RAG"] = "true"
    
    # Run tests
    success = run_tests(args.type, args.verbose)
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 