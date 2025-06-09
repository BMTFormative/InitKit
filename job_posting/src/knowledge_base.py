import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import re
from src.vector_store_simple import VectorStore
from config.settings import KNOWLEDGE_BASE_PATH

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    def __init__(self):
        """Initialize the knowledge base manager"""
        self.vector_store = VectorStore()
        self.kb_path = Path(KNOWLEDGE_BASE_PATH)
        self.kb_path.mkdir(parents=True, exist_ok=True)

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for other punctuation
                    punct_end = text.rfind('!', start, end)
                    if punct_end == -1:
                        punct_end = text.rfind('?', start, end)
                    if punct_end > start + chunk_size // 2:
                        end = punct_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + chunk_size - overlap, end - overlap)
            if start >= len(text):
                break
        
        return chunks

    def load_knowledge_base(self) -> bool:
        """
        Load all knowledge base files into the vector store
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Loading knowledge base files...")
            
            # Clear existing collection
            self.vector_store.clear_collection()
            
            documents = []
            doc_id = 0
            
            # Process all text files in the knowledge base directory
            for file_path in self.kb_path.glob("*.txt"):
                logger.info(f"Processing file: {file_path.name}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Determine the source type based on filename
                    filename = file_path.stem.lower()
                    if 'linkedin' in filename:
                        source_type = 'linkedin'
                        platform = 'linkedin'
                    elif 'kb2' in filename:
                        source_type = 'general'
                        platform = 'general'
                    else:
                        source_type = 'general'
                        platform = 'general'
                    
                    # Chunk the content
                    chunks = self.chunk_text(content)
                    
                    # Create document entries for each chunk
                    for i, chunk in enumerate(chunks):
                        doc_id += 1
                        documents.append({
                            'id': f"doc_{doc_id}",
                            'content': chunk,
                            'metadata': {
                                'source_file': file_path.name,
                                'source_type': source_type,
                                'platform': platform,
                                'chunk_index': i,
                                'total_chunks': len(chunks)
                            }
                        })
                
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    continue
            
            # Add all documents to vector store
            if documents:
                self.vector_store.add_documents(documents)
                logger.info(f"Successfully loaded {len(documents)} document chunks from {len(list(self.kb_path.glob('*.txt')))} files")
                return True
            else:
                logger.warning("No documents found to load")
                return False
                
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return False

    def search_knowledge_base(self, query: str, platform: str = None) -> str:
        """
        Search the knowledge base and return relevant context
        
        Args:
            query: Search query
            platform: Optional platform filter
            
        Returns:
            Formatted context string
        """
        try:
            # Search based on platform if specified
            if platform and platform.lower() == 'linkedin':
                results = self.vector_store.search_by_platform(query, 'linkedin')
            else:
                results = self.vector_store.search(query)
            
            if not results:
                return ""
            
            # Format the context
            context_parts = []
            for result in results[:3]:  # Use top 3 results
                source_info = f"[Source: {result['metadata'].get('source_file', 'Unknown')}]"
                context_parts.append(f"{source_info}\n{result['content']}")
            
            return "\n\n---\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return ""

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            
            # Count files in KB directory
            txt_files = list(self.kb_path.glob("*.txt"))
            
            return {
                'kb_files_count': len(txt_files),
                'kb_files': [f.name for f in txt_files],
                'vector_documents': vector_stats['document_count'],
                'collection_name': vector_stats['collection_name'],
                'embedding_model': vector_stats.get('embedding_model', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Error getting KB stats: {e}")
            return {'error': str(e)}

    def copy_kb_files_from_source(self, source_path: str) -> bool:
        """
        Copy knowledge base files from source directory
        
        Args:
            source_path: Path to source KB directory
            
        Returns:
            True if successful
        """
        try:
            source_dir = Path(source_path)
            if not source_dir.exists():
                logger.error(f"Source directory does not exist: {source_path}")
                return False
            
            copied_count = 0
            for file_path in source_dir.glob("*.txt"):
                dest_path = self.kb_path / file_path.name
                
                # Copy file content
                with open(file_path, 'r', encoding='utf-8') as src_f:
                    content = src_f.read()
                
                with open(dest_path, 'w', encoding='utf-8') as dest_f:
                    dest_f.write(content)
                
                copied_count += 1
                logger.info(f"Copied: {file_path.name}")
            
            logger.info(f"Successfully copied {copied_count} KB files")
            return copied_count > 0
            
        except Exception as e:
            logger.error(f"Error copying KB files: {e}")
            return False