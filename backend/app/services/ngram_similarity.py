"""
N-gram Similarity Service
Implements n-gram extraction and similarity comparison using Jaccard coefficient.
"""

from typing import List, Set, Dict, Tuple
from collections import Counter
import numpy as np

from app.services.preprocessing import preprocessor


class NgramSimilarityAnalyzer:
    """
    Analyzes text similarity using n-gram overlap.
    Supports unigrams, bigrams, and trigrams.
    """
    
    def __init__(self, n: int = 2):
        """
        Initialize the N-gram analyzer.
        
        Args:
            n: Size of n-grams (1=unigrams, 2=bigrams, 3=trigrams)
        """
        if n < 1:
            raise ValueError("n must be at least 1")
        self.n = n
    
    def generate_ngrams(self, tokens: List[str], n: int = None) -> List[Tuple[str, ...]]:
        """
        Generate n-grams from a list of tokens.
        
        Args:
            tokens: List of word tokens
            n: Size of n-grams (uses instance default if None)
            
        Returns:
            List of n-gram tuples
        """
        if n is None:
            n = self.n
        
        if not tokens or len(tokens) < n:
            return []
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i + n])
            ngrams.append(ngram)
        
        return ngrams
    
    def generate_character_ngrams(self, text: str, n: int = 3) -> List[str]:
        """
        Generate character-level n-grams from text.
        Useful for detecting similar phrases regardless of word boundaries.
        
        Args:
            text: Input text
            n: Size of character n-grams
            
        Returns:
            List of character n-gram strings
        """
        if not text or len(text) < n:
            return []
        
        # Remove spaces for character n-grams
        text = text.replace(" ", "")
        
        char_ngrams = []
        for i in range(len(text) - n + 1):
            char_ngrams.append(text[i:i + n])
        
        return char_ngrams
    
    def jaccard_similarity(self, set1: Set, set2: Set) -> float:
        """
        Calculate Jaccard similarity coefficient between two sets.
        
        Jaccard = |A ∩ B| / |A ∪ B|
        
        Args:
            set1: First set
            set2: Second set
            
        Returns:
            Jaccard similarity score (0-1)
        """
        if not set1 and not set2:
            return 1.0
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def cosine_similarity_ngrams(self, ngrams1: List, ngrams2: List) -> float:
        """
        Calculate cosine similarity between two n-gram lists.
        
        Args:
            ngrams1: First n-gram list
            ngrams2: Second n-gram list
            
        Returns:
            Cosine similarity score (0-1)
        """
        if not ngrams1 or not ngrams2:
            return 0.0
        
        # Count n-gram frequencies
        counter1 = Counter(ngrams1)
        counter2 = Counter(ngrams2)
        
        # Get all unique n-grams
        all_ngrams = set(counter1.keys()).union(set(counter2.keys()))
        
        # Create frequency vectors
        vec1 = np.array([counter1.get(ng, 0) for ng in all_ngrams])
        vec2 = np.array([counter2.get(ng, 0) for ng in all_ngrams])
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def dice_coefficient(self, set1: Set, set2: Set) -> float:
        """
        Calculate Dice coefficient between two sets.
        
        Dice = 2 * |A ∩ B| / (|A| + |B|)
        
        Args:
            set1: First set
            set2: Second set
            
        Returns:
            Dice coefficient score (0-1)
        """
        if not set1 and not set2:
            return 1.0
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        
        return (2.0 * intersection) / (len(set1) + len(set2))
    
    def calculate_similarity(
        self, 
        text1: str, 
        text2: str, 
        method: str = "jaccard"
    ) -> float:
        """
        Calculate n-gram similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            method: Similarity method ("jaccard", "cosine", or "dice")
            
        Returns:
            Similarity score (0-1)
        """
        # Preprocess texts
        tokens1 = preprocessor.preprocess_for_ngrams(text1, remove_stops=False)
        tokens2 = preprocessor.preprocess_for_ngrams(text2, remove_stops=False)
        
        # Generate n-grams
        ngrams1 = self.generate_ngrams(tokens1)
        ngrams2 = self.generate_ngrams(tokens2)
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        # Calculate similarity based on method
        if method == "cosine":
            return self.cosine_similarity_ngrams(ngrams1, ngrams2)
        elif method == "dice":
            return self.dice_coefficient(set(ngrams1), set(ngrams2))
        else:  # jaccard (default)
            return self.jaccard_similarity(set(ngrams1), set(ngrams2))
    
    def compare_with_references(
        self, 
        query_text: str, 
        reference_texts: List[str],
        method: str = "jaccard"
    ) -> List[float]:
        """
        Compare query text with multiple reference documents.
        
        Args:
            query_text: Text to analyze
            reference_texts: List of reference texts
            method: Similarity method to use
            
        Returns:
            List of similarity scores for each reference
        """
        similarities = []
        
        for ref_text in reference_texts:
            sim = self.calculate_similarity(query_text, ref_text, method)
            similarities.append(sim)
        
        return similarities
    
    def analyze_multi_ngram(
        self, 
        text1: str, 
        text2: str
    ) -> Dict[str, float]:
        """
        Analyze similarity using multiple n-gram sizes.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Dictionary with unigram, bigram, and trigram similarities
        """
        results = {}
        
        # Analyze with different n-gram sizes
        for n in [1, 2, 3]:
            analyzer = NgramSimilarityAnalyzer(n=n)
            similarity = analyzer.calculate_similarity(text1, text2, method="jaccard")
            results[f"{n}gram_similarity"] = float(similarity)
        
        # Calculate average
        results["average_ngram_similarity"] = float(np.mean(list(results.values())))
        
        return results
    
    def get_common_ngrams(
        self, 
        text1: str, 
        text2: str, 
        top_k: int = 10
    ) -> List[Tuple[Tuple[str, ...], int]]:
        """
        Find common n-grams between two texts.
        
        Args:
            text1: First text
            text2: Second text
            top_k: Number of top common n-grams to return
            
        Returns:
            List of (ngram, frequency) tuples
        """
        # Preprocess texts
        tokens1 = preprocessor.preprocess_for_ngrams(text1, remove_stops=False)
        tokens2 = preprocessor.preprocess_for_ngrams(text2, remove_stops=False)
        
        # Generate n-grams
        ngrams1 = self.generate_ngrams(tokens1)
        ngrams2 = self.generate_ngrams(tokens2)
        
        # Count frequencies
        counter1 = Counter(ngrams1)
        counter2 = Counter(ngrams2)
        
        # Find common n-grams
        common = set(counter1.keys()).intersection(set(counter2.keys()))
        
        # Create list with minimum frequency
        common_ngrams = [
            (ng, min(counter1[ng], counter2[ng]))
            for ng in common
        ]
        
        # Sort by frequency
        common_ngrams.sort(key=lambda x: x[1], reverse=True)
        
        return common_ngrams[:top_k]
    
    def get_unique_ngrams(self, text: str) -> Set[Tuple[str, ...]]:
        """
        Get unique n-grams from text.
        
        Args:
            text: Input text
            
        Returns:
            Set of unique n-grams
        """
        tokens = preprocessor.preprocess_for_ngrams(text, remove_stops=False)
        ngrams = self.generate_ngrams(tokens)
        return set(ngrams)


def calculate_ngram_similarity(
    query_text: str, 
    reference_texts: List[str],
    n: int = 2,
    method: str = "jaccard"
) -> Dict[str, any]:
    """
    Convenience function to calculate n-gram similarity.
    
    Args:
        query_text: Text to analyze
        reference_texts: List of reference texts
        n: N-gram size
        method: Similarity method
        
    Returns:
        Dictionary with similarity analysis
    """
    analyzer = NgramSimilarityAnalyzer(n=n)
    similarities = analyzer.compare_with_references(query_text, reference_texts, method)
    
    return {
        "ngram_size": n,
        "method": method,
        "similarities": [float(s) for s in similarities],
        "average_similarity": float(np.mean(similarities)) if similarities else 0.0,
        "max_similarity": float(np.max(similarities)) if similarities else 0.0
    }


def analyze_comprehensive_ngrams(
    text1: str, 
    text2: str
) -> Dict[str, any]:
    """
    Perform comprehensive n-gram analysis between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Detailed n-gram analysis results
    """
    # Multi n-gram analysis
    multi_results = NgramSimilarityAnalyzer().analyze_multi_ngram(text1, text2)
    
    # Find common bigrams
    bigram_analyzer = NgramSimilarityAnalyzer(n=2)
    common_bigrams = bigram_analyzer.get_common_ngrams(text1, text2, top_k=10)
    
    return {
        **multi_results,
        "common_bigrams": [
            {
                "ngram": " ".join(ng),
                "frequency": freq
            }
            for ng, freq in common_bigrams
        ]
    }
