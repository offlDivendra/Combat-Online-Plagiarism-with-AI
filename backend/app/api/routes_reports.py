"""
Report Routes
API endpoints for report generation and management.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.models.database import get_db, AnalysisHistory, ReportGeneration
from app.models.schemas import ReportGenerationRequest, ReportGenerationResponse
from app.services.report_generator import report_generator
from app.utils.helpers import get_timestamp


router = APIRouter()


@router.post("/reports/generate", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a plagiarism detection report for an analysis.
    
    Args:
        request: Report generation request
        db: Database session
        
    Returns:
        Report generation details
    """
    try:
        # Get analysis from database
        analysis = db.query(AnalysisHistory)\
            .filter(AnalysisHistory.id == request.analysis_id)\
            .first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Prepare analysis data for report
        analysis_data = analysis.to_detailed_dict()
        
        # Generate report
        report_path = report_generator.generate_report(
            analysis_data=analysis_data,
            report_format=request.report_format
        )
        
        # Get report filename and size
        report_filename = os.path.basename(report_path)
        report_size = os.path.getsize(report_path)
        
        # Save report record to database
        report_record = ReportGeneration(
            analysis_id=request.analysis_id,
            report_filename=report_filename,
            report_path=report_path,
            report_format=request.report_format,
            file_size=report_size
        )
        
        db.add(report_record)
        db.commit()
        db.refresh(report_record)
        
        return ReportGenerationResponse(
            id=report_record.id,
            analysis_id=report_record.analysis_id,
            report_filename=report_record.report_filename,
            generation_date=report_record.generation_date,
            report_format=report_record.report_format,
            file_size=report_record.file_size,
            download_url=f"/api/reports/download/{report_record.id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/reports/download/{report_id}")
async def download_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Download a generated report.
    
    Args:
        report_id: ID of the report
        db: Database session
        
    Returns:
        Report file
    """
    try:
        # Get report from database
        report = db.query(ReportGeneration)\
            .filter(ReportGeneration.id == report_id)\
            .first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Check if file exists
        if not os.path.exists(report.report_path):
            raise HTTPException(status_code=404, detail="Report file not found on disk")
        
        # Determine media type
        media_type = "application/pdf" if report.report_format == "pdf" else "application/json"
        
        # Return file
        return FileResponse(
            path=report.report_path,
            filename=report.report_filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/reports/analysis/{analysis_id}")
async def get_reports_for_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all reports generated for a specific analysis.
    
    Args:
        analysis_id: ID of the analysis
        db: Database session
        
    Returns:
        List of reports
    """
    try:
        # Check if analysis exists
        analysis = db.query(AnalysisHistory)\
            .filter(AnalysisHistory.id == analysis_id)\
            .first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get reports for this analysis
        reports = db.query(ReportGeneration)\
            .filter(ReportGeneration.analysis_id == analysis_id)\
            .order_by(ReportGeneration.generation_date.desc())\
            .all()
        
        report_list = [
            {
                **report.to_dict(),
                "download_url": f"/api/reports/download/{report.id}"
            }
            for report in reports
        ]
        
        return {
            "analysis_id": analysis_id,
            "reports": report_list,
            "count": len(report_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")


@router.get("/reports")
async def get_all_reports(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get all generated reports with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of reports
    """
    try:
        # Get total count
        total_count = db.query(ReportGeneration).count()
        
        # Get paginated results
        reports = db.query(ReportGeneration)\
            .order_by(ReportGeneration.generation_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        report_list = [
            {
                **report.to_dict(),
                "download_url": f"/api/reports/download/{report.id}"
            }
            for report in reports
        ]
        
        return {
            "reports": report_list,
            "total_count": total_count,
            "page": skip // limit + 1 if limit > 0 else 1,
            "page_size": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a report.
    
    Args:
        report_id: ID of the report to delete
        db: Database session
        
    Returns:
        Success message
    """
    try:
        report = db.query(ReportGeneration)\
            .filter(ReportGeneration.id == report_id)\
            .first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Delete file from disk if it exists
        if os.path.exists(report.report_path):
            try:
                os.remove(report.report_path)
            except Exception as e:
                print(f"Warning: Could not delete report file: {e}")
        
        # Delete from database
        db.delete(report)
        db.commit()
        
        return {
            "message": "Report deleted successfully",
            "id": report_id,
            "filename": report.report_filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")


@router.post("/reports/generate-quick")
async def generate_quick_report(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate and immediately download a report (one-step operation).
    
    Args:
        analysis_id: ID of the analysis
        db: Database session
        
    Returns:
        Report file for download
    """
    try:
        # Generate the report
        request = ReportGenerationRequest(
            analysis_id=analysis_id,
            report_format="pdf"
        )
        
        report_response = await generate_report(request, db)
        
        # Immediately return the file
        return await download_report(report_response.id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick report generation failed: {str(e)}")
