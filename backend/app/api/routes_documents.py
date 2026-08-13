"""
Document Management Routes
API endpoints for managing reference documents.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os

from app.models.database import get_db, ReferenceDocument
from app.models.schemas import (
    ReferenceDocumentResponse, ReferenceDocumentList,
    DocumentUploadResponse, ErrorResponse
)
from app.services.preprocessing import preprocessor
from app.utils.text_extractor import text_extractor, is_supported_file
from app.utils.helpers import save_uploaded_file, delete_file_safe
from app.config import settings


router = APIRouter()


@router.get("/documents", response_model=ReferenceDocumentList)
async def get_reference_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all reference documents with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of reference documents
    """
    try:
        # Get total count
        total_count = db.query(ReferenceDocument).count()
        
        # Get paginated results
        documents = db.query(ReferenceDocument)\
            .order_by(ReferenceDocument.upload_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        # Convert to response format
        doc_list = [doc.to_dict() for doc in documents]
        
        return {
            "documents": doc_list,
            "total_count": total_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")


@router.get("/documents/{document_id}")
async def get_reference_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific reference document by ID.
    
    Args:
        document_id: ID of the document
        db: Database session
        
    Returns:
        Reference document details
    """
    try:
        document = db.query(ReferenceDocument)\
            .filter(ReferenceDocument.id == document_id)\
            .first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Return with full text
        doc_dict = document.to_dict()
        doc_dict["text_content"] = document.text_content
        
        return doc_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch document: {str(e)}")


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_reference_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a new reference document.
    
    Args:
        file: Uploaded file (TXT, PDF, or DOCX)
        db: Database session
        
    Returns:
        Upload confirmation with document details
    """
    try:
        # Validate file type
        if not is_supported_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Save file temporarily
        upload_dir = "./temp_uploads"
        file_path = save_uploaded_file(file_content, file.filename, upload_dir)
        
        try:
            # Extract text from file
            extracted_text, file_ext = text_extractor.extract_text(file_path)
            
            # Preprocess to get word and sentence count
            processed = preprocessor.preprocess_document(extracted_text)
            
            # Create database entry
            ref_document = ReferenceDocument(
                filename=file.filename,
                original_filename=file.filename,
                file_extension=file_ext,
                file_size=file_size,
                text_content=extracted_text,
                word_count=processed["word_count"],
                sentence_count=processed["sentence_count"]
            )
            
            db.add(ref_document)
            db.commit()
            db.refresh(ref_document)
            
            return DocumentUploadResponse(
                filename=file.filename,
                file_size=file_size,
                text_extracted=True,
                word_count=processed["word_count"],
                message=f"Reference document uploaded successfully with ID {ref_document.id}"
            )
            
        finally:
            # Clean up temporary file
            delete_file_safe(file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/documents/upload-multiple")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple reference documents at once.
    
    Args:
        files: List of uploaded files
        db: Database session
        
    Returns:
        Upload results for each file
    """
    results = []
    
    for file in files:
        try:
            result = await upload_reference_document(file, db)
            results.append({
                "filename": file.filename,
                "status": "success",
                "data": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "results": results,
        "total": len(files),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error")
    }


@router.delete("/documents/{document_id}")
async def delete_reference_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a reference document.
    
    Args:
        document_id: ID of the document to delete
        db: Database session
        
    Returns:
        Success message
    """
    try:
        document = db.query(ReferenceDocument)\
            .filter(ReferenceDocument.id == document_id)\
            .first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {
            "message": "Reference document deleted successfully",
            "id": document_id,
            "filename": document.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.delete("/documents")
async def delete_all_documents(db: Session = Depends(get_db)):
    """
    Delete all reference documents (use with caution).
    
    Args:
        db: Database session
        
    Returns:
        Success message with count
    """
    try:
        count = db.query(ReferenceDocument).count()
        
        if count == 0:
            return {"message": "No documents to delete", "deleted_count": 0}
        
        # Delete all documents
        db.query(ReferenceDocument).delete()
        db.commit()
        
        return {
            "message": f"All reference documents deleted successfully",
            "deleted_count": count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete documents: {str(e)}")


@router.get("/documents/search/{query}")
async def search_documents(
    query: str,
    db: Session = Depends(get_db)
):
    """
    Search reference documents by filename or content.
    
    Args:
        query: Search query
        db: Database session
        
    Returns:
        Matching documents
    """
    try:
        # Search in filename
        documents = db.query(ReferenceDocument)\
            .filter(ReferenceDocument.filename.contains(query))\
            .all()
        
        results = [doc.to_dict() for doc in documents]
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/documents/statistics/summary")
async def get_document_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about reference documents.
    
    Args:
        db: Database session
        
    Returns:
        Document statistics
    """
    try:
        documents = db.query(ReferenceDocument).all()
        
        if not documents:
            return {
                "total_documents": 0,
                "total_words": 0,
                "total_sentences": 0,
                "average_words_per_document": 0,
                "total_size_mb": 0
            }
        
        total_words = sum(doc.word_count for doc in documents)
        total_sentences = sum(doc.sentence_count for doc in documents)
        total_size = sum(doc.file_size for doc in documents)
        
        return {
            "total_documents": len(documents),
            "total_words": total_words,
            "total_sentences": total_sentences,
            "average_words_per_document": round(total_words / len(documents), 2),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_extension": {
                ".txt": sum(1 for d in documents if d.file_extension == ".txt"),
                ".pdf": sum(1 for d in documents if d.file_extension == ".pdf"),
                ".docx": sum(1 for d in documents if d.file_extension == ".docx")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")
