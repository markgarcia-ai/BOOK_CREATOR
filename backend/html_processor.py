"""
HTML Processing Module for Google Docs Integration
Handles HTML files exported from Google Docs and converts them to enhanced book content
"""

import os
import re
import base64
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from bs4 import BeautifulSoup
import zipfile
import tempfile
import shutil

logger = logging.getLogger(__name__)

class HTMLProcessor:
    """Process HTML files exported from Google Docs"""
    
    def __init__(self):
        self.supported_image_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        self.image_counter = 0
        
    def process_html_upload(self, file_path: Path, extract_dir: Path) -> Dict[str, Any]:
        """
        Process uploaded HTML file (potentially zipped from Google Docs)
        
        Args:
            file_path: Path to uploaded file
            extract_dir: Directory to extract files to
            
        Returns:
            Dictionary with extracted content, images, and metadata
        """
        logger.info(f"🔄 Processing HTML upload: {file_path.name}")
        
        try:
            # Handle zipped HTML (Google Docs export format)
            if file_path.suffix.lower() == '.zip':
                return self._process_zipped_html(file_path, extract_dir)
            elif file_path.suffix.lower() in {'.html', '.htm'}:
                return self._process_single_html(file_path, extract_dir)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
                
        except Exception as e:
            logger.error(f"❌ Error processing HTML upload: {e}")
            raise
    
    def _process_zipped_html(self, zip_path: Path, extract_dir: Path) -> Dict[str, Any]:
        """Process zipped HTML file from Google Docs"""
        logger.info("📦 Extracting zipped HTML file")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the main HTML file
        html_files = list(extract_dir.glob("*.html"))
        if not html_files:
            raise ValueError("No HTML file found in the zip archive")
        
        main_html = html_files[0]  # Usually there's only one
        logger.info(f"📄 Found main HTML file: {main_html.name}")
        
        return self._process_single_html(main_html, extract_dir)
    
    def _process_single_html(self, html_path: Path, extract_dir: Path) -> Dict[str, Any]:
        """Process a single HTML file"""
        logger.info(f"📖 Processing HTML file: {html_path.name}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content and structure
        text_content = self._extract_text_content(soup)
        
        # Extract and process images
        images = self._extract_images(soup, extract_dir)
        
        # Convert to markdown
        markdown_content = self._convert_to_markdown(soup, images)
        
        # Analyze document structure
        structure = self._analyze_structure(soup)
        
        result = {
            'title': self._extract_title(soup),
            'text_content': text_content,
            'markdown_content': markdown_content,
            'images': images,
            'structure': structure,
            'word_count': len(text_content.split()),
            'estimated_chapters': max(1, len(structure.get('headings', [])) or 1)
        }
        
        logger.info(f"✅ Processed HTML: {result['word_count']} words, {len(images)} images")
        return result
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract document title"""
        # Try different methods to find title
        title_selectors = [
            'title',
            'h1',
            '.title',
            '#title',
            '[role="heading"][aria-level="1"]'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return "Imported Document"
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_images(self, soup: BeautifulSoup, extract_dir: Path) -> List[Dict[str, Any]]:
        """Extract images from HTML"""
        images = []
        self.image_counter = 0
        
        for img in soup.find_all('img'):
            image_info = self._process_image(img, extract_dir)
            if image_info:
                images.append(image_info)
        
        logger.info(f"🖼️ Extracted {len(images)} images")
        return images
    
    def _process_image(self, img_tag, extract_dir: Path) -> Dict[str, Any]:
        """Process individual image"""
        self.image_counter += 1
        
        src = img_tag.get('src', '')
        alt = img_tag.get('alt', f'Image {self.image_counter}')
        title = img_tag.get('title', '')
        
        image_info = {
            'id': f'img_{self.image_counter}',
            'alt': alt,
            'title': title,
            'original_src': src,
            'local_path': None,
            'description': alt or title or f'Image {self.image_counter}'
        }
        
        try:
            if src.startswith('data:image'):
                # Handle base64 embedded images
                image_info['local_path'] = self._save_base64_image(src, extract_dir, self.image_counter)
            elif src.startswith('http'):
                # External image - we'll note it but not download
                image_info['external_url'] = src
                logger.warning(f"⚠️ External image found: {src[:50]}...")
            else:
                # Local file reference
                local_img_path = extract_dir / src
                if local_img_path.exists():
                    image_info['local_path'] = local_img_path
                else:
                    logger.warning(f"⚠️ Image file not found: {src}")
        
        except Exception as e:
            logger.warning(f"⚠️ Error processing image {src}: {e}")
        
        return image_info
    
    def _save_base64_image(self, data_url: str, extract_dir: Path, counter: int) -> Path:
        """Save base64 encoded image to file"""
        try:
            # Parse data URL: data:image/png;base64,iVBORw0KGgoAAAA...
            header, data = data_url.split(',', 1)
            format_info = header.split(';')[0].split('/')[-1]
            
            # Decode base64 data
            image_data = base64.b64decode(data)
            
            # Save to file
            filename = f"image_{counter}.{format_info}"
            image_path = extract_dir / filename
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"💾 Saved base64 image: {filename}")
            return image_path
            
        except Exception as e:
            logger.error(f"❌ Error saving base64 image: {e}")
            return None
    
    def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze document structure"""
        structure = {
            'headings': [],
            'paragraphs': 0,
            'lists': 0,
            'tables': 0,
            'has_toc': False
        }
        
        # Find headings
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            for heading in headings:
                structure['headings'].append({
                    'level': level,
                    'text': heading.get_text().strip(),
                    'id': heading.get('id', '')
                })
        
        # Count other elements
        structure['paragraphs'] = len(soup.find_all('p'))
        structure['lists'] = len(soup.find_all(['ul', 'ol']))
        structure['tables'] = len(soup.find_all('table'))
        
        # Check for table of contents
        toc_indicators = soup.find_all(text=re.compile(r'table.{0,10}contents|contents', re.I))
        structure['has_toc'] = len(toc_indicators) > 0
        
        return structure
    
    def _convert_to_markdown(self, soup: BeautifulSoup, images: List[Dict]) -> str:
        """Convert HTML to markdown with image placeholders"""
        markdown_lines = []
        
        # Process the document body
        body = soup.find('body') or soup
        
        for element in body.descendants:
            if element.name == 'h1':
                markdown_lines.append(f"\n# {element.get_text().strip()}\n")
            elif element.name == 'h2':
                markdown_lines.append(f"\n## {element.get_text().strip()}\n")
            elif element.name == 'h3':
                markdown_lines.append(f"\n### {element.get_text().strip()}\n")
            elif element.name == 'h4':
                markdown_lines.append(f"\n#### {element.get_text().strip()}\n")
            elif element.name == 'h5':
                markdown_lines.append(f"\n##### {element.get_text().strip()}\n")
            elif element.name == 'h6':
                markdown_lines.append(f"\n###### {element.get_text().strip()}\n")
            elif element.name == 'p' and element.get_text().strip():
                markdown_lines.append(f"\n{element.get_text().strip()}\n")
            elif element.name == 'img':
                # Find corresponding image info
                img_info = next((img for img in images if img['original_src'] == element.get('src')), None)
                if img_info:
                    alt_text = img_info['description']
                    if img_info.get('local_path'):
                        markdown_lines.append(f"\n![{alt_text}]({img_info['local_path'].name})\n")
                    else:
                        markdown_lines.append(f"\n*[Image: {alt_text}]*\n")
            elif element.name == 'strong' or element.name == 'b':
                text = element.get_text().strip()
                if text:
                    markdown_lines.append(f"**{text}**")
            elif element.name == 'em' or element.name == 'i':
                text = element.get_text().strip()
                if text:
                    markdown_lines.append(f"*{text}*")
        
        # Clean up and join
        markdown = ''.join(markdown_lines)
        
        # Clean up excessive newlines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        return markdown.strip()

def create_temp_extraction_dir() -> Path:
    """Create temporary directory for file extraction"""
    temp_dir = Path(tempfile.mkdtemp(prefix="book_creator_html_"))
    logger.info(f"📁 Created temp extraction directory: {temp_dir}")
    return temp_dir

def cleanup_temp_dir(temp_dir: Path):
    """Clean up temporary directory"""
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        logger.info(f"🗑️ Cleaned up temp directory: {temp_dir}")
