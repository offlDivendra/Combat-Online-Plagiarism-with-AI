import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getAnalysisHistory, deleteAnalysis } from '../services/api';
import './History.css';

function History() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 10;
  
  useEffect(() => {
    loadHistory();
  }, [page]);
  
  const loadHistory = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * pageSize;
      const data = await getAnalysisHistory(skip, pageSize);
      setAnalyses(data.analyses || []);
      setTotalCount(data.total_count || 0);
      setError(null);
    } catch (err) {
      setError('Failed to load analysis history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this analysis?')) {
      return;
    }
    
    try {
      await deleteAnalysis(id);
      loadHistory(); // Reload after deletion
    } catch (err) {
      alert('Failed to delete analysis');
      console.error(err);
    }
  };
  
  const getSimilarityColor = (similarity) => {
    if (similarity >= 80) return '#dc2626';
    if (similarity >= 60) return '#ea580c';
    if (similarity >= 40) return '#f59e0b';
    if (similarity >= 20) return '#84cc16';
    return '#22c55e';
  };
  
  const totalPages = Math.ceil(totalCount / pageSize);
  
  return (
    <div className="history-page">
      <div className="history-header">
        <h1>Analysis History</h1>
        <Link to="/analyze" className="btn btn-primary">
          New Analysis
        </Link>
      </div>
      
      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}
      
      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner-large"></div>
          <p>Loading history...</p>
        </div>
      ) : analyses.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h2>No Analysis History</h2>
          <p>You haven't analyzed any documents yet. Start your first analysis!</p>
          <Link to="/analyze" className="btn btn-primary">
            Analyze Document
          </Link>
        </div>
      ) : (
        <>
          <div className="history-list">
            {analyses.map((analysis) => (
              <div key={analysis.id} className="history-item card">
                <div className="history-main">
                  <div className="history-info">
                    <h3 className="history-title">{analysis.document_name}</h3>
                    <div className="history-meta">
                      <span>📅 {new Date(analysis.analysis_date).toLocaleDateString()}</span>
                      <span>📝 {analysis.word_count} words</span>
                      <span>📄 {analysis.sentence_count} sentences</span>
                    </div>
                  </div>
                  
                  <div className="history-similarity">
                    <div 
                      className="similarity-value"
                      style={{ color: getSimilarityColor(analysis.overall_similarity) }}
                    >
                      {analysis.overall_similarity?.toFixed(1)}%
                    </div>
                    <div 
                      className="similarity-badge"
                      style={{ 
                        backgroundColor: getSimilarityColor(analysis.overall_similarity),
                        opacity: 0.2,
                        color: getSimilarityColor(analysis.overall_similarity)
                      }}
                    >
                      {analysis.classification}
                    </div>
                  </div>
                </div>
                
                <div className="history-actions">
                  <Link 
                    to={`/results/${analysis.id}`}
                    className="btn btn-secondary btn-sm"
                  >
                    View Details
                  </Link>
                  <button
                    onClick={() => handleDelete(analysis.id)}
                    className="btn btn-danger btn-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-secondary"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                ← Previous
              </button>
              <span className="page-info">
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-secondary"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default History;
