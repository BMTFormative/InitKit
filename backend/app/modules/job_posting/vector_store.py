import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
from app.core.config import settings

# Load vector store configuration from core settings
VECTOR_STORE_PATH = settings.VECTOR_STORE_PATH
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
VECTOR_SEARCH_TOP_K = settings.VECTOR_SEARCH_TOP_K
VECTOR_SEARCH_SIMILARITY_THRESHOLD = settings.VECTOR_SEARCH_SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        """Initialize the vector store with ChromaDB"""
        # Ensure vector store directory exists
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=VECTOR_STORE_PATH
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Get or create collection
        self.collection_name = "job_posting_kb"
        try:
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Job posting knowledge base"}
            )
            logger.info(f"Created new collection: {self.collection_name}")

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the vector store
        
        Args:
            documents: List of dicts with 'content', 'metadata', 'id' keys
        """
        try:
            texts = [doc['content'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]
            ids = [doc['id'] for doc in documents]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} documents...")
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def search(self, query: str, n_results: int = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents in the vector store
        
        Args:
            query: Search query
            n_results: Number of results to return (default: VECTOR_SEARCH_TOP_K)
            
        Returns:
            List of matching documents with scores
        """
        try:
            if n_results is None:
                n_results = VECTOR_SEARCH_TOP_K
                
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    score = 1 - results['distances'][0][i]  # Convert distance to similarity
                    
                    # Only include results above similarity threshold
                    if score >= VECTOR_SEARCH_SIMILARITY_THRESHOLD:
                        formatted_results.append({
                            'content': doc,
                            'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                            'score': score,
                            'id': results['ids'][0][i]
                        })
            
            logger.info(f"Found {len(formatted_results)} relevant documents for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                'document_count': count,
                'collection_name': self.collection_name,
                'embedding_model': EMBEDDING_MODEL
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'document_count': 0, 'collection_name': self.collection_name}

    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Job posting knowledge base"}
            )
            logger.info("Collection cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

    def search_by_platform(self, query: str, platform: str) -> List[Dict[str, Any]]:
        """
        Search for documents specific to a platform
        
        Args:
            query: Search query
            platform: Platform name (e.g., 'linkedin', 'indeed')
            
        Returns:
            List of matching documents
        """
        try:
            # First try to find platform-specific content
            platform_query = f"{query} {platform}"
            results = self.search(platform_query)
            
            # If no platform-specific results, fall back to general search
            if not results:
                results = self.search(query)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching by platform: {e}")
            return []