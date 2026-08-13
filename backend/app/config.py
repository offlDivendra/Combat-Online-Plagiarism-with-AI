"""
Configuration module for the plagiarism detection system.
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Settings
    APP_NAME: str = "AI Plagiarism Detector"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./plagiarism_detector.db"
    
    # File Upload Settings
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".pdf", ".docx"]
    
    # Similarity Algorithm Weights (must sum to 1.0)
    TFIDF_WEIGHT: float = 0.50
    NGRAM_WEIGHT: float = 0.20
    FUZZY_WEIGHT: float = 0.30
    
    # Classification Thresholds (percentages)
    THRESHOLD_LOW: float = 20.0
    THRESHOLD_MODERATE: float = 40.0
    THRESHOLD_HIGH: float = 60.0
    THRESHOLD_PLAGIARISM: float = 80.0
    
    # NLP Settings
    MIN_SENTENCE_LENGTH: int = 10
    FUZZY_MATCH_THRESHOLD: float = 82.0
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def validate_weights(self) -> bool:
        """Validate that similarity weights sum to 1.0."""
        total = self.TFIDF_WEIGHT + self.NGRAM_WEIGHT + self.FUZZY_WEIGHT
        return abs(total - 1.0) < 0.001
    
    def get_classification(self, similarity: float) -> str:
        """
        Classify similarity score into categories.
        
        Args:
            similarity: Similarity score (0-100)
            
        Returns:
            Classification category as string
        """
        if similarity >= self.THRESHOLD_PLAGIARISM:
            return "Potential Plagiarism"
        elif similarity >= self.THRESHOLD_HIGH:
            return "High Similarity"
        elif similarity >= self.THRESHOLD_MODERATE:
            return "Moderate Similarity"
        elif similarity >= self.THRESHOLD_LOW:
            return "Low Similarity"
        else:
            return "Mostly Original"


# Global settings instance
settings = Settings()

# Validate weights on startup
if not settings.validate_weights():
    raise ValueError(
        f"Similarity weights must sum to 1.0. "
        f"Current: {settings.TFIDF_WEIGHT + settings.NGRAM_WEIGHT + settings.FUZZY_WEIGHT}"
    )
