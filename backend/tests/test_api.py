"""
Unit tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base, get_db


# Create test database
TEST_DATABASE_URL = "sqlite:///./test_plagiarism.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health check returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestDocumentEndpoints:
    """Test document management endpoints."""
    
    def test_get_documents_empty(self):
        """Test getting documents when none exist."""
        response = client.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total_count" in data
    
    def test_upload_document_invalid_type(self):
        """Test upload with invalid file type."""
        # Create a fake file with invalid extension
        files = {"file": ("test.xyz", b"content", "application/octet-stream")}
        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 400
    
    def test_get_document_not_found(self):
        """Test getting non-existent document."""
        response = client.get("/api/documents/99999")
        assert response.status_code == 404
    
    def test_delete_document_not_found(self):
        """Test deleting non-existent document."""
        response = client.delete("/api/documents/99999")
        assert response.status_code == 404
    
    def test_search_documents(self):
        """Test document search."""
        response = client.get("/api/documents/search/test")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data
    
    def test_document_statistics(self):
        """Test document statistics endpoint."""
        response = client.get("/api/documents/statistics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "total_words" in data


class TestAnalysisEndpoints:
    """Test plagiarism analysis endpoints."""
    
    def test_analyze_text_no_references(self):
        """Test analysis fails when no reference documents exist."""
        payload = {
            "text": "This is a test document with enough words to pass validation check here.",
            "document_name": "test.txt"
        }
        response = client.post("/api/analyze", json=payload)
        # Should fail because no reference documents exist
        assert response.status_code == 400
    
    def test_analyze_text_too_short(self):
        """Test analysis fails with text too short."""
        payload = {
            "text": "Short",
            "document_name": "test.txt"
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 400
    
    def test_analyze_text_empty(self):
        """Test analysis fails with empty text."""
        payload = {
            "text": "",
            "document_name": "test.txt"
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_get_analysis_history(self):
        """Test getting analysis history."""
        response = client.get("/api/analyze/history")
        assert response.status_code == 200
        data = response.json()
        assert "analyses" in data
        assert "total_count" in data
        assert "page" in data
    
    def test_get_analysis_history_pagination(self):
        """Test analysis history pagination."""
        response = client.get("/api/analyze/history?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 10
    
    def test_get_analysis_detail_not_found(self):
        """Test getting non-existent analysis."""
        response = client.get("/api/analyze/history/99999")
        assert response.status_code == 404
    
    def test_delete_analysis_not_found(self):
        """Test deleting non-existent analysis."""
        response = client.delete("/api/analyze/history/99999")
        assert response.status_code == 404
    
    def test_get_statistics(self):
        """Test getting system statistics."""
        response = client.get("/api/analyze/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_analyses" in data
        assert "total_reference_documents" in data
        assert "average_similarity" in data


class TestReportEndpoints:
    """Test report generation endpoints."""
    
    def test_generate_report_analysis_not_found(self):
        """Test report generation for non-existent analysis."""
        payload = {
            "analysis_id": 99999,
            "report_format": "pdf"
        }
        response = client.post("/api/reports/generate", json=payload)
        assert response.status_code == 404
    
    def test_generate_report_invalid_format(self):
        """Test report generation with invalid format."""
        payload = {
            "analysis_id": 1,
            "report_format": "invalid"
        }
        response = client.post("/api/reports/generate", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_download_report_not_found(self):
        """Test downloading non-existent report."""
        response = client.get("/api/reports/download/99999")
        assert response.status_code == 404
    
    def test_get_reports_for_analysis_not_found(self):
        """Test getting reports for non-existent analysis."""
        response = client.get("/api/reports/analysis/99999")
        assert response.status_code == 404
    
    def test_get_all_reports(self):
        """Test getting all reports."""
        response = client.get("/api/reports")
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        assert "total_count" in data
    
    def test_delete_report_not_found(self):
        """Test deleting non-existent report."""
        response = client.delete("/api/reports/99999")
        assert response.status_code == 404


# Cleanup test database after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    """Cleanup test database after tests."""
    yield
    # Close all connections
    engine.dispose()
    # Remove test database file
    import os
    if os.path.exists("./test_plagiarism.db"):
        os.remove("./test_plagiarism.db")
