"""
Plagiarism Detection Engine
Combines TF-IDF, N-gram, and Fuzzy Matching to detect plagiarism with configurable weights.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime

from app.config import settings
from app.services.preprocessing import preprocessor
from app.services.tfidf_similarity import TfidfSimilarityAnalyzer
from app.services.ngram_similarity import NgramSimilarityAnalyzer
from app.services.fuzzy_matching import FuzzyMatchingAnalyzer


class PlagiarismEngine:
    """
    Main plagiarism detection engine that combines multiple similarity algorithms.
    """
    
    def __init__(
        self,
        tfidf_weight: float = None,
        ngram_weight: float = None,
        fuzzy_weight: float = None
    ):
        """
        Initialize the plagiarism engine.
        
        Args:
            tfidf_weight: Weight for TF-IDF similarity (uses config default if None)
            ngram_weight: Weight for N-gram similarity (uses config default if None)
            fuzzy_weight: Weight for Fuzzy matching (uses config default if None)
        """
        self.tfidf_weight = tfidf_weight or settings.TFIDF_WEIGHT
        self.ngram_weight = ngram_weight or settings.NGRAM_WEIGHT
        self.fuzzy_weight = fuzzy_weight or settings.FUZZY_WEIGHT
        
        # Validate weights
        total_weight = self.tfidf_weight + self.ngram_weight + self.fuzzy_weight
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(
                f"Weights must sum to 1.0. Current sum: {total_weight}"
            )
        
        # Initialize analyzers
        self.tfidf_analyzer = TfidfSimilarityAnalyzer()
        self.ngram_analyzer = NgramSimilarityAnalyzer(n=2)  # Bigrams
        self.fuzzy_analyzer = FuzzyMatchingAnalyzer(
            threshold=settings.FUZZY_MATCH_THRESHOLD
        )
    
    def calculate_combined_similarity(
        self,
        tfidf_score: float,
        ngram_score: float,
        fuzzy_score: float
    ) -> float:
        """
        Calculate weighted combined similarity score.
        
        Args:
            tfidf_score: TF-IDF similarity (0-1)
            ngram_score: N-gram similarity (0-1)
            fuzzy_score: Fuzzy matching similarity (0-100)
            
        Returns:
            Combined similarity score (0-100)
        """
        # Normalize fuzzy score to 0-1 scale
        fuzzy_normalized = fuzzy_score / 100.0
        
        # Calculate weighted average
        combined = (
            self.tfidf_weight * tfidf_score +
            self.ngram_weight * ngram_score +
            self.fuzzy_weight * fuzzy_normalized
        )
        
        # Convert to percentage
        return round(combined * 100, 2)
    
    def classify_similarity(self, similarity: float) -> str:
        """
        Classify similarity score into categories.
        
        Args:
            similarity: Similarity percentage (0-100)
            
        Returns:
            Classification label
        """
        return settings.get_classification(similarity)
    
    def analyze_sentence_matches(
        self,
        query_sentences: List[str],
        reference_sentences: List[str],
        reference_name: str = "Reference"
    ) -> List[Dict[str, any]]:
        """
        Find sentence-level matches using fuzzy matching.
        
        Args:
            query_sentences: List of query sentences
            reference_sentences: List of reference sentences
            reference_name: Name of reference document
            
        Returns:
            List of sentence match dictionaries
        """
        matches = []
        
        for query_idx, query_sent in enumerate(query_sentences):
            if len(query_sent) < settings.MIN_SENTENCE_LENGTH:
                continue
            
            # Find best matching reference sentence
            similar_sentences = self.fuzzy_analyzer.sentence_similarity(
                query_sent,
                reference_sentences,
                method="weighted"
            )
            
            if similar_sentences:
                best_match = similar_sentences[0]
                matched_sent, score, ref_idx = best_match
                
                matches.append({
                    "submitted_sentence": query_sent,
                    "matched_sentence": matched_sent,
                    "similarity": round(score, 2),
                    "source": reference_name,
                    "query_index": query_idx,
                    "reference_index": ref_idx,
                    "method": "fuzzy_matching"
                })
        
        return matches
    
    def analyze_document(
        self,
        query_text: str,
        reference_texts: List[str],
        reference_names: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Perform complete plagiarism analysis on a document.
        
        Args:
            query_text: Text to analyze
            reference_texts: List of reference document texts
            reference_names: Optional names for reference documents
            
        Returns:
            Comprehensive plagiarism analysis results
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")
        
        if not reference_texts:
            raise ValueError("At least one reference document is required")
        
        # Generate default names if not provided
        if reference_names is None:
            reference_names = [f"document_{i+1:02d}" for i in range(len(reference_texts))]
        
        # Preprocess query document
        query_processed = preprocessor.preprocess_document(query_text)
        
        # Initialize result storage
        all_similarities = []
        source_results = []
        all_sentence_matches = []
        
        # Analyze against each reference document
        for ref_idx, (ref_text, ref_name) in enumerate(zip(reference_texts, reference_names)):
            # Preprocess reference
            ref_processed = preprocessor.preprocess_document(ref_text)
            
            # TF-IDF Similarity
            if ref_idx == 0:
                # Fit on first reference, then reuse
                self.tfidf_analyzer.fit_references([ref_text])
                tfidf_score = self.tfidf_analyzer.get_max_similarity(query_text)
            else:
                self.tfidf_analyzer.fit_references([ref_text])
                tfidf_score = self.tfidf_analyzer.get_max_similarity(query_text)
            
            # N-gram Similarity
            ngram_score = self.ngram_analyzer.calculate_similarity(
                query_text,
                ref_text,
                method="jaccard"
            )
            
            # Fuzzy Matching
            fuzzy_result = self.fuzzy_analyzer.analyze_document_similarity(
                query_text,
                ref_text
            )
            fuzzy_score = fuzzy_result["overall_similarity"]
            
            # Calculate combined similarity
            combined_similarity = self.calculate_combined_similarity(
                tfidf_score,
                ngram_score,
                fuzzy_score
            )
            
            all_similarities.append(combined_similarity)
            
            # Find sentence matches
            sentence_matches = self.analyze_sentence_matches(
                query_processed["sentences"],
                ref_processed["sentences"],
                ref_name
            )
            
            all_sentence_matches.extend(sentence_matches)
            
            # Store source result
            source_results.append({
                "name": ref_name,
                "similarity": combined_similarity,
                "tfidf_score": round(tfidf_score * 100, 2),
                "ngram_score": round(ngram_score * 100, 2),
                "fuzzy_score": round(fuzzy_score, 2),
                "matched_sentences": len(sentence_matches)
            })
        
        # Sort sources by similarity
        source_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Calculate overall statistics
        overall_similarity = max(all_similarities) if all_similarities else 0.0
        average_similarity = np.mean(all_similarities) if all_similarities else 0.0
        
        # Get individual component scores (from highest matching source)
        if source_results:
            top_source = source_results[0]
            component_scores = {
                "tfidf": top_source["tfidf_score"],
                "ngram": top_source["ngram_score"],
                "fuzzy": top_source["fuzzy_score"]
            }
        else:
            component_scores = {"tfidf": 0.0, "ngram": 0.0, "fuzzy": 0.0}
        
        # Sort sentence matches by similarity
        all_sentence_matches.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Classification
        classification = self.classify_similarity(overall_similarity)
        
        return {
            "document_name": "submitted_document",
            "analysis_date": datetime.now().isoformat(),
            "word_count": query_processed["word_count"],
            "sentence_count": query_processed["sentence_count"],
            "overall_similarity": overall_similarity,
            "average_similarity": round(average_similarity, 2),
            "classification": classification,
            "scores": component_scores,
            "weights": {
                "tfidf_weight": self.tfidf_weight,
                "ngram_weight": self.ngram_weight,
                "fuzzy_weight": self.fuzzy_weight
            },
            "sources": source_results,
            "sentence_matches": all_sentence_matches[:50],  # Limit to top 50
            "total_matches": len(all_sentence_matches),
            "high_similarity_matches": sum(
                1 for m in all_sentence_matches if m["similarity"] >= 80.0
            )
        }
    
    def quick_analyze(
        self,
        query_text: str,
        reference_text: str
    ) -> Dict[str, any]:
        """
        Quick plagiarism check between two documents.
        
        Args:
            query_text: Text to analyze
            reference_text: Reference text
            
        Returns:
            Simplified analysis results
        """
        result = self.analyze_document(query_text, [reference_text], ["reference"])
        
        return {
            "similarity": result["overall_similarity"],
            "classification": result["classification"],
            "scores": result["scores"],
            "matched_sentences": result["total_matches"]
        }
    
    def batch_analyze(
        self,
        query_texts: List[str],
        reference_texts: List[str]
    ) -> List[Dict[str, any]]:
        """
        Analyze multiple query documents against reference documents.
        
        Args:
            query_texts: List of texts to analyze
            reference_texts: List of reference texts
            
        Returns:
            List of analysis results for each query
        """
        results = []
        
        for idx, query_text in enumerate(query_texts):
            try:
                result = self.analyze_document(
                    query_text,
                    reference_texts,
                    reference_names=[f"ref_{i+1}" for i in range(len(reference_texts))]
                )
                result["query_index"] = idx
                results.append(result)
            except Exception as e:
                results.append({
                    "query_index": idx,
                    "error": str(e),
                    "overall_similarity": 0.0
                })
        
        return results
    
    def get_detailed_report_data(
        self,
        analysis_result: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Prepare detailed data for report generation.
        
        Args:
            analysis_result: Result from analyze_document()
            
        Returns:
            Enhanced data for report generation
        """
        return {
            **analysis_result,
            "thresholds": {
                "low": settings.THRESHOLD_LOW,
                "moderate": settings.THRESHOLD_MODERATE,
                "high": settings.THRESHOLD_HIGH,
                "plagiarism": settings.THRESHOLD_PLAGIARISM
            },
            "algorithm_info": {
                "methods": ["TF-IDF", "N-Grams", "Fuzzy Matching"],
                "description": (
                    "This system uses a combination of three NLP techniques: "
                    "TF-IDF for term importance, N-grams for phrase matching, "
                    "and Fuzzy Matching for paraphrase detection."
                )
            },
            "disclaimer": (
                "This similarity score indicates textual overlap and should be "
                "reviewed by a human before concluding plagiarism. Common phrases "
                "and domain-specific terminology may create false positives."
            )
        }


# Global engine instance
plagiarism_engine = PlagiarismEngine()


# Convenience functions
def detect_plagiarism(
    query_text: str,
    reference_texts: List[str],
    reference_names: Optional[List[str]] = None
) -> Dict[str, any]:
    """
    Convenience function to detect plagiarism.
    
    Args:
        query_text: Text to analyze
        reference_texts: List of reference texts
        reference_names: Optional names for references
        
    Returns:
        Plagiarism analysis results
    """
    return plagiarism_engine.analyze_document(
        query_text,
        reference_texts,
        reference_names
    )


def quick_check(query_text: str, reference_text: str) -> float:
    """
    Quick similarity check returning only the percentage.
    
    Args:
        query_text: Text to analyze
        reference_text: Reference text
        
    Returns:
        Similarity percentage (0-100)
    """
    result = plagiarism_engine.quick_analyze(query_text, reference_text)
    return result["similarity"]
