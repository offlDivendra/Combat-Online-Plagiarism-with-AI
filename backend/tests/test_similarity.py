"""
Unit tests for similarity services.
"""

import pytest
from app.services.tfidf_similarity import TfidfSimilarityAnalyzer, calculate_tfidf_similarity
from app.services.ngram_similarity import NgramSimilarityAnalyzer, calculate_ngram_similarity
from app.services.fuzzy_matching import FuzzyMatchingAnalyzer, calculate_fuzzy_similarity


class TestTfidfSimilarity:
    """Test cases for TF-IDF similarity analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TfidfSimilarityAnalyzer()
        self.ref_texts = [
            "Machine learning is a branch of artificial intelligence.",
            "Climate change affects global temperatures and weather patterns.",
            "Cybersecurity protects systems from digital attacks."
        ]
    
    def test_fit_references(self):
        """Test fitting on reference documents."""
        self.analyzer.fit_references(self.ref_texts)
        assert self.analyzer.vectorizer is not None
        assert self.analyzer.reference_vectors is not None
    
    def test_fit_references_empty_raises_error(self):
        """Test that empty reference list raises error."""
        with pytest.raises(ValueError):
            self.analyzer.fit_references([])
    
    def test_calculate_similarity_identical(self):
        """Test similarity of identical texts."""
        text = "Machine learning is a branch of artificial intelligence."
        self.analyzer.fit_references([text])
        similarities = self.analyzer.calculate_similarity(text)
        assert similarities[0] > 0.95  # Should be very high
    
    def test_calculate_similarity_different(self):
        """Test similarity of completely different texts."""
        self.analyzer.fit_references(self.ref_texts)
        query = "The ancient Romans built impressive aqueducts."
        similarities = self.analyzer.calculate_similarity(query)
        # Should have low similarity with all references
        assert all(sim < 0.5 for sim in similarities)
    
    def test_calculate_similarity_similar(self):
        """Test similarity of similar texts."""
        self.analyzer.fit_references(self.ref_texts)
        query = "Artificial intelligence includes machine learning techniques."
        similarities = self.analyzer.calculate_similarity(query)
        # Should have highest similarity with first reference
        assert similarities[0] > similarities[1]
        assert similarities[0] > similarities[2]
    
    def test_find_most_similar(self):
        """Test finding most similar documents."""
        self.analyzer.fit_references(self.ref_texts)
        query = "Machine learning and AI are related fields."
        results = self.analyzer.find_most_similar(query, top_k=2)
        
        assert len(results) <= 2
        assert all("index" in r for r in results)
        assert all("similarity" in r for r in results)
        # Results should be sorted by similarity
        if len(results) > 1:
            assert results[0]["similarity"] >= results[1]["similarity"]
    
    def test_get_average_similarity(self):
        """Test average similarity calculation."""
        self.analyzer.fit_references(self.ref_texts)
        query = "Machine learning is important."
        avg_sim = self.analyzer.get_average_similarity(query)
        assert 0 <= avg_sim <= 1
    
    def test_get_max_similarity(self):
        """Test maximum similarity calculation."""
        self.analyzer.fit_references(self.ref_texts)
        query = "Machine learning is important."
        max_sim = self.analyzer.get_max_similarity(query)
        assert 0 <= max_sim <= 1
    
    def test_compare_documents(self):
        """Test complete document comparison."""
        query = "Machine learning helps computers learn from data."
        result = self.analyzer.compare_documents(query, self.ref_texts)
        
        assert "average_similarity" in result
        assert "max_similarity" in result
        assert "similarities" in result
        assert "top_matches" in result
        assert len(result["similarities"]) == len(self.ref_texts)


class TestNgramSimilarity:
    """Test cases for N-gram similarity analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = NgramSimilarityAnalyzer(n=2)
    
    def test_generate_ngrams(self):
        """Test n-gram generation."""
        tokens = ["machine", "learning", "is", "great"]
        ngrams = self.analyzer.generate_ngrams(tokens, n=2)
        assert len(ngrams) == 3  # 4 tokens - 2 + 1
        assert ("machine", "learning") in ngrams
        assert ("learning", "is") in ngrams
        assert ("is", "great") in ngrams
    
    def test_generate_ngrams_insufficient_tokens(self):
        """Test n-gram generation with insufficient tokens."""
        tokens = ["one"]
        ngrams = self.analyzer.generate_ngrams(tokens, n=2)
        assert ngrams == []
    
    def test_jaccard_similarity_identical(self):
        """Test Jaccard similarity of identical sets."""
        set1 = {1, 2, 3, 4}
        set2 = {1, 2, 3, 4}
        similarity = self.analyzer.jaccard_similarity(set1, set2)
        assert similarity == 1.0
    
    def test_jaccard_similarity_disjoint(self):
        """Test Jaccard similarity of disjoint sets."""
        set1 = {1, 2, 3}
        set2 = {4, 5, 6}
        similarity = self.analyzer.jaccard_similarity(set1, set2)
        assert similarity == 0.0
    
    def test_jaccard_similarity_partial(self):
        """Test Jaccard similarity of partially overlapping sets."""
        set1 = {1, 2, 3, 4}
        set2 = {3, 4, 5, 6}
        similarity = self.analyzer.jaccard_similarity(set1, set2)
        assert 0 < similarity < 1
    
    def test_calculate_similarity_identical(self):
        """Test similarity of identical texts."""
        text = "Machine learning is amazing"
        similarity = self.analyzer.calculate_similarity(text, text)
        assert similarity > 0.9  # Should be very high
    
    def test_calculate_similarity_different(self):
        """Test similarity of different texts."""
        text1 = "Machine learning is amazing"
        text2 = "The ancient Romans built aqueducts"
        similarity = self.analyzer.calculate_similarity(text1, text2)
        assert similarity < 0.3  # Should be low
    
    def test_calculate_similarity_methods(self):
        """Test different similarity methods."""
        text1 = "Machine learning is a field"
        text2 = "Machine learning is important"
        
        jaccard = self.analyzer.calculate_similarity(text1, text2, method="jaccard")
        cosine = self.analyzer.calculate_similarity(text1, text2, method="cosine")
        dice = self.analyzer.calculate_similarity(text1, text2, method="dice")
        
        # All should return valid scores
        assert 0 <= jaccard <= 1
        assert 0 <= cosine <= 1
        assert 0 <= dice <= 1
    
    def test_compare_with_references(self):
        """Test comparison with multiple references."""
        query = "Machine learning is great"
        references = [
            "Machine learning is amazing",
            "Climate change is serious",
            "Cybersecurity is important"
        ]
        
        similarities = self.analyzer.compare_with_references(query, references)
        assert len(similarities) == len(references)
        # First reference should be most similar
        assert similarities[0] > similarities[1]
        assert similarities[0] > similarities[2]
    
    def test_analyze_multi_ngram(self):
        """Test multi-ngram analysis."""
        text1 = "Machine learning helps solve problems"
        text2 = "Machine learning solves complex problems"
        
        result = self.analyzer.analyze_multi_ngram(text1, text2)
        
        assert "1gram_similarity" in result
        assert "2gram_similarity" in result
        assert "3gram_similarity" in result
        assert "average_ngram_similarity" in result
    
    def test_get_common_ngrams(self):
        """Test finding common n-grams."""
        text1 = "Machine learning is a branch of artificial intelligence"
        text2 = "Machine learning and artificial intelligence are related"
        
        common = self.analyzer.get_common_ngrams(text1, text2, top_k=5)
        
        assert len(common) <= 5
        # Check format: list of (ngram, frequency) tuples
        if common:
            assert isinstance(common[0], tuple)
            assert isinstance(common[0][0], tuple)  # ngram is tuple
            assert isinstance(common[0][1], int)    # frequency is int


class TestFuzzyMatching:
    """Test cases for fuzzy matching analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FuzzyMatchingAnalyzer(threshold=75.0)
    
    def test_simple_ratio_identical(self):
        """Test simple ratio on identical texts."""
        text = "Machine learning is amazing"
        score = self.analyzer.simple_ratio(text, text)
        assert score == 100.0
    
    def test_simple_ratio_different(self):
        """Test simple ratio on different texts."""
        text1 = "Machine learning"
        text2 = "Ancient Rome"
        score = self.analyzer.simple_ratio(text1, text2)
        assert score < 50.0
    
    def test_token_sort_ratio(self):
        """Test token sort ratio handles word order."""
        text1 = "machine learning is great"
        text2 = "great is machine learning"
        score = self.analyzer.token_sort_ratio(text1, text2)
        assert score > 90.0  # Should be high despite word order
    
    def test_partial_ratio(self):
        """Test partial ratio for substring matching."""
        text1 = "machine learning"
        text2 = "machine learning is a field of artificial intelligence"
        score = self.analyzer.partial_ratio(text1, text2)
        assert score > 90.0  # text1 is substring of text2
    
    def test_comprehensive_similarity(self):
        """Test comprehensive similarity analysis."""
        text1 = "Machine learning is important"
        text2 = "Machine learning is crucial"
        
        result = self.analyzer.comprehensive_similarity(text1, text2)
        
        assert "simple_ratio" in result
        assert "partial_ratio" in result
        assert "token_sort_ratio" in result
        assert "token_set_ratio" in result
        assert "weighted_ratio" in result
        
        # All scores should be in valid range
        for score in result.values():
            assert 0 <= score <= 100
    
    def test_best_similarity(self):
        """Test getting best similarity score."""
        text1 = "Machine learning is important"
        text2 = "Machine learning is crucial"
        
        best = self.analyzer.best_similarity(text1, text2)
        assert 0 <= best <= 100
    
    def test_average_similarity(self):
        """Test getting average similarity score."""
        text1 = "Machine learning is important"
        text2 = "Machine learning is crucial"
        
        avg = self.analyzer.average_similarity(text1, text2)
        assert 0 <= avg <= 100
    
    def test_sentence_similarity(self):
        """Test sentence similarity matching."""
        query = "Machine learning is a field of AI"
        references = [
            "Machine learning is a branch of artificial intelligence",
            "Climate change affects the environment",
            "Cybersecurity protects computer systems"
        ]
        
        matches = self.analyzer.sentence_similarity(query, references)
        
        # Should find matches above threshold
        if matches:
            assert all(isinstance(m, tuple) for m in matches)
            assert all(len(m) == 3 for m in matches)  # (sentence, score, index)
            # Scores should be above threshold
            assert all(m[1] >= self.analyzer.threshold for m in matches)
    
    def test_find_best_match(self):
        """Test finding best match from choices."""
        query = "Machine learning techniques"
        choices = [
            "Machine learning algorithms",
            "Climate change effects",
            "Cybersecurity measures"
        ]
        
        matches = self.analyzer.find_best_match(query, choices, limit=1)
        
        assert len(matches) <= 1
        if matches:
            # First choice should match best
            assert matches[0][2] == 0  # index of first choice
    
    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation."""
        text1 = "kitten"
        text2 = "sitting"
        distance = self.analyzer.levenshtein_distance(text1, text2)
        assert distance == 3  # Known edit distance
    
    def test_normalized_levenshtein_similarity(self):
        """Test normalized Levenshtein similarity."""
        text1 = "hello"
        text2 = "hello"
        similarity = self.analyzer.normalized_levenshtein_similarity(text1, text2)
        assert similarity == 1.0
        
        text1 = "hello"
        text2 = "world"
        similarity = self.analyzer.normalized_levenshtein_similarity(text1, text2)
        assert 0 <= similarity < 1.0


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""
    
    def test_calculate_tfidf_similarity(self):
        """Test TF-IDF convenience function."""
        query = "Machine learning is great"
        references = ["Machine learning is amazing", "Climate change is serious"]
        
        result = calculate_tfidf_similarity(query, references)
        assert "average_similarity" in result
        assert "max_similarity" in result
    
    def test_calculate_ngram_similarity(self):
        """Test N-gram convenience function."""
        query = "Machine learning"
        references = ["Machine learning algorithms", "Climate change"]
        
        result = calculate_ngram_similarity(query, references, n=2)
        assert "ngram_size" in result
        assert "similarities" in result
        assert result["ngram_size"] == 2
    
    def test_calculate_fuzzy_similarity(self):
        """Test fuzzy matching convenience function."""
        text1 = "Machine learning"
        text2 = "Machine learning algorithms"
        
        score = calculate_fuzzy_similarity(text1, text2)
        assert 0 <= score <= 100
