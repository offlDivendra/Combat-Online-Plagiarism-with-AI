"""
Unit tests for text preprocessing service.
"""

import pytest
from app.services.preprocessing import (
    TextPreprocessor, normalize_text, clean_text,
    tokenize_text, remove_stopwords, split_sentences,
    preprocess_document
)


class TestTextPreprocessor:
    """Test cases for TextPreprocessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = TextPreprocessor()
    
    def test_normalize_text_lowercase(self):
        """Test text normalization converts to lowercase."""
        text = "Hello WORLD!"
        result = self.preprocessor.normalize_text(text)
        assert result == "hello world!"
    
    def test_normalize_text_whitespace(self):
        """Test text normalization handles multiple whitespaces."""
        text = "Hello    World   Test"
        result = self.preprocessor.normalize_text(text)
        assert result == "hello world test"
    
    def test_normalize_text_empty(self):
        """Test text normalization handles empty input."""
        result = self.preprocessor.normalize_text("")
        assert result == ""
    
    def test_clean_text_removes_urls(self):
        """Test clean_text removes URLs."""
        text = "Check this link https://example.com for more info"
        result = self.preprocessor.clean_text(text)
        assert "https://example.com" not in result
        assert "Check this link" in result
    
    def test_clean_text_removes_emails(self):
        """Test clean_text removes email addresses."""
        text = "Contact me at test@example.com"
        result = self.preprocessor.clean_text(text)
        assert "test@example.com" not in result
    
    def test_clean_text_with_punctuation(self):
        """Test clean_text preserves punctuation when not removing."""
        text = "Hello, world! How are you?"
        result = self.preprocessor.clean_text(text, remove_punctuation=False)
        assert "," in result or "!" in result or "?" in result
    
    def test_clean_text_without_punctuation(self):
        """Test clean_text removes punctuation when specified."""
        text = "Hello, world! How are you?"
        result = self.preprocessor.clean_text(text, remove_punctuation=True)
        assert "," not in result
        assert "!" not in result
        assert "?" not in result
    
    def test_tokenize_text_basic(self):
        """Test basic text tokenization."""
        text = "Machine learning is amazing"
        tokens = self.preprocessor.tokenize_text(text)
        assert len(tokens) > 0
        assert "Machine" in tokens or "machine" in tokens
        assert "learning" in tokens
    
    def test_tokenize_text_empty(self):
        """Test tokenization of empty text."""
        tokens = self.preprocessor.tokenize_text("")
        assert tokens == []
    
    def test_remove_stopwords(self):
        """Test stopword removal."""
        tokens = ["the", "machine", "learning", "is", "a", "field"]
        filtered = self.preprocessor.remove_stopwords(tokens)
        assert "machine" in filtered
        assert "learning" in filtered
        assert "field" in filtered
        assert "the" not in filtered
        assert "is" not in filtered
        assert "a" not in filtered
    
    def test_remove_stopwords_empty(self):
        """Test stopword removal with empty input."""
        filtered = self.preprocessor.remove_stopwords([])
        assert filtered == []
    
    def test_split_sentences(self):
        """Test sentence splitting."""
        text = "This is first sentence. This is second sentence. This is third."
        sentences = self.preprocessor.split_sentences(text)
        assert len(sentences) == 3
    
    def test_split_sentences_min_length(self):
        """Test sentence splitting respects minimum length."""
        text = "This is a long sentence that should be included. Short. Another long sentence here."
        sentences = self.preprocessor.split_sentences(text, min_length=20)
        # Should only include sentences longer than 20 characters
        for sent in sentences:
            assert len(sent) >= 20
    
    def test_split_sentences_empty(self):
        """Test sentence splitting with empty text."""
        sentences = self.preprocessor.split_sentences("")
        assert sentences == []
    
    def test_preprocess_for_tfidf(self):
        """Test preprocessing for TF-IDF."""
        text = "Machine Learning is a Field of AI!"
        result = self.preprocessor.preprocess_for_tfidf(text)
        assert result.islower()
        assert len(result) > 0
    
    def test_preprocess_for_ngrams(self):
        """Test preprocessing for n-grams."""
        text = "Machine learning is a field of artificial intelligence."
        tokens = self.preprocessor.preprocess_for_ngrams(text, remove_stops=True)
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        # Check stopwords removed
        assert "is" not in tokens
        assert "a" not in tokens
    
    def test_get_word_count(self):
        """Test word counting."""
        text = "Machine learning is amazing"
        count = self.preprocessor.get_word_count(text)
        assert count == 4
    
    def test_get_word_count_empty(self):
        """Test word count with empty text."""
        count = self.preprocessor.get_word_count("")
        assert count == 0
    
    def test_get_sentence_count(self):
        """Test sentence counting."""
        text = "First sentence. Second sentence. Third sentence."
        count = self.preprocessor.get_sentence_count(text)
        assert count == 3
    
    def test_preprocess_document_complete(self):
        """Test complete document preprocessing."""
        text = "Machine learning is amazing. It can solve complex problems."
        result = self.preprocessor.preprocess_document(text)
        
        assert "original" in result
        assert "normalized" in result
        assert "cleaned" in result
        assert "sentences" in result
        assert "tokens" in result
        assert "tokens_no_stops" in result
        assert "word_count" in result
        assert "sentence_count" in result
        
        assert result["original"] == text
        assert len(result["sentences"]) > 0
        assert result["word_count"] > 0
        assert result["sentence_count"] > 0
    
    def test_preprocess_document_empty(self):
        """Test document preprocessing with empty input."""
        result = self.preprocessor.preprocess_document("")
        assert result["word_count"] == 0
        assert result["sentence_count"] == 0
        assert len(result["sentences"]) == 0


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""
    
    def test_normalize_text_function(self):
        """Test normalize_text convenience function."""
        result = normalize_text("HELLO World")
        assert result == "hello world"
    
    def test_clean_text_function(self):
        """Test clean_text convenience function."""
        result = clean_text("Hello, world!")
        assert len(result) > 0
    
    def test_tokenize_text_function(self):
        """Test tokenize_text convenience function."""
        tokens = tokenize_text("Machine learning")
        assert len(tokens) > 0
    
    def test_remove_stopwords_function(self):
        """Test remove_stopwords convenience function."""
        tokens = ["the", "machine", "is"]
        filtered = remove_stopwords(tokens)
        assert "machine" in filtered
        assert "the" not in filtered
    
    def test_split_sentences_function(self):
        """Test split_sentences convenience function."""
        sentences = split_sentences("First. Second. Third.")
        assert len(sentences) > 0
    
    def test_preprocess_document_function(self):
        """Test preprocess_document convenience function."""
        result = preprocess_document("Test text here.")
        assert "word_count" in result
        assert result["word_count"] > 0
