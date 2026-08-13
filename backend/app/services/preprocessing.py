"""
Text Preprocessing Service
Handles text normalization, tokenization, sentence splitting, and stopword removal.
"""

import re
import string
from typing import List, Dict
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Download required NLTK data (will be skipped if already downloaded)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class TextPreprocessor:
    """
    Handles all text preprocessing operations for plagiarism detection.
    """
    
    def __init__(self):
        """Initialize the preprocessor with stopwords."""
        self.stopwords = set(stopwords.words('english'))
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by converting to lowercase and handling whitespace.
        
        Args:
            text: Raw input text
            
        Returns:
            Normalized text string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Replace multiple whitespaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading and trailing whitespace
        text = text.strip()
        
        return text
    
    def clean_text(self, text: str, remove_punctuation: bool = False) -> str:
        """
        Clean text by removing special characters and optionally punctuation.
        
        Args:
            text: Input text
            remove_punctuation: Whether to remove punctuation marks
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove numbers (optional - keeping them for now as they might be relevant)
        # text = re.sub(r'\d+', '', text)
        
        # Remove special characters but keep basic punctuation for sentence structure
        if not remove_punctuation:
            text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\-\'\"()]', '', text)
        else:
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of word tokens
        """
        if not text:
            return []
        
        try:
            tokens = word_tokenize(text)
            return tokens
        except Exception as e:
            # Fallback to simple split if NLTK fails
            return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove common stopwords from token list.
        
        Args:
            tokens: List of word tokens
            
        Returns:
            List of tokens with stopwords removed
        """
        if not tokens:
            return []
        
        # Keep words that are not in stopwords set
        filtered_tokens = [
            token for token in tokens 
            if token.lower() not in self.stopwords and len(token) > 1
        ]
        
        return filtered_tokens
    
    def split_sentences(self, text: str, min_length: int = 10) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            min_length: Minimum sentence length in characters
            
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        try:
            sentences = sent_tokenize(text)
        except Exception:
            # Fallback to simple split on periods
            sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        # Filter out very short sentences
        sentences = [
            sent.strip() for sent in sentences 
            if len(sent.strip()) >= min_length
        ]
        
        return sentences
    
    def preprocess_for_tfidf(self, text: str) -> str:
        """
        Preprocess text specifically for TF-IDF vectorization.
        Applies normalization and cleaning but preserves sentence structure.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text suitable for TF-IDF
        """
        # Normalize
        text = self.normalize_text(text)
        
        # Clean but keep punctuation for sentence boundaries
        text = self.clean_text(text, remove_punctuation=False)
        
        return text
    
    def preprocess_for_ngrams(self, text: str, remove_stops: bool = True) -> List[str]:
        """
        Preprocess text for n-gram analysis.
        
        Args:
            text: Input text
            remove_stops: Whether to remove stopwords
            
        Returns:
            List of tokens ready for n-gram generation
        """
        # Normalize and clean
        text = self.normalize_text(text)
        text = self.clean_text(text, remove_punctuation=True)
        
        # Tokenize
        tokens = self.tokenize_text(text)
        
        # Optionally remove stopwords
        if remove_stops:
            tokens = self.remove_stopwords(tokens)
        
        return tokens
    
    def get_word_count(self, text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Input text
            
        Returns:
            Number of words
        """
        if not text:
            return 0
        
        tokens = self.tokenize_text(text)
        return len(tokens)
    
    def get_sentence_count(self, text: str) -> int:
        """
        Count sentences in text.
        
        Args:
            text: Input text
            
        Returns:
            Number of sentences
        """
        sentences = self.split_sentences(text)
        return len(sentences)
    
    def preprocess_document(self, text: str) -> Dict:
        """
        Perform complete preprocessing on a document and return all variants.
        
        Args:
            text: Raw document text
            
        Returns:
            Dictionary containing different preprocessed versions
        """
        if not text:
            return {
                "original": "",
                "normalized": "",
                "cleaned": "",
                "sentences": [],
                "tokens": [],
                "tokens_no_stops": [],
                "word_count": 0,
                "sentence_count": 0
            }
        
        # Get normalized version
        normalized = self.normalize_text(text)
        
        # Get cleaned version
        cleaned = self.clean_text(normalized, remove_punctuation=False)
        
        # Split into sentences
        sentences = self.split_sentences(cleaned)
        
        # Tokenize
        tokens = self.tokenize_text(cleaned)
        
        # Remove stopwords
        tokens_no_stops = self.remove_stopwords(tokens)
        
        return {
            "original": text,
            "normalized": normalized,
            "cleaned": cleaned,
            "sentences": sentences,
            "tokens": tokens,
            "tokens_no_stops": tokens_no_stops,
            "word_count": len(tokens),
            "sentence_count": len(sentences)
        }


# Global preprocessor instance
preprocessor = TextPreprocessor()


# Convenience functions
def normalize_text(text: str) -> str:
    """Normalize text using global preprocessor."""
    return preprocessor.normalize_text(text)


def clean_text(text: str, remove_punctuation: bool = False) -> str:
    """Clean text using global preprocessor."""
    return preprocessor.clean_text(text, remove_punctuation)


def tokenize_text(text: str) -> List[str]:
    """Tokenize text using global preprocessor."""
    return preprocessor.tokenize_text(text)


def remove_stopwords(tokens: List[str]) -> List[str]:
    """Remove stopwords using global preprocessor."""
    return preprocessor.remove_stopwords(tokens)


def split_sentences(text: str, min_length: int = 10) -> List[str]:
    """Split text into sentences using global preprocessor."""
    return preprocessor.split_sentences(text, min_length)


def preprocess_document(text: str) -> Dict:
    """Preprocess entire document using global preprocessor."""
    return preprocessor.preprocess_document(text)
