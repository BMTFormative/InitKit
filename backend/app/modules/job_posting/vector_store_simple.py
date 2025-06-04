import os
import logging
import json
from pathlib import Path
from typing import List, Dict, Any
import re
from app.core.config import settings

# Load vector store configuration from core settings
VECTOR_STORE_PATH = settings.VECTOR_STORE_PATH
VECTOR_SEARCH_TOP_K = settings.VECTOR_SEARCH_TOP_K

from .balanced_retrieval import BalancedRetrieval

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, enable_balanced_retrieval: bool = True):
        """
        Initialize the simple vector store with text search
        
        Args:
            enable_balanced_retrieval: Enable source diversity balancing
        """
        # Ensure vector store directory exists
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        
        # Simple storage file
        self.storage_file = Path(VECTOR_STORE_PATH) / "documents.json"
        self.documents = []
        
        # Initialize balanced retrieval system
        self.enable_balanced_retrieval = enable_balanced_retrieval
        if enable_balanced_retrieval:
            self.balanced_retrieval = BalancedRetrieval(min_sources=2, max_per_source=3)
        
        # Load existing documents if any
        self._load_documents()
        
        logger.info(f"Simple vector store initialized (balanced_retrieval={'enabled' if enable_balanced_retrieval else 'disabled'})")

    def _load_documents(self):
        """Load documents from storage file"""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                logger.info(f"Loaded {len(self.documents)} documents from storage")
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            self.documents = []

    def _save_documents(self):
        """Save documents to storage file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.documents)} documents to storage")
        except Exception as e:
            logger.error(f"Error saving documents: {e}")

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the vector store
        
        Args:
            documents: List of dicts with 'content', 'metadata', 'id' keys
        """
        try:
            for doc in documents:
                # Add search keywords for better matching
                content_lower = doc['content'].lower()
                keywords = self._extract_keywords(content_lower)
                
                doc_entry = {
                    'id': doc['id'],
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'content_lower': content_lower,
                    'keywords': keywords
                }
                self.documents.append(doc_entry)
            
            self._save_documents()
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for better search"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text)
        # Filter out common words and keep meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(keywords))  # Remove duplicates

    def search(self, query: str, n_results: int = None, force_balance: bool = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents using text matching with optional source balancing
        
        Args:
            query: Search query
            n_results: Number of results to return (default: VECTOR_SEARCH_TOP_K)
            force_balance: Override global balanced_retrieval setting
            
        Returns:
            List of matching documents with scores (potentially balanced by source)
        """
        try:
            if n_results is None:
                n_results = VECTOR_SEARCH_TOP_K
                
            query_lower = query.lower()
            query_keywords = self._extract_keywords(query_lower)
            
            # Score documents based on text similarity
            scored_docs = []
            for doc in self.documents:
                score = self._calculate_similarity(query_lower, query_keywords, doc)
                if score > 0.1:  # Minimum similarity threshold
                    scored_docs.append({
                        'content': doc['content'],
                        'metadata': doc['metadata'],
                        'score': score,
                        'id': doc['id']
                    })
            
            # Sort by score initially
            scored_docs.sort(key=lambda x: x['score'], reverse=True)
            
            # Apply balanced retrieval if enabled
            use_balancing = force_balance if force_balance is not None else self.enable_balanced_retrieval
            
            if use_balancing and hasattr(self, 'balanced_retrieval'):
                # Get more results initially for better balancing
                candidate_results = scored_docs[:n_results * 2]
                
                # Apply balanced retrieval
                balanced_results = self.balanced_retrieval.balance_search_results(
                    candidate_results, n_results
                )
                
                # Log balancing info
                distribution = self.balanced_retrieval.analyze_source_distribution(balanced_results)
                logger.info(f"Search balanced: {distribution['total_sources']} sources, "
                          f"diversity_score={distribution['diversity_score']}")
                
                results = balanced_results
            else:
                results = scored_docs[:n_results]
            
            logger.info(f"Found {len(results)} relevant documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []

    def _calculate_similarity(self, query: str, query_keywords: List[str], doc: Dict) -> float:
        """Calculate similarity between query and document"""
        score = 0.0
        
        # Direct text matching (higher weight)
        if query in doc['content_lower']:
            score += 0.8
        
        # Word matching
        query_words = query.split()
        for word in query_words:
            if word in doc['content_lower']:
                score += 0.3
        
        # Keyword matching
        common_keywords = set(query_keywords) & set(doc['keywords'])
        if common_keywords:
            score += len(common_keywords) * 0.2
        
        # Platform-specific boost
        platform = doc['metadata'].get('platform', '').lower()
        if 'linkedin' in query and platform == 'linkedin':
            score += 0.5
        elif 'linkedin' not in query and platform != 'linkedin':
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            return {
                'document_count': len(self.documents),
                'collection_name': 'simple_text_store',
                'embedding_model': 'simple_text_matching'
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'document_count': 0, 'collection_name': 'simple_text_store'}

    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            self.documents = []
            self._save_documents()
            logger.info("Collection cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

    def search_by_platform(self, query: str, platform: str) -> List[Dict[str, Any]]:
        """
        Search for documents specific to a platform with balanced retrieval
        
        Args:
            query: Search query
            platform: Platform name (e.g., 'linkedin', 'indeed')
            
        Returns:
            List of matching documents
        """
        try:
            # First try to find platform-specific content
            platform_query = f"{query} {platform}"
            results = self.search(platform_query, force_balance=True)
            
            # If no platform-specific results, fall back to general search
            if not results:
                results = self.search(query, force_balance=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching by platform: {e}")
            return []
    
    def analyze_search_bias(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """
        Analyze potential bias in search results
        
        Args:
            query: Search query to analyze
            n_results: Number of results to analyze
            
        Returns:
            Bias analysis report
        """
        try:
            # Get unbalanced results
            unbalanced_results = self.search(query, n_results, force_balance=False)
            
            # Get balanced results  
            balanced_results = self.search(query, n_results, force_balance=True)
            
            # Analyze both sets
            if hasattr(self, 'balanced_retrieval'):
                unbalanced_dist = self.balanced_retrieval.analyze_source_distribution(unbalanced_results)
                balanced_dist = self.balanced_retrieval.analyze_source_distribution(balanced_results)
                
                return {
                    "query": query,
                    "unbalanced": {
                        "results_count": len(unbalanced_results),
                        "source_distribution": unbalanced_dist,
                        "dominant_source_percentage": max(
                            [stats["percentage"] for stats in unbalanced_dist["sources"].values()]
                        ) if unbalanced_dist["sources"] else 0
                    },
                    "balanced": {
                        "results_count": len(balanced_results),
                        "source_distribution": balanced_dist,
                        "diversity_improvement": balanced_dist["diversity_score"] - unbalanced_dist["diversity_score"]
                    },
                    "bias_detected": unbalanced_dist["diversity_score"] < 0.5,
                    "balancing_effective": balanced_dist["diversity_score"] > unbalanced_dist["diversity_score"]
                }
            else:
                return {"error": "Balanced retrieval not enabled"}
                
        except Exception as e:
            logger.error(f"Error analyzing search bias: {e}")
            return {"error": str(e)}