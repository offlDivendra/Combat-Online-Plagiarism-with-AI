import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getStatistics } from '../services/api';
import './Home.css';

function Home() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadStatistics();
  }, []);
  
  const loadStatistics = async () => {
    try {
      const data = await getStatistics();
      setStats(data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="home-page">
      <div className="hero-section">
        <h1 className="hero-title">Combat Online Plagiarism with AI</h1>
        <p className="hero-subtitle">
          Detect similar and duplicated content using advanced NLP and machine learning techniques
        </p>
        <Link to="/analyze" className="btn btn-primary btn-large">
          Start Analysis
        </Link>
      </div>
      
      <div className="features-section">
        <h2 className="section-title">How It Works</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <h3>TF-IDF Analysis</h3>
            <p>Identifies important terms and calculates document similarity using term frequency-inverse document frequency.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🔤</div>
            <h3>N-Gram Matching</h3>
            <p>Detects similar phrase patterns using unigram, bigram, and trigram analysis.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Fuzzy Matching</h3>
            <p>Catches paraphrased content with RapidFuzz algorithms for approximate string matching.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Combined Scoring</h3>
            <p>Weighted combination of multiple algorithms provides comprehensive similarity analysis.</p>
          </div>
        </div>
      </div>
      
      {!loading && stats && (
        <div className="stats-section">
          <h2 className="section-title">System Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats.total_analyses || 0}</div>
              <div className="stat-label">Total Analyses</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_reference_documents || 0}</div>
              <div className="stat-label">Reference Documents</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.average_similarity?.toFixed(1) || 0}%</div>
              <div className="stat-label">Average Similarity</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.most_common_classification || 'N/A'}</div>
              <div className="stat-label">Most Common Result</div>
            </div>
          </div>
        </div>
      )}
      
      <div className="cta-section">
        <h2>Ready to Check Your Document?</h2>
        <p>Upload your document or paste text to start plagiarism detection</p>
        <Link to="/analyze" className="btn btn-primary">
          Get Started
        </Link>
      </div>
    </div>
  );
}

export default Home;
