"""
Document Processor for loading and chunking documents
"""
import os
from typing import List, Dict
from pathlib import Path
import pypdf
from docx import Document
from .. import config


class DocumentChunk:
    """Represents a chunk of text from a document"""
    
    def __init__(self, text: str, metadata: Dict):
        self.text = text
        self.metadata = metadata
    
    def __repr__(self):
        return f"DocumentChunk(text_length={len(self.text)}, metadata={self.metadata})"


class DocumentProcessor:
    """Processes documents and splits them into chunks"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize document processor
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
    
    def load_document(self, file_path: str) -> str:
        """
        Load document content based on file type
        
        Args:
            file_path: Path to the document
            
        Returns:
            Document text content
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.txt' or extension == '.md':
            return self._load_text_file(file_path)
        elif extension == '.pdf':
            return self._load_pdf(file_path)
        elif extension == '.docx':
            return self._load_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def _load_text_file(self, file_path: Path) -> str:
        """Load plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_pdf(self, file_path: Path) -> str:
        """Load PDF file"""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _load_docx(self, file_path: Path) -> str:
        """Load DOCX file"""
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[DocumentChunk]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to chunks
            
        Returns:
            List of DocumentChunk objects
        """
        if metadata is None:
            metadata = {}
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # If not at the end, try to break at a sentence or word boundary
            if end < text_length:
                # Look for sentence boundary
                for delimiter in ['. ', '.\n', '! ', '?\n', '\n\n']:
                    last_delimiter = text.rfind(delimiter, start, end)
                    if last_delimiter != -1:
                        end = last_delimiter + len(delimiter)
                        break
                else:
                    # If no sentence boundary, look for word boundary
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1:
                        end = last_space
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = len(chunks)
                chunk_metadata['start_char'] = start
                chunk_metadata['end_char'] = end
                chunks.append(DocumentChunk(chunk_text, chunk_metadata))
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_document(self, file_path: str) -> List[DocumentChunk]:
        """
        Load and chunk a document
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of DocumentChunk objects
        """
        print(f"Processing document: {file_path}")
        text = self.load_document(file_path)
        
        metadata = {
            'source': file_path,
            'filename': os.path.basename(file_path)
        }
        
        chunks = self.chunk_text(text, metadata)
        print(f"Created {len(chunks)} chunks from {file_path}")
        return chunks
    
    def process_directory(self, directory_path: str) -> List[DocumentChunk]:
        """
        Process all supported documents in a directory
        
        Args:
            directory_path: Path to directory
            
        Returns:
            List of all DocumentChunk objects
        """
        all_chunks = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in config.SUPPORTED_EXTENSIONS:
                try:
                    chunks = self.process_document(str(file_path))
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        print(f"Total chunks created: {len(all_chunks)}")
        return all_chunks

# Made with Bob
