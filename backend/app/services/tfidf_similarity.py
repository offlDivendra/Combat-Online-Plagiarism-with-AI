"""
TF-IDF Similarity Service
Implements TF-IDF vectorization and cosine similarity for document comparison.
"""

from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.preprocessing import preprocessor


class TfidfSimilarityAnalyzer:
    """
    Analyzes document similarity using TF-IDF (Term Frequency-Inverse Document Frequency)
    and cosine similarity metrics.
    """
    
    def __init__(self, max_features: int = 5000, ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize the TF-IDF analyzer.
        
        Args:
            max_features: Maximum number of features for TF-IDF vectorizer
            ngram_range: The range of n-grams to extract (default: unigrams and bigrams)
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer = None
        self.reference_vectors = None
        self.reference_documents = []
    
    def _create_vectorizer(self, num_docs: int = 10) -> TfidfVectorizer:
        """
        Create a TF-IDF vectorizer with appropriate settings.
        
        Args:
            num_docs: Number of documents (used to set safe max_df)
            
        Returns:
            Configured TfidfVectorizer instance
        """
        # When there's only 1 doc, max_df=0.95 means 0 docs which conflicts with min_df=1
        # Use 1.0 (no upper limit) when corpus is tiny
        max_df = 0.95 if num_docs >= 5 else 1.0
        return TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            lowercase=True,
            stop_words='english',
            strip_accents='unicode',
            token_pattern=r'\b[a-zA-Z]{2,}\b',  # Words with at least 2 letters
            min_df=1,  # Minimum document frequency
            max_df=max_df  # Maximum document frequency (ignore very common terms)
        )
    
    def fit_references(self, reference_texts: List[str]) -> None:
        """
        Fit the TF-IDF model on reference documents.
        
        Args:
            reference_texts: List of reference document texts
        """
        if not reference_texts:
            raise ValueError("Reference texts cannot be empty")
        
        # Preprocess reference texts
        processed_references = [
            preprocessor.preprocess_for_tfidf(text) 
            for text in reference_texts
        ]
        
        # Create and fit vectorizer
        self.vectorizer = self._create_vectorizer(num_docs=len(processed_references))
        self.reference_vectors = self.vectorizer.fit_transform(processed_references)
        self.reference_documents = processed_references
    
    def calculate_similarity(self, query_text: str) -> List[float]:
        """
        Calculate cosine similarity between query text and all reference documents.
        
        Args:
            query_text: Text to compare against references
            
        Returns:
            List of similarity scores (0-1) for each reference document
        """
        if self.vectorizer is None or self.reference_vectors is None:
            raise ValueError("Vectorizer not fitted. Call fit_references() first.")
        
        if not query_text or not query_text.strip():
            return [0.0] * len(self.reference_documents)
        
        # Preprocess query text
        processed_query = preprocessor.preprocess_for_tfidf(query_text)
        
        # Transform query to TF-IDF vector
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate cosine similarity with all reference documents
        similarities = cosine_similarity(query_vector, self.reference_vectors)[0]
        
        return similarities.tolist()
    
    def find_most_similar(
        self, 
        query_text: str, 
        top_k: int = None
    ) -> List[Dict[str, any]]:
        """
        Find the most similar reference documents to the query.
        
        Args:
            query_text: Text to compare
            top_k: Number of top results to return (None = all)
            
        Returns:
            List of dictionaries with document index and similarity score
        """
        similarities = self.calculate_similarity(query_text)
        
        # Create list of (index, similarity) tuples
        results = [
            {"index": idx, "similarity": float(sim)}
            for idx, sim in enumerate(similarities)
        ]
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top_k results
        if top_k is not None:
            results = results[:top_k]
        
        return results
    
    def get_average_similarity(self, query_text: str) -> float:
        """
        Calculate average similarity across all reference documents.
        
        Args:
            query_text: Text to compare
            
        Returns:
            Average similarity score (0-1)
        """
        similarities = self.calculate_similarity(query_text)
        
        if not similarities:
            return 0.0
        
        return float(np.mean(similarities))
    
    def get_max_similarity(self, query_text: str) -> float:
        """
        Get maximum similarity score across all reference documents.
        
        Args:
            query_text: Text to compare
            
        Returns:
            Maximum similarity score (0-1)
        """
        similarities = self.calculate_similarity(query_text)
        
        if not similarities:
            return 0.0
        
        return float(np.max(similarities))
    
    def compare_documents(
        self, 
        query_text: str, 
        reference_texts: List[str]
    ) -> Dict[str, any]:
        """
        Complete TF-IDF comparison between query and reference documents.
        
        Args:
            query_text: Text to analyze
            reference_texts: List of reference document texts
            
        Returns:
            Dictionary with detailed similarity analysis
        """
        if not reference_texts:
            return {
                "average_similarity": 0.0,
                "max_similarity": 0.0,
                "similarities": [],
                "top_matches": []
            }
        
        # Fit references
        self.fit_references(reference_texts)
        
        # Calculate similarities
        similarities = self.calculate_similarity(query_text)
        
        # Get top matches
        top_matches = self.find_most_similar(query_text, top_k=5)
        
        return {
            "average_similarity": float(np.mean(similarities)),
            "max_similarity": float(np.max(similarities)),
            "similarities": [float(s) for s in similarities],
            "top_matches": top_matches
        }
    
    def get_important_terms(self, text: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Extract the most important terms from text based on TF-IDF scores.
        
        Args:
            text: Input text
            top_n: Number of top terms to return
            
        Returns:
            List of (term, score) tuples
        """
        if self.vectorizer is None:
            # Create temporary vectorizer
            temp_vectorizer = self._create_vectorizer(num_docs=1)
            vector = temp_vectorizer.fit_transform([text])
            feature_names = temp_vectorizer.get_feature_names_out()
        else:
            vector = self.vectorizer.transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
        
        # Get TF-IDF scores
        scores = vector.toarray()[0]
        
        # Create list of (term, score) tuples
        term_scores = [
            (feature_names[idx], scores[idx])
            for idx in range(len(scores))
            if scores[idx] > 0
        ]
        
        # Sort by score (descending)
        term_scores.sort(key=lambda x: x[1], reverse=True)
        
        return term_scores[:top_n]


def calculate_tfidf_similarity(
    query_text: str, 
    reference_texts: List[str]
) -> Dict[str, any]:
    """
    Convenience function to calculate TF-IDF similarity.
    
    Args:
        query_text: Text to analyze
        reference_texts: List of reference document texts
        
    Returns:
        Dictionary with similarity scores and analysis
    """
    analyzer = TfidfSimilarityAnalyzer()
    return analyzer.compare_documents(query_text, reference_texts)


def get_similarity_percentage(similarity_score: float) -> float:
    """
    Convert similarity score (0-1) to percentage (0-100).
    
    Args:
        similarity_score: Similarity score between 0 and 1
        
    Returns:
        Percentage value between 0 and 100
    """
    return round(similarity_score * 100, 2)
