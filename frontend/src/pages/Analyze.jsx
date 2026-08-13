import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeText, analyzeFile } from '../services/api';
import './Analyze.css';

function Analyze() {
  const [mode, setMode] = useState('text'); // 'text' or 'file'
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [documentName, setDocumentName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();
  
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const ext = selectedFile.name.split('.').pop().toLowerCase();
      if (['txt', 'pdf', 'docx'].includes(ext)) {
        setFile(selectedFile);
        setDocumentName(selectedFile.name);
        setError(null);
      } else {
        setError('Please select a TXT, PDF, or DOCX file');
        setFile(null);
      }
    }
  };
  
  const handleAnalyze = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      let result;
      
      if (mode === 'text') {
        if (!text.trim()) {
          throw new Error('Please enter some text to analyze');
        }
        if (text.length < 50) {
          throw new Error('Text must be at least 50 characters long');
        }
        result = await analyzeText(text, documentName || 'Submitted Text');
      } else {
        if (!file) {
          throw new Error('Please select a file to analyze');
        }
        result = await analyzeFile(file);
      }
      
      // Navigate to results page
      if (result.analysis_id) {
        navigate(`/results/${result.analysis_id}`);
      } else {
        // Pass result directly via navigation state as fallback
        navigate('/results/0', { state: { result } });
      }
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err.response?.data?.detail || err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="analyze-page">
      <div className="analyze-header">
        <h1>Analyze Document for Plagiarism</h1>
        <p>Upload a document or paste text to check for potential plagiarism</p>
      </div>
      
      <div className="card">
        <div className="mode-selector">
          <button
            className={`mode-btn ${mode === 'text' ? 'active' : ''}`}
            onClick={() => setMode('text')}
          >
            📝 Paste Text
          </button>
          <button
            className={`mode-btn ${mode === 'file' ? 'active' : ''}`}
            onClick={() => setMode('file')}
          >
            📁 Upload File
          </button>
        </div>
        
        <form onSubmit={handleAnalyze} className="analyze-form">
          {error && (
            <div className="alert alert-error">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}
          
          {mode === 'text' ? (
            <>
              <div className="form-group">
                <label className="form-label">
                  Document Name (Optional)
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., My Essay"
                  value={documentName}
                  onChange={(e) => setDocumentName(e.target.value)}
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">
                  Text to Analyze *
                  <span className="text-hint">
                    (Minimum 50 characters)
                  </span>
                </label>
                <textarea
                  className="form-textarea"
                  placeholder="Paste your text here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={12}
                  required
                />
                <div className="char-count">
                  {text.length} characters
                </div>
              </div>
            </>
          ) : (
            <div className="form-group">
              <label className="form-label">
                Select File *
                <span className="text-hint">
                  (TXT, PDF, or DOCX, max 10MB)
                </span>
              </label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="file-input"
                  className="file-input"
                  accept=".txt,.pdf,.docx"
                  onChange={handleFileChange}
                  required
                />
                <label htmlFor="file-input" className="file-input-label">
                  {file ? (
                    <>
                      <span>📄</span>
                      <span>{file.name}</span>
                    </>
                  ) : (
                    <>
                      <span>📁</span>
                      <span>Choose File</span>
                    </>
                  )}
                </label>
              </div>
            </div>
          )}
          
          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loading-spinner"></span>
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <span>🔍</span>
                  <span>Analyze for Plagiarism</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
      
      <div className="info-section">
        <h3>ℹ️ Important Information</h3>
        <ul>
          <li>The system analyzes your document against reference documents in the database</li>
          <li>Results show similarity scores using TF-IDF, N-grams, and Fuzzy Matching</li>
          <li>Similarity does not automatically mean plagiarism - human review is required</li>
          <li>Common phrases and domain-specific terminology may create false positives</li>
          <li>Analysis typically takes 5-15 seconds depending on document length</li>
        </ul>
      </div>
    </div>
  );
}

export default Analyze;
