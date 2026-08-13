import { useEffect, useState } from 'react';
import { getDocuments, uploadDocument, deleteDocument, getDocumentStatistics } from '../services/api';
import './Documents.css';

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  useEffect(() => {
    loadDocuments();
    loadStatistics();
  }, []);
  
  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await getDocuments();
      setDocuments(data.documents || []);
      setError(null);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const loadStatistics = async () => {
    try {
      const data = await getDocumentStatistics();
      setStats(data);
    } catch (err) {
      console.error('Failed to load statistics:', err);
    }
  };
  
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['txt', 'pdf', 'docx'].includes(ext)) {
      setError('Please select a TXT, PDF, or DOCX file');
      return;
    }
    
    setUploading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await uploadDocument(file);
      setSuccess(`Successfully uploaded ${file.name}`);
      loadDocuments();
      loadStatistics();
      e.target.value = ''; // Reset file input
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };
  
  const handleDelete = async (id, filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }
    
    try {
      await deleteDocument(id);
      setSuccess(`Deleted ${filename}`);
      loadDocuments();
      loadStatistics();
    } catch (err) {
      setError('Failed to delete document');
      console.error(err);
    }
  };
  
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };
  
  return (
    <div className="documents-page">
      <div className="documents-header">
        <div>
          <h1>Reference Documents</h1>
          <p>Manage documents used for plagiarism comparison</p>
        </div>
      </div>
      
      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}
      
      {success && (
        <div className="alert alert-success">
          <span>✅</span>
          <span>{success}</span>
        </div>
      )}
      
      {stats && (
        <div className="stats-section">
          <div className="stat-card">
            <div className="stat-value">{stats.total_documents}</div>
            <div className="stat-label">Total Documents</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_words?.toLocaleString()}</div>
            <div className="stat-label">Total Words</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_size_mb?.toFixed(2)} MB</div>
            <div className="stat-label">Total Size</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.average_words_per_document?.toFixed(0)}</div>
            <div className="stat-label">Avg Words/Doc</div>
          </div>
        </div>
      )}
      
      <div className="card upload-section">
        <h2>Upload Reference Document</h2>
        <p className="upload-hint">Supported formats: TXT, PDF, DOCX (max 10MB)</p>
        
        <div className="file-upload-area">
          <input
            type="file"
            id="doc-upload"
            className="file-input"
            accept=".txt,.pdf,.docx"
            onChange={handleFileChange}
            disabled={uploading}
          />
          <label htmlFor="doc-upload" className="file-upload-label">
            {uploading ? (
              <>
                <span className="loading-spinner"></span>
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <span>📁</span>
                <span>Choose File to Upload</span>
              </>
            )}
          </label>
        </div>
      </div>
      
      <div className="card">
        <h2>Uploaded Documents ({documents.length})</h2>
        
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner-large"></div>
            <p>Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📚</div>
            <p>No reference documents uploaded yet</p>
            <p className="empty-hint">Upload documents to enable plagiarism detection</p>
          </div>
        ) : (
          <div className="documents-list">
            {documents.map((doc) => (
              <div key={doc.id} className="document-item">
                <div className="doc-icon">
                  {doc.file_extension === '.pdf' ? '📕' : 
                   doc.file_extension === '.docx' ? '📘' : '📄'}
                </div>
                <div className="doc-info">
                  <div className="doc-name">{doc.original_filename}</div>
                  <div className="doc-meta">
                    <span>{doc.word_count} words</span>
                    <span>{doc.sentence_count} sentences</span>
                    <span>{formatBytes(doc.file_size)}</span>
                    <span>{new Date(doc.upload_date).toLocaleDateString()}</span>
                  </div>
                </div>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => handleDelete(doc.id, doc.original_filename)}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Documents;
