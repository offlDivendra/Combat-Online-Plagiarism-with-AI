"""
Fuzzy Matching Service
Implements fuzzy string matching using RapidFuzz for detecting similar but not identical text.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from rapidfuzz import fuzz, process
from rapidfuzz.distance import Levenshtein

from app.services.preprocessing import preprocessor


class FuzzyMatchingAnalyzer:
    """
    Analyzes text similarity using fuzzy string matching algorithms.
    Detects paraphrased or slightly modified content.
    """
    
    def __init__(self, threshold: float = 82.0):
        """
        Initialize the fuzzy matching analyzer.
        
        Args:
            threshold: Minimum similarity threshold (0-100) for considering a match
        """
        self.threshold = threshold
    
    def simple_ratio(self, text1: str, text2: str) -> float:
        """
        Calculate simple fuzzy ratio between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-100)
        """
        if not text1 or not text2:
            return 0.0
        
        return fuzz.ratio(text1, text2)
    
    def partial_ratio(self, text1: str, text2: str) -> float:
        """
        Calculate partial fuzzy ratio (substring matching).
        Useful when one text is much shorter than the other.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-100)
        """
        if not text1 or not text2:
            return 0.0
        
        return fuzz.partial_ratio(text1, text2)
    
    def token_sort_ratio(self, text1: str, text2: str) -> float:
        """
        Calculate fuzzy ratio after sorting tokens alphabetically.
        Handles word order differences.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-100)
        """
        if not text1 or not text2:
            return 0.0
        
        return fuzz.token_sort_ratio(text1, text2)
    
    def token_set_ratio(self, text1: str, text2: str) -> float:
        """
        Calculate fuzzy ratio using token sets.
        Most robust against word order and duplicates.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-100)
        """
        if not text1 or not text2:
            return 0.0
        
        return fuzz.token_set_ratio(text1, text2)
    
    def weighted_ratio(self, text1: str, text2: str) -> float:
        """
        Calculate weighted average of multiple fuzzy ratios.
        Provides a comprehensive similarity score.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Weighted similarity score (0-100)
        """
        if not text1 or not text2:
            return 0.0
        
        return fuzz.WRatio(text1, text2)
    
    def comprehensive_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """
        Calculate all fuzzy similarity metrics.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Dictionary with all similarity scores
        """
        # Normalize texts for consistent comparison
        norm_text1 = preprocessor.normalize_text(text1)
        norm_text2 = preprocessor.normalize_text(text2)
        
        return {
            "simple_ratio": float(self.simple_ratio(norm_text1, norm_text2)),
            "partial_ratio": float(self.partial_ratio(norm_text1, norm_text2)),
            "token_sort_ratio": float(self.token_sort_ratio(norm_text1, norm_text2)),
            "token_set_ratio": float(self.token_set_ratio(norm_text1, norm_text2)),
            "weighted_ratio": float(self.weighted_ratio(norm_text1, norm_text2))
        }
    
    def best_similarity(self, text1: str, text2: str) -> float:
        """
        Get the best (maximum) similarity score from all methods.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Best similarity score (0-100)
        """
        scores = self.comprehensive_similarity(text1, text2)
        return max(scores.values())
    
    def average_similarity(self, text1: str, text2: str) -> float:
        """
        Get the average similarity score from all methods.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Average similarity score (0-100)
        """
        scores = self.comprehensive_similarity(text1, text2)
        return float(np.mean(list(scores.values())))
    
    def sentence_similarity(
        self, 
        query_sentence: str, 
        reference_sentences: List[str],
        method: str = "weighted"
    ) -> List[Tuple[str, float, int]]:
        """
        Find similar sentences from a list of reference sentences.
        
        Args:
            query_sentence: Sentence to match
            reference_sentences: List of reference sentences
            method: Fuzzy matching method to use
            
        Returns:
            List of (sentence, score, index) tuples sorted by similarity
        """
        if not query_sentence or not reference_sentences:
            return []
        
        # Normalize query
        norm_query = preprocessor.normalize_text(query_sentence)
        
        # Choose scoring method
        if method == "simple":
            score_func = self.simple_ratio
        elif method == "partial":
            score_func = self.partial_ratio
        elif method == "token_sort":
            score_func = self.token_sort_ratio
        elif method == "token_set":
            score_func = self.token_set_ratio
        else:  # weighted (default)
            score_func = self.weighted_ratio
        
        # Calculate similarities
        results = []
        for idx, ref_sentence in enumerate(reference_sentences):
            norm_ref = preprocessor.normalize_text(ref_sentence)
            score = score_func(norm_query, norm_ref)
            
            if score >= self.threshold:
                results.append((ref_sentence, float(score), idx))
        
        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def find_best_match(
        self, 
        query: str, 
        choices: List[str],
        limit: int = 1
    ) -> List[Tuple[str, float, int]]:
        """
        Find the best matching string(s) from a list of choices.
        Uses token_set_ratio which is robust but doesn't inflate short-vs-long matches.
        
        Args:
            query: Text to match
            choices: List of candidate texts
            limit: Number of top matches to return
            
        Returns:
            List of (match, score, index) tuples
        """
        if not query or not choices:
            return []
        
        # Use token_set_ratio: handles word order, robust against length differences
        # but still requires actual content overlap (unlike partial_ratio / WRatio)
        results = process.extract(
            query,
            choices,
            scorer=fuzz.token_set_ratio,
            limit=limit
        )
        
        # Convert to our format: (text, score, index)
        return [
            (match[0], float(match[1]), match[2])
            for match in results
            if match[1] >= self.threshold
        ]
    
    def compare_sentence_pairs(
        self, 
        query_sentences: List[str], 
        reference_sentences: List[str]
    ) -> List[Dict[str, any]]:
        """
        Compare each query sentence against reference sentences.
        Finds the best match for each query sentence.
        
        Args:
            query_sentences: List of sentences to analyze
            reference_sentences: List of reference sentences
            
        Returns:
            List of match dictionaries with details
        """
        matches = []
        
        for query_idx, query_sent in enumerate(query_sentences):
            # Find best matching reference sentence
            best_matches = self.find_best_match(query_sent, reference_sentences, limit=1)
            
            if best_matches:
                matched_sent, score, ref_idx = best_matches[0]
                
                matches.append({
                    "query_sentence": query_sent,
                    "query_index": query_idx,
                    "matched_sentence": matched_sent,
                    "reference_index": ref_idx,
                    "similarity": score,
                    "is_high_similarity": score >= 80.0
                })
        
        return matches
    
    def analyze_document_similarity(
        self, 
        query_text: str, 
        reference_text: str
    ) -> Dict[str, any]:
        """
        Comprehensive fuzzy analysis between two documents.
        Uses sentence-level matching to avoid inflated scores on long documents.
        
        Args:
            query_text: Text to analyze
            reference_text: Reference text
            
        Returns:
            Detailed similarity analysis
        """
        # Sentence-level analysis (more accurate for long documents)
        query_sentences = preprocessor.split_sentences(query_text)
        ref_sentences = preprocessor.split_sentences(reference_text)
        
        # Filter out very short sentences
        min_len = 20
        query_sentences = [s for s in query_sentences if len(s.strip()) >= min_len]
        ref_sentences = [s for s in ref_sentences if len(s.strip()) >= min_len]
        
        sentence_matches = self.compare_sentence_pairs(query_sentences, ref_sentences)
        
        # Calculate overall similarity as:
        # (number of sentences with a match above threshold) / (total query sentences)
        # weighted by their individual scores
        if query_sentences:
            matched_indices = set()
            total_weighted_score = 0.0
            for m in sentence_matches:
                idx = m["query_index"]
                if idx not in matched_indices:
                    matched_indices.add(idx)
                    total_weighted_score += m["similarity"]
            
            # Proportion of sentences matched, scaled by their average score
            if matched_indices:
                avg_match_score = total_weighted_score / len(matched_indices)
                coverage = len(matched_indices) / len(query_sentences)
                # Combined: how much is matched * how well it matches
                overall_sim = coverage * avg_match_score
            else:
                overall_sim = 0.0
        else:
            overall_sim = 0.0
        
        # Document-level similarity (kept for reference, not used as primary score)
        # Only computed on a short sample to avoid performance issues
        sample1 = query_text[:500] if len(query_text) > 500 else query_text
        sample2 = reference_text[:500] if len(reference_text) > 500 else reference_text
        doc_similarity = self.comprehensive_similarity(sample1, sample2)
        
        high_sim_count = sum(1 for m in sentence_matches if m["is_high_similarity"])
        avg_sentence_sim = float(np.mean([m["similarity"] for m in sentence_matches])) if sentence_matches else 0.0
        
        return {
            "document_similarity": doc_similarity,
            "overall_similarity": round(overall_sim, 2),
            "sentence_matches": sentence_matches,
            "total_query_sentences": len(query_sentences),
            "total_matched_sentences": len(sentence_matches),
            "average_sentence_similarity": avg_sentence_sim,
            "high_similarity_count": high_sim_count
        }
    
    def compare_with_multiple_references(
        self, 
        query_text: str, 
        reference_texts: List[str]
    ) -> List[Dict[str, any]]:
        """
        Compare query text with multiple reference documents.
        
        Args:
            query_text: Text to analyze
            reference_texts: List of reference texts
            
        Returns:
            List of similarity results for each reference
        """
        results = []
        
        for idx, ref_text in enumerate(reference_texts):
            analysis = self.analyze_document_similarity(query_text, ref_text)
            results.append({
                "reference_index": idx,
                "similarity": analysis["overall_similarity"],
                "details": analysis
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results
    
    def levenshtein_distance(self, text1: str, text2: str) -> int:
        """
        Calculate Levenshtein edit distance between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Edit distance (number of operations needed to transform text1 to text2)
        """
        if not text1 or not text2:
            return max(len(text1), len(text2))
        
        return Levenshtein.distance(text1, text2)
    
    def normalized_levenshtein_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate normalized Levenshtein similarity (0-1).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Normalized similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        distance = self.levenshtein_distance(text1, text2)
        max_len = max(len(text1), len(text2))
        
        if max_len == 0:
            return 1.0
        
        return 1.0 - (distance / max_len)


# Global analyzer instance
fuzzy_analyzer = FuzzyMatchingAnalyzer()


# Convenience functions
def calculate_fuzzy_similarity(text1: str, text2: str) -> float:
    """Calculate weighted fuzzy similarity between two texts."""
    return fuzzy_analyzer.weighted_ratio(text1, text2)


def find_similar_sentences(
    query_sentence: str, 
    reference_sentences: List[str],
    threshold: float = 75.0
) -> List[Tuple[str, float, int]]:
    """Find similar sentences using fuzzy matching."""
    analyzer = FuzzyMatchingAnalyzer(threshold=threshold)
    return analyzer.sentence_similarity(query_sentence, reference_sentences)


def analyze_fuzzy_document(
    query_text: str, 
    reference_texts: List[str]
) -> Dict[str, any]:
    """
    Comprehensive fuzzy analysis for plagiarism detection.
    
    Args:
        query_text: Text to analyze
        reference_texts: List of reference texts
        
    Returns:
        Detailed fuzzy matching analysis
    """
    results = fuzzy_analyzer.compare_with_multiple_references(query_text, reference_texts)
    
    # Calculate aggregate scores
    if results:
        similarities = [r["similarity"] for r in results]
        avg_similarity = float(np.mean(similarities))
        max_similarity = float(np.max(similarities))
    else:
        avg_similarity = 0.0
        max_similarity = 0.0
    
    return {
        "average_similarity": avg_similarity,
        "max_similarity": max_similarity,
        "reference_results": results
    }
