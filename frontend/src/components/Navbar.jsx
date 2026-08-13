import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };
  
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">🔍</span>
          <span className="logo-text">AI Plagiarism Detector</span>
        </Link>
        
        <ul className="navbar-menu">
          <li className="navbar-item">
            <Link to="/" className={`navbar-link ${isActive('/')}`}>
              Home
            </Link>
          </li>
          <li className="navbar-item">
            <Link to="/analyze" className={`navbar-link ${isActive('/analyze')}`}>
              Analyze
            </Link>
          </li>
          <li className="navbar-item">
            <Link to="/history" className={`navbar-link ${isActive('/history')}`}>
              History
            </Link>
          </li>
          <li className="navbar-item">
            <Link to="/documents" className={`navbar-link ${isActive('/documents')}`}>
              Documents
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
