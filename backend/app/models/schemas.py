"""
Pydantic Schemas
Data validation and serialization schemas for API requests and responses.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


# ============================================================================
# Request Schemas
# ============================================================================

class TextAnalysisRequest(BaseModel):
    """Request schema for text-based plagiarism analysis."""
    
    text: str = Field(..., min_length=10, description="Text to analyze for plagiarism")
    document_name: Optional[str] = Field(None, description="Optional document name")
    
    @validator('text')
    def validate_text(cls, v):
        """Validate text is not empty after stripping."""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Machine learning is a branch of artificial intelligence...",
                "document_name": "student_assignment.txt"
            }
        }


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""
    
    filename: str
    file_size: int
    text_extracted: bool
    word_count: int
    message: str


# ============================================================================
# Reference Document Schemas
# ============================================================================

class ReferenceDocumentCreate(BaseModel):
    """Schema for creating a reference document."""
    
    filename: str
    original_filename: str
    file_extension: str
    file_size: int
    text_content: str
    word_count: int
    sentence_count: int
    file_path: Optional[str] = None


class ReferenceDocumentResponse(BaseModel):
    """Response schema for reference document."""
    
    id: int
    filename: str
    original_filename: str
    file_extension: str
    file_size: int
    word_count: int
    sentence_count: int
    upload_date: datetime
    text_preview: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReferenceDocumentList(BaseModel):
    """Response schema for list of reference documents."""
    
    documents: List[ReferenceDocumentResponse]
    total_count: int


# ============================================================================
# Analysis Result Schemas
# ============================================================================

class SimilarityScores(BaseModel):
    """Schema for individual similarity scores."""
    
    tfidf: float = Field(..., ge=0, le=100, description="TF-IDF similarity score")
    ngram: float = Field(..., ge=0, le=100, description="N-gram similarity score")
    fuzzy: float = Field(..., ge=0, le=100, description="Fuzzy matching score")


class AlgorithmWeights(BaseModel):
    """Schema for algorithm weights."""
    
    tfidf_weight: float
    ngram_weight: float
    fuzzy_weight: float


class SourceMatch(BaseModel):
    """Schema for a source document match."""
    
    name: str
    similarity: float
    tfidf_score: float
    ngram_score: float
    fuzzy_score: float
    matched_sentences: int


class SentenceMatch(BaseModel):
    """Schema for a sentence-level match."""
    
    submitted_sentence: str
    matched_sentence: str
    similarity: float
    source: str
    query_index: int
    reference_index: int
    method: str


class PlagiarismAnalysisResult(BaseModel):
    """Complete plagiarism analysis result schema."""
    
    analysis_id: Optional[int] = None
    document_name: str
    analysis_date: str
    word_count: int
    sentence_count: int
    overall_similarity: float = Field(..., ge=0, le=100)
    average_similarity: float = Field(..., ge=0, le=100)
    classification: str
    scores: SimilarityScores
    weights: AlgorithmWeights
    sources: List[SourceMatch]
    sentence_matches: List[SentenceMatch]
    total_matches: int
    high_similarity_matches: int
    
    class Config:
        schema_extra = {
            "example": {
                "document_name": "student_paper.txt",
                "analysis_date": "2024-08-13T10:30:00",
                "word_count": 850,
                "sentence_count": 42,
                "overall_similarity": 72.4,
                "average_similarity": 65.2,
                "classification": "High Similarity",
                "scores": {
                    "tfidf": 68.2,
                    "ngram": 74.1,
                    "fuzzy": 77.5
                },
                "weights": {
                    "tfidf_weight": 0.5,
                    "ngram_weight": 0.2,
                    "fuzzy_weight": 0.3
                },
                "sources": [],
                "sentence_matches": [],
                "total_matches": 15,
                "high_similarity_matches": 8
            }
        }


class QuickAnalysisResult(BaseModel):
    """Quick analysis result schema."""
    
    similarity: float
    classification: str
    scores: SimilarityScores
    matched_sentences: int


# ============================================================================
# Analysis History Schemas
# ============================================================================

class AnalysisHistoryCreate(BaseModel):
    """Schema for creating analysis history record."""
    
    document_name: str
    word_count: int
    sentence_count: int
    overall_similarity: float
    average_similarity: float
    tfidf_score: float
    ngram_score: float
    fuzzy_score: float
    classification: str
    total_references: int
    total_matches: int
    high_similarity_matches: int
    sources: Optional[List[Dict]] = None
    sentence_matches: Optional[List[Dict]] = None
    submitted_text: Optional[str] = None


class AnalysisHistoryResponse(BaseModel):
    """Response schema for analysis history."""
    
    id: int
    document_name: str
    analysis_date: datetime
    word_count: int
    sentence_count: int
    overall_similarity: float
    average_similarity: float
    classification: str
    scores: SimilarityScores
    total_references: int
    total_matches: int
    high_similarity_matches: int
    
    class Config:
        from_attributes = True


class AnalysisHistoryDetail(AnalysisHistoryResponse):
    """Detailed analysis history with sources and matches."""
    
    sources: Optional[List[Dict]] = None
    sentence_matches: Optional[List[Dict]] = None
    submitted_text: Optional[str] = None


class AnalysisHistoryList(BaseModel):
    """Response schema for list of analysis history."""
    
    analyses: List[AnalysisHistoryResponse]
    total_count: int
    page: int
    page_size: int


# ============================================================================
# Report Schemas
# ============================================================================

class ReportGenerationRequest(BaseModel):
    """Request schema for report generation."""
    
    analysis_id: int = Field(..., description="ID of the analysis to generate report for")
    report_format: str = Field(default="pdf", description="Report format (pdf, json)")
    
    @validator('report_format')
    def validate_format(cls, v):
        """Validate report format."""
        allowed_formats = ['pdf', 'json']
        if v.lower() not in allowed_formats:
            raise ValueError(f"Report format must be one of: {', '.join(allowed_formats)}")
        return v.lower()


class ReportGenerationResponse(BaseModel):
    """Response schema for report generation."""
    
    id: int
    analysis_id: int
    report_filename: str
    generation_date: datetime
    report_format: str
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    error: str
    detail: Optional[str] = None
    status_code: int


class ValidationErrorDetail(BaseModel):
    """Validation error detail schema."""
    
    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""
    
    error: str = "Validation Error"
    details: List[ValidationErrorDetail]


# ============================================================================
# Statistics Schemas
# ============================================================================

class SystemStatistics(BaseModel):
    """System statistics schema."""
    
    total_analyses: int
    total_reference_documents: int
    total_reports_generated: int
    average_similarity: float
    most_common_classification: str


class AnalysisSummary(BaseModel):
    """Summary statistics for analyses."""
    
    total: int
    by_classification: Dict[str, int]
    average_similarity: float
    max_similarity: float
    min_similarity: float
