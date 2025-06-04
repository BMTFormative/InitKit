import logging
from typing import List, Dict, Any, Set
from collections import defaultdict
import random

logger = logging.getLogger(__name__)

class BalancedRetrieval:
    """
    Balanced retrieval system to ensure diverse source representation
    and avoid single-source bias in RAG responses.
    """
    
    def __init__(self, min_sources: int = 2, max_per_source: int = 2):
        """
        Initialize balanced retrieval system
        
        Args:
            min_sources: Minimum number of different sources to include
            max_per_source: Maximum chunks per source file
        """
        self.min_sources = min_sources
        self.max_per_source = max_per_source
        
    def balance_search_results(self, results: List[Dict[str, Any]], 
                             target_count: int = 5) -> List[Dict[str, Any]]:
        """
        Balance search results to ensure source diversity
        
        Args:
            results: Raw search results from vector store
            target_count: Target number of results to return
            
        Returns:
            Balanced list of results with source diversity
        """
        if not results:
            return results
            
        try:
            # Group results by source file
            source_groups = defaultdict(list)
            for result in results:
                source_file = result.get('metadata', {}).get('source_file', 'unknown')
                source_groups[source_file].append(result)
            
            logger.info(f"Found results from {len(source_groups)} different sources")
            
            # Check if we have enough source diversity
            if len(source_groups) < self.min_sources:
                logger.warning(f"Only {len(source_groups)} sources available, minimum is {self.min_sources}")
                # If not enough sources, return top results as-is
                return results[:target_count]
            
            # Apply balancing strategy
            balanced_results = self._apply_balancing_strategy(source_groups, target_count)
            
            # Sort by original score to maintain relevance order within balanced set
            balanced_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            logger.info(f"Balanced results: {len(balanced_results)} items from {len(set(r.get('metadata', {}).get('source_file', '') for r in balanced_results))} sources")
            
            return balanced_results
            
        except Exception as e:
            logger.error(f"Error in balanced retrieval: {e}")
            # Fallback to original results
            return results[:target_count]
    
    def _apply_balancing_strategy(self, source_groups: Dict[str, List[Dict]], 
                                target_count: int) -> List[Dict[str, Any]]:
        """
        Apply balanced selection strategy across sources
        """
        balanced_results = []
        sources = list(source_groups.keys())
        
        # Strategy 1: Round-robin selection
        max_rounds = max(target_count // len(sources), 1)
        
        for round_num in range(max_rounds):
            for source in sources:
                if len(balanced_results) >= target_count:
                    break
                    
                source_results = source_groups[source]
                
                # Get next best result from this source that we haven't selected
                available_results = [
                    r for r in source_results 
                    if r not in balanced_results
                ]
                
                if available_results:
                    # Select based on round number (0=best, 1=second best, etc.)
                    if round_num < len(available_results):
                        balanced_results.append(available_results[round_num])
        
        # Strategy 2: Fill remaining slots with highest scores regardless of source
        if len(balanced_results) < target_count:
            all_remaining = []
            for source_results in source_groups.values():
                for result in source_results:
                    if result not in balanced_results:
                        all_remaining.append(result)
            
            # Sort by score and take remaining slots
            all_remaining.sort(key=lambda x: x.get('score', 0), reverse=True)
            slots_remaining = target_count - len(balanced_results)
            balanced_results.extend(all_remaining[:slots_remaining])
        
        return balanced_results
    
    def enforce_source_limits(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enforce maximum results per source file
        """
        source_counts = defaultdict(int)
        filtered_results = []
        
        for result in results:
            source_file = result.get('metadata', {}).get('source_file', 'unknown')
            
            if source_counts[source_file] < self.max_per_source:
                filtered_results.append(result)
                source_counts[source_file] += 1
        
        return filtered_results
    
    def analyze_source_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the distribution of sources in results
        """
        if not results:
            return {"total_results": 0, "sources": {}, "diversity_score": 0.0}
        
        source_counts = defaultdict(int)
        source_scores = defaultdict(list)
        
        for result in results:
            source_file = result.get('metadata', {}).get('source_file', 'unknown')
            score = result.get('score', 0)
            
            source_counts[source_file] += 1
            source_scores[source_file].append(score)
        
        # Calculate diversity metrics
        total_sources = len(source_counts)
        total_results = len(results)
        
        # Diversity score: 1.0 = perfectly balanced, 0.0 = all from one source
        if total_sources == 1:
            diversity_score = 0.0
        else:
            # Calculate Shannon diversity index (simplified)
            diversity_score = min(1.0, total_sources / max(source_counts.values()))
        
        # Source statistics
        source_stats = {}
        for source, count in source_counts.items():
            avg_score = sum(source_scores[source]) / len(source_scores[source])
            source_stats[source] = {
                "count": count,
                "percentage": (count / total_results) * 100,
                "avg_score": round(avg_score, 3),
                "max_score": round(max(source_scores[source]), 3)
            }
        
        return {
            "total_results": total_results,
            "total_sources": total_sources,
            "diversity_score": round(diversity_score, 3),
            "sources": source_stats,
            "is_balanced": diversity_score > 0.5,
            "dominant_source": max(source_counts.items(), key=lambda x: x[1])[0] if source_counts else None
        }
    
    def get_source_weights(self, source_stats: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate weights to boost underrepresented sources
        """
        if not source_stats.get("sources"):
            return {}
        
        sources = source_stats["sources"]
        total_results = source_stats["total_results"]
        
        # Calculate ideal distribution (equal weight per source)
        num_sources = len(sources)
        ideal_percentage = 100.0 / num_sources
        
        weights = {}
        for source, stats in sources.items():
            current_percentage = stats["percentage"]
            
            # Boost underrepresented sources
            if current_percentage < ideal_percentage:
                weight = ideal_percentage / current_percentage
            else:
                weight = 1.0
            
            weights[source] = min(weight, 2.0)  # Cap boost at 2x
        
        return weights
    
    def reweight_results(self, results: List[Dict[str, Any]], 
                        source_weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Apply source weights to boost underrepresented sources
        """
        reweighted_results = []
        
        for result in results:
            source_file = result.get('metadata', {}).get('source_file', 'unknown')
            weight = source_weights.get(source_file, 1.0)
            
            # Create copy with adjusted score
            reweighted_result = result.copy()
            original_score = result.get('score', 0)
            reweighted_result['score'] = min(original_score * weight, 1.0)
            reweighted_result['original_score'] = original_score
            reweighted_result['source_weight'] = weight
            
            reweighted_results.append(reweighted_result)
        
        # Re-sort by new weighted scores
        reweighted_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return reweighted_results