# Combat Online Plagiarism with AI

🔍 **AI-Powered Plagiarism Detection System** using NLP and Machine Learning

A complete plagiarism detection system that combines TF-IDF, N-Grams, and Fuzzy Matching algorithms to identify similar and potentially duplicated content. Built as a BTech CSE project demonstrating advanced NLP techniques and full-stack development.

---

## 🎯 Project Overview

This system analyzes submitted documents against a database of reference documents using multiple NLP techniques to detect textual similarity. It provides detailed analysis reports with similarity scores, matched sentences, and source identification.

### Key Features

- **Multi-Algorithm Detection**: Combines TF-IDF, N-gram analysis, and Fuzzy Matching
- **Configurable Weights**: Adjustable algorithm weights for customized detection
- **Sentence-Level Matching**: Identifies specific similar sentences with source attribution
- **Multiple File Formats**: Supports TXT, PDF, and DOCX files
- **Professional Reports**: Generates downloadable PDF reports with detailed analysis
- **User-Friendly Interface**: Modern React-based web interface
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints
- **Analysis History**: Track and review past analyses
- **Reference Management**: Upload and manage reference documents

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │◄────►│   FastAPI    │◄────►│   SQLite    │
│  Frontend   │      │   Backend    │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                    ┌───────┴───────┐
                    │   NLP Engine  │
                    ├───────────────┤
                    │  • TF-IDF     │
                    │  • N-Grams    │
                    │  • Fuzzy      │
                    └───────────────┘
```

---

## 🧪 NLP Pipeline

### 1. Text Preprocessing
- Normalization (lowercase, whitespace handling)
- Tokenization using NLTK
- Stopword removal
- Sentence segmentation

### 2. TF-IDF Analysis
- Term Frequency-Inverse Document Frequency vectorization
- Cosine similarity calculation
- Unigram and bigram features

### 3. N-Gram Similarity
- Word-level n-grams (unigrams, bigrams, trigrams)
- Jaccard similarity coefficient
- Dice coefficient
- Phrase pattern matching

### 4. Fuzzy Matching
- RapidFuzz algorithms (multiple ratio methods)
- Paraphrase detection
- Levenshtein distance
- Token-based matching

### 5. Combined Scoring
```
Final Score = (0.5 × TF-IDF) + (0.2 × N-Grams) + (0.3 × Fuzzy)
```

### 6. Classification
- **0-20%**: Mostly Original
- **20-40%**: Low Similarity
- **40-60%**: Moderate Similarity
- **60-80%**: High Similarity
- **80-100%**: Potential Plagiarism

---

## 📁 Project Structure

```
Combat/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── models/            # Database models & schemas
│   │   ├── services/          # NLP services
│   │   │   ├── preprocessing.py
│   │   │   ├── tfidf_similarity.py
│   │   │   ├── ngram_similarity.py
│   │   │   ├── fuzzy_matching.py
│   │   │   ├── plagiarism_engine.py
│   │   │   └── report_generator.py
│   │   ├── utils/             # Utilities
│   │   ├── config.py          # Configuration
│   │   └── main.py            # FastAPI app
│   ├── datasets/              # Sample documents
│   ├── tests/                 # Unit tests
│   └── requirements.txt
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API service layer
│   │   └── App.jsx
│   └── package.json
│
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 16+** (for frontend)
- **pip** (Python package manager)
- **npm** (Node package manager)

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
```

3. **Activate virtual environment**:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Download NLTK data** (first time only):
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

6. **Copy environment file**:
```bash
copy .env.example .env
```

7. **Run the backend**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/api/docs`

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start development server**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## 📊 Usage Guide

### 1. Upload Reference Documents

First, upload reference documents that will be used for comparison:

1. Go to **Documents** page
2. Click **Choose File to Upload**
3. Select TXT, PDF, or DOCX files
4. Documents are automatically processed and stored

**Sample documents** are provided in `backend/datasets/sample_documents/`

### 2. Analyze a Document

Two methods to analyze documents:

**Method A: Paste Text**
1. Go to **Analyze** page
2. Select "Paste Text" tab
3. Enter or paste your text (minimum 50 characters)
4. Optional: Enter document name
5. Click "Analyze for Plagiarism"

**Method B: Upload File**
1. Go to **Analyze** page
2. Select "Upload File" tab
3. Choose TXT, PDF, or DOCX file
4. Click "Analyze for Plagiarism"

### 3. View Results

The results page displays:

- **Overall Similarity Score**: Weighted combination of all algorithms
- **Classification**: Category based on similarity level
- **Component Scores**: Individual TF-IDF, N-gram, and Fuzzy scores
- **Matching Sources**: Reference documents with similar content
- **Match Statistics**: Total matches and high-similarity count
- **Download Report**: Generate PDF report

### 4. Review History

Access **History** page to:
- View all past analyses
- See similarity scores and classifications
- Navigate to detailed results
- Delete old analyses

---

## 🧪 Testing

### Run Unit Tests

```bash
cd backend
pytest -v
```

### Test Coverage

- **36 tests** for preprocessing service
- **40+ tests** for similarity services
- **25+ tests** for API endpoints

### Test Sample Documents

Use the provided test documents in `backend/datasets/test_documents/`:

- `high_similarity_text.txt` - Expected: 75-90% similarity
- `moderate_similarity_text.txt` - Expected: 40-60% similarity
- `low_similarity_text.txt` - Expected: <20% similarity

---

## ⚙️ Configuration

Edit `backend/.env` to customize:

```env
# Similarity Weights (must sum to 1.0)
TFIDF_WEIGHT=0.50
NGRAM_WEIGHT=0.20
FUZZY_WEIGHT=0.30

# Classification Thresholds (percentages)
THRESHOLD_LOW=20.0
THRESHOLD_MODERATE=40.0
THRESHOLD_HIGH=60.0
THRESHOLD_PLAGIARISM=80.0

# File Upload Settings
MAX_UPLOAD_SIZE_MB=10
ALLOWED_EXTENSIONS=.txt,.pdf,.docx
```

---

## 📈 Demo Scenario

### Step-by-Step Demonstration

1. **Setup**:
   - Upload all 5 sample reference documents from `backend/datasets/sample_documents/`
   - Verify documents appear in Documents page

2. **Test High Similarity**:
   - Analyze `high_similarity_text.txt`
   - Expected result: 75-90% similarity, "High Similarity" or "Potential Plagiarism"
   - View matching sentences from AI/ML reference document

3. **Test Moderate Similarity**:
   - Analyze `moderate_similarity_text.txt`
   - Expected result: 40-60% similarity, "Moderate Similarity"
   - Paraphrased content should be detected

4. **Test Original Content**:
   - Analyze `low_similarity_text.txt`
   - Expected result: <20% similarity, "Mostly Original"
   - Different topic should show minimal matches

5. **Generate Report**:
   - Click "Download Report" on results page
   - Review PDF with complete analysis

---

## 🎓 Educational Value

### Concepts Demonstrated

1. **Natural Language Processing**
   - Text preprocessing and normalization
   - Tokenization and stemming
   - Statistical text analysis

2. **Machine Learning**
   - Feature extraction (TF-IDF)
   - Similarity metrics
   - Classification algorithms

3. **Software Engineering**
   - RESTful API design
   - Database modeling
   - Full-stack development
   - Testing and validation

4. **User Experience**
   - Responsive web design
   - Intuitive navigation
   - Real-time feedback

### Technologies Used

**Backend:**
- FastAPI
- scikit-learn
- NLTK
- spaCy
- RapidFuzz
- SQLAlchemy
- ReportLab

**Frontend:**
- React 18
- React Router
- Axios
- Vite

**Database:**
- SQLite

---

## ⚠️ Important Disclaimer

This system detects **textual similarity** and should be used as an **assistance tool** only.

- Similarity does NOT automatically prove plagiarism
- Common phrases may create false positives
- Paraphrasing may reduce similarity scores
- **Human review is required** for final decisions
- Use responsibly for educational purposes

---

## 📝 Viva Questions & Answers

### 1. How does TF-IDF work?

TF-IDF (Term Frequency-Inverse Document Frequency) identifies important words by considering how frequently they appear in a document (TF) versus how rare they are across all documents (IDF). Words that are common in one document but rare overall get higher weights.

### 2. Why combine multiple algorithms?

Each algorithm has strengths and weaknesses:
- **TF-IDF**: Good for overall document similarity
- **N-Grams**: Detects phrase patterns and sequences
- **Fuzzy Matching**: Catches paraphrasing and slight modifications

Combining them provides more robust detection.

### 3. What is the difference between Jaccard and Cosine similarity?

- **Jaccard**: Measures overlap of unique n-grams (set-based)
- **Cosine**: Measures angle between feature vectors (considers frequency)

Cosine is generally better for text where word frequency matters.

### 4. How do you handle false positives?

- Use multiple algorithms with different strengths
- Provide detailed sentence-level matches for human review
- Include disclaimer that human judgment is required
- Show source attribution for verification

### 5. Can this system be improved?

Yes, potential improvements:
- Add semantic similarity using transformers (BERT, Sentence-BERT)
- Implement citation detection
- Add multilingual support
- Use deep learning for better paraphrase detection
- Implement real-time web search

---

## 📄 License

Educational project for BTech CSE demonstration purposes.

---

## 👨‍💻 Author

BTech CSE Project - AI-Powered Plagiarism Detection System

---

## 🤝 Acknowledgments

- NLTK Project for NLP tools
- scikit-learn for machine learning utilities
- RapidFuzz for fuzzy matching algorithms
- FastAPI for excellent backend framework
- React for frontend development

---

**Note**: This is a demonstration project for educational purposes. For production use, consider additional features like user authentication, rate limiting, and enhanced security measures.
