"""
Analysis Routes
API endpoints for plagiarism analysis operations.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.models.database import get_db, AnalysisHistory, ReferenceDocument
from app.models.schemas import (
    TextAnalysisRequest, PlagiarismAnalysisResult,
    DocumentUploadResponse, ErrorResponse
)
from app.services.plagiarism_engine import plagiarism_engine
from app.services.preprocessing import preprocessor
from app.utils.text_extractor import text_extractor, is_supported_file
from app.utils.helpers import save_uploaded_file, delete_file_safe, validate_text_length
from app.config import settings


router = APIRouter()


@router.post("/analyze", response_model=PlagiarismAnalysisResult)
async def analyze_text(
    request: TextAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze text for plagiarism against reference documents.
    
    Args:
        request: Text analysis request with text and optional document name
        db: Database session
        
    Returns:
        Plagiarism analysis results
    """
    try:
        # Validate text length
        is_valid, error_msg = validate_text_length(request.text, min_length=50)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Get all reference documents from database
        reference_docs = db.query(ReferenceDocument).all()
        
        if not reference_docs:
            raise HTTPException(
                status_code=400,
                detail="No reference documents found. Please upload reference documents first."
            )
        
        # Extract text and names from reference documents
        reference_texts = [doc.text_content for doc in reference_docs]
        reference_names = [doc.filename for doc in reference_docs]
        
        # Perform plagiarism analysis
        analysis_result = plagiarism_engine.analyze_document(
            query_text=request.text,
            reference_texts=reference_texts,
            reference_names=reference_names
        )
        
        # Update document name if provided
        if request.document_name:
            analysis_result["document_name"] = request.document_name
        
        # Save analysis to database
        try:
            analysis_history = AnalysisHistory(
                document_name=analysis_result["document_name"],
                word_count=analysis_result["word_count"],
                sentence_count=analysis_result["sentence_count"],
                overall_similarity=analysis_result["overall_similarity"],
                average_similarity=analysis_result["average_similarity"],
                tfidf_score=analysis_result["scores"]["tfidf"],
                ngram_score=analysis_result["scores"]["ngram"],
                fuzzy_score=analysis_result["scores"]["fuzzy"],
                classification=analysis_result["classification"],
                total_references=len(reference_texts),
                total_matches=analysis_result["total_matches"],
                high_similarity_matches=analysis_result["high_similarity_matches"],
                sources=analysis_result["sources"],
                sentence_matches=analysis_result["sentence_matches"],
                submitted_text=request.text
            )
            
            db.add(analysis_history)
            db.commit()
            db.refresh(analysis_history)
            
            # Add analysis ID to result
            analysis_result["analysis_id"] = analysis_history.id
            
        except Exception as db_error:
            # Log but don't fail if database save fails
            print(f"Warning: Failed to save analysis to database: {db_error}")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/file", response_model=PlagiarismAnalysisResult)
async def analyze_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analyze uploaded file for plagiarism.
    
    Args:
        file: Uploaded file (TXT, PDF, or DOCX)
        db: Database session
        
    Returns:
        Plagiarism analysis results
    """
    try:
        # Validate file type
        if not is_supported_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Save uploaded file temporarily
        upload_dir = "./temp_uploads"
        file_content = await file.read()
        
        file_path = save_uploaded_file(file_content, file.filename, upload_dir)
        
        try:
            # Extract text from file
            extracted_text, file_ext = text_extractor.extract_text(file_path)
            
            # Create analysis request
            request = TextAnalysisRequest(
                text=extracted_text,
                document_name=file.filename
            )
            
            # Perform analysis
            result = await analyze_text(request, db)
            
            return result
            
        finally:
            # Clean up temporary file
            delete_file_safe(file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")


@router.get("/analyze/history")
async def get_analysis_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get analysis history with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of analysis history records
    """
    try:
        # Get total count
        total_count = db.query(AnalysisHistory).count()
        
        # Get paginated results (ordered by most recent)
        analyses = db.query(AnalysisHistory)\
            .order_by(AnalysisHistory.analysis_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        # Convert to dictionaries
        results = [analysis.to_dict() for analysis in analyses]
        
        return {
            "analyses": results,
            "total_count": total_count,
            "page": skip // limit + 1 if limit > 0 else 1,
            "page_size": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@router.get("/analyze/history/{analysis_id}")
async def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed analysis results by ID.
    
    Args:
        analysis_id: ID of the analysis
        db: Database session
        
    Returns:
        Detailed analysis results
    """
    try:
        analysis = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis.to_detailed_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analysis: {str(e)}")


@router.delete("/analyze/history/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an analysis record.
    
    Args:
        analysis_id: ID of the analysis to delete
        db: Database session
        
    Returns:
        Success message
    """
    try:
        analysis = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        db.delete(analysis)
        db.commit()
        
        return {"message": "Analysis deleted successfully", "id": analysis_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete analysis: {str(e)}")


@router.get("/analyze/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get system statistics.
    
    Args:
        db: Database session
        
    Returns:
        System statistics
    """
    try:
        # Total analyses
        total_analyses = db.query(AnalysisHistory).count()
        
        # Total reference documents
        total_references = db.query(ReferenceDocument).count()
        
        # Get all similarities for average
        all_analyses = db.query(AnalysisHistory).all()
        
        if all_analyses:
            avg_similarity = sum(a.overall_similarity for a in all_analyses) / len(all_analyses)
            
            # Count by classification
            classifications = {}
            for analysis in all_analyses:
                classification = analysis.classification
                classifications[classification] = classifications.get(classification, 0) + 1
            
            most_common = max(classifications.items(), key=lambda x: x[1])[0] if classifications else "N/A"
        else:
            avg_similarity = 0.0
            classifications = {}
            most_common = "N/A"
        
        return {
            "total_analyses": total_analyses,
            "total_reference_documents": total_references,
            "average_similarity": round(avg_similarity, 2),
            "most_common_classification": most_common,
            "by_classification": classifications
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")
