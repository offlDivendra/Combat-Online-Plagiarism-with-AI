import { useEffect, useState } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import { getAnalysisDetail, generateReport, downloadReport } from '../services/api';
import './Results.css';

function Results() {
  const { id } = useParams();
  const location = useLocation();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  
  useEffect(() => {
    // If result was passed directly via navigation state, use it
    if (location.state?.result) {
      setResult(location.state.result);
      setLoading(false);
    } else if (id && id !== '0') {
      loadAnalysisDetail();
    } else {
      setError('No analysis result found');
      setLoading(false);
    }
  }, [id]);
  
  const loadAnalysisDetail = async () => {
    try {
      const data = await getAnalysisDetail(id);
      setResult(data);
    } catch (err) {
      setError('Failed to load analysis results');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const getSimilarityColor = (similarity) => {
    if (similarity >= 80) return '#dc2626';
    if (similarity >= 60) return '#ea580c';
    if (similarity >= 40) return '#f59e0b';
    if (similarity >= 20) return '#84cc16';
    return '#22c55e';
  };
  
  const handleDownloadReport = async () => {
    const analysisId = result?.analysis_id || id;
    if (!analysisId || analysisId === '0') {
      alert('Report can only be generated for saved analyses. Please run the analysis again.');
      return;
    }
    try {
      setReportLoading(true);
      const reportData = await generateReport(analysisId, 'pdf');
      if (reportData?.id) {
        const url = downloadReport(reportData.id);
        window.open(url, '_blank');
      }
    } catch (err) {
      console.error('Report generation failed:', err);
      alert('Failed to generate report. Please try again.');
    } finally {
      setReportLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="results-page">
        <div className="loading-container">
          <div className="loading-spinner-large"></div>
          <p>Loading results...</p>
        </div>
      </div>
    );
  }
  
  if (error || !result) {
    return (
      <div className="results-page">
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error || 'Results not found'}</span>
        </div>
        <Link to="/analyze" className="btn btn-primary">
          New Analysis
        </Link>
      </div>
    );
  }
  
  return (
    <div className="results-page">
      <div className="results-header">
        <h1>Plagiarism Analysis Results</h1>
        <div className="header-actions">
          <button onClick={handleDownloadReport} className="btn btn-secondary" disabled={reportLoading}>
            {reportLoading ? '⏳ Generating...' : '📄 Download Report'}
          </button>
          <Link to="/analyze" className="btn btn-primary">
            New Analysis
          </Link>
        </div>
      </div>
      
      <div className="card">
        <h2>Document Information</h2>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Document:</span>
            <span className="info-value">{result.document_name}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Analysis Date:</span>
            <span className="info-value">{new Date(result.analysis_date).toLocaleString()}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Word Count:</span>
            <span className="info-value">{result.word_count}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Sentences:</span>
            <span className="info-value">{result.sentence_count}</span>
          </div>
        </div>
      </div>
      
      <div className="card similarity-card">
        <h2>Overall Similarity</h2>
        <div 
          className="similarity-score"
          style={{ color: getSimilarityColor(result.overall_similarity) }}
        >
          {result.overall_similarity?.toFixed(2)}%
        </div>
        <div 
          className="classification-badge"
          style={{ backgroundColor: getSimilarityColor(result.overall_similarity) }}
        >
          {result.classification}
        </div>
      </div>
      
      <div className="card">
        <h2>Component Scores</h2>
        <div className="scores-grid">
          <div className="score-item">
            <div className="score-label">TF-IDF</div>
            <div className="score-value">{result.scores?.tfidf?.toFixed(2)}%</div>
            <div className="score-weight">Weight: 50%</div>
          </div>
          <div className="score-item">
            <div className="score-label">N-Grams</div>
            <div className="score-value">{result.scores?.ngram?.toFixed(2)}%</div>
            <div className="score-weight">Weight: 20%</div>
          </div>
          <div className="score-item">
            <div className="score-label">Fuzzy Match</div>
            <div className="score-value">{result.scores?.fuzzy?.toFixed(2)}%</div>
            <div className="score-weight">Weight: 30%</div>
          </div>
        </div>
      </div>
      
      {result.sources && result.sources.length > 0 && (
        <div className="card">
          <h2>Matching Sources</h2>
          <div className="sources-list">
            {result.sources.slice(0, 5).map((source, index) => (
              <div key={index} className="source-item">
                <div className="source-info">
                  <div className="source-name">{source.name}</div>
                  <div className="source-matches">{source.matched_sentences} sentence(s) matched</div>
                </div>
                <div 
                  className="source-similarity"
                  style={{ color: getSimilarityColor(source.similarity) }}
                >
                  {source.similarity?.toFixed(2)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="card">
        <h2>Match Statistics</h2>
        <div className="stats-row">
          <div className="stat-box">
            <div className="stat-value">{result.total_matches}</div>
            <div className="stat-label">Total Matches</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{result.high_similarity_matches}</div>
            <div className="stat-label">High Similarity (≥80%)</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{result.total_references}</div>
            <div className="stat-label">References Analyzed</div>
          </div>
        </div>
      </div>
      
      <div className="disclaimer-section">
        <h3>⚠️ Important Disclaimer</h3>
        <p>
          This similarity score indicates textual overlap and should be reviewed by a human before
          concluding plagiarism. Common phrases and domain-specific terminology may create false positives.
          The system uses NLP techniques to detect potential similarities but does not prove plagiarism.
        </p>
      </div>
    </div>
  );
}

export default Results;
