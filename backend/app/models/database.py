"""
Database Models
SQLAlchemy models for storing documents, analysis results, and history.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class ReferenceDocument(Base):
    """Model for storing reference documents."""
    
    __tablename__ = "reference_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_extension = Column(String(10), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    text_content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    sentence_count = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_path = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<ReferenceDocument(id={self.id}, filename='{self.filename}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_extension": self.file_extension,
            "file_size": self.file_size,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "text_preview": self.text_content[:200] + "..." if len(self.text_content) > 200 else self.text_content
        }


class AnalysisHistory(Base):
    """Model for storing plagiarism analysis history."""
    
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(255), nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    word_count = Column(Integer, nullable=False)
    sentence_count = Column(Integer, nullable=False)
    
    # Similarity scores
    overall_similarity = Column(Float, nullable=False)
    average_similarity = Column(Float, nullable=False)
    tfidf_score = Column(Float, nullable=False)
    ngram_score = Column(Float, nullable=False)
    fuzzy_score = Column(Float, nullable=False)
    
    # Classification
    classification = Column(String(50), nullable=False)
    
    # Matching statistics
    total_references = Column(Integer, nullable=False)
    total_matches = Column(Integer, nullable=False)
    high_similarity_matches = Column(Integer, nullable=False)
    
    # Detailed results (stored as JSON)
    sources = Column(JSON, nullable=True)
    sentence_matches = Column(JSON, nullable=True)
    
    # Original text
    submitted_text = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AnalysisHistory(id={self.id}, document='{self.document_name}', similarity={self.overall_similarity}%)>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "document_name": self.document_name,
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "overall_similarity": self.overall_similarity,
            "average_similarity": self.average_similarity,
            "classification": self.classification,
            "scores": {
                "tfidf": self.tfidf_score,
                "ngram": self.ngram_score,
                "fuzzy": self.fuzzy_score
            },
            "total_references": self.total_references,
            "total_matches": self.total_matches,
            "high_similarity_matches": self.high_similarity_matches
        }
    
    def to_detailed_dict(self):
        """Convert model to detailed dictionary with all data."""
        base_dict = self.to_dict()
        base_dict.update({
            "sources": self.sources,
            "sentence_matches": self.sentence_matches,
            "submitted_text": self.submitted_text
        })
        return base_dict


class ReportGeneration(Base):
    """Model for storing generated reports."""
    
    __tablename__ = "report_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, nullable=False)  # Links to AnalysisHistory
    report_filename = Column(String(255), nullable=False)
    report_path = Column(String(500), nullable=False)
    generation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    report_format = Column(String(20), nullable=False)  # PDF, JSON, etc.
    file_size = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<ReportGeneration(id={self.id}, filename='{self.report_filename}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "report_filename": self.report_filename,
            "generation_date": self.generation_date.isoformat() if self.generation_date else None,
            "report_format": self.report_format,
            "file_size": self.file_size
        }


# Database session dependency
def get_db():
    """
    Database session dependency for FastAPI.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database initialization
def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)


def reset_db():
    """Reset database by dropping and recreating all tables."""
    drop_db()
    init_db()
