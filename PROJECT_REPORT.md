# COMBAT ONLINE PLAGIARISM WITH AI
## Full Project Report — Beginner Friendly Edition

**Project Title:** Combat Online Plagiarism with AI  
**Technology Stack:** Python (FastAPI) + React.js  
**Database:** SQLite  
**Author:** BTech CSE Student  
**Year:** 2026  

---

# TABLE OF CONTENTS

1. [What Is This Project?](#1-what-is-this-project)
2. [Why Did We Build This?](#2-why-did-we-build-this)
3. [What Does It Do?](#3-what-does-it-do)
4. [Technologies Used](#4-technologies-used)
5. [System Architecture](#5-system-architecture)
6. [How NLP Works in This Project](#6-how-nlp-works-in-this-project)
7. [Algorithm Deep Dive](#7-algorithm-deep-dive)
8. [Project Folder Structure](#8-project-folder-structure)
9. [Database Design](#9-database-design)
10. [API Endpoints](#10-api-endpoints)
11. [Frontend Pages](#11-frontend-pages)
12. [How to Run the Project](#12-how-to-run-the-project)
13. [Test Results & Evaluation](#13-test-results--evaluation)
14. [Limitations](#14-limitations)
15. [Future Improvements](#15-future-improvements)
16. [Viva Questions & Answers](#16-viva-questions--answers)
17. [Conclusion](#17-conclusion)

---

# 1. WHAT IS THIS PROJECT?

## Simple Explanation (For a Beginner)

Imagine a teacher receives 50 student assignments. She suspects some students copied from the internet or from each other. Checking each one manually takes hours. This project **automates that process using Artificial Intelligence**.

**"Combat Online Plagiarism with AI"** is a web application that:
- Takes any piece of text or document as input
- Compares it against a database of reference documents
- Tells you HOW SIMILAR it is (as a percentage)
- Shows you WHICH sentences were copied
- Generates a detailed PDF report

## What Is Plagiarism?

Plagiarism means **copying someone else's work and presenting it as your own**. This includes:
- Copying text word-for-word
- Paraphrasing (changing words slightly but keeping the same meaning)
- Using ideas without giving credit

## What Makes This Project Special?

Most basic plagiarism checkers just look for **exact word matches**. Our system is smarter:
- It understands **meaning**, not just words
- It detects **paraphrased content** (changed words, same meaning)
- It uses **3 different algorithms** and combines them for accuracy

---

# 2. WHY DID WE BUILD THIS?

## The Problem

| Problem | Impact |
|---------|--------|
| Manual checking is slow | Teacher spends hours per assignment |
| Students copy and change words | Simple tools fail to detect |
| No evidence/documentation | Hard to prove plagiarism |
| No centralized system | Each teacher checks independently |

## Our Solution

An automated AI-powered system that:
1. Checks documents in **seconds** (not hours)
2. Detects both **exact copying** and **paraphrasing**
3. Provides **evidence** with matched sentence highlights
4. Generates **PDF reports** for documentation
5. Stores **history** of all checks

## Real-World Applications

- **Universities** — Check student assignments and theses
- **Online platforms** — Verify article originality
- **Publishers** — Check manuscripts before publishing
- **Companies** — Verify content uniqueness

---

# 3. WHAT DOES IT DO?

## Core Features (Explained Simply)

### Feature 1: Text Analysis
You paste any text → System compares it → Shows similarity %

### Feature 2: File Upload
Upload a .TXT, .PDF, or .DOCX file → System extracts text → Analyzes it

### Feature 3: Three Algorithm Detection
```
Your Text
    │
    ├──► TF-IDF Analysis ──────► Score 1 (50% weight)
    │
    ├──► N-Gram Analysis ──────► Score 2 (20% weight)
    │
    └──► Fuzzy Matching ───────► Score 3 (30% weight)
                                        │
                                        ▼
                              Combined Score (0-100%)
                                        │
                                        ▼
                              Classification Label
```

### Feature 4: Classification

| Score Range | Classification | What It Means |
|-------------|----------------|---------------|
| 0% – 20% | Mostly Original | Very little similarity, likely original |
| 20% – 40% | Low Similarity | Some common phrases, probably fine |
| 40% – 60% | Moderate Similarity | Notable overlap, review recommended |
| 60% – 80% | High Similarity | Significant copying detected |
| 80% – 100% | Potential Plagiarism | Very high chance of plagiarism |

### Feature 5: PDF Report Generation
Download a professional PDF showing:
- Similarity score with color coding
- Matched sentences highlighted
- Source documents identified
- Algorithm breakdown

### Feature 6: History
All past analyses saved — view, compare, delete any time.

### Feature 7: Document Management
Upload and manage the reference database — add new references, remove old ones.

---

# 4. TECHNOLOGIES USED

## What Is Each Technology? (Beginner Guide)

### Python
- **What:** A programming language, easy to read and write
- **Why we used it:** Best ecosystem for AI/ML/NLP work
- **Used for:** Backend, NLP algorithms, database operations

### FastAPI
- **What:** A tool (framework) to build web APIs using Python
- **Why we used it:** Very fast, automatic documentation, modern
- **Used for:** Creating all the API endpoints (routes)

### React.js
- **What:** A JavaScript library for building user interfaces
- **Why we used it:** Component-based, fast, popular
- **Used for:** All the web pages users see and interact with

### SQLite
- **What:** A lightweight database stored as a single file
- **Why we used it:** No setup needed, perfect for local projects
- **Used for:** Storing analysis history and reference documents

### SQLAlchemy
- **What:** A Python library to talk to databases using Python code (no SQL needed)
- **Why we used it:** Cleaner code, easier to maintain
- **Used for:** All database operations (save, read, delete)

### scikit-learn (sklearn)
- **What:** Python's most popular machine learning library
- **Why we used it:** Has TF-IDF built in
- **Used for:** TF-IDF vectorization and cosine similarity

### NLTK (Natural Language Toolkit)
- **What:** Python library for processing human language
- **Why we used it:** Has tokenizers and stopword lists
- **Used for:** Text preprocessing (splitting sentences, removing stopwords)

### RapidFuzz
- **What:** Ultra-fast fuzzy string matching library
- **Why we used it:** Much faster than FuzzyWuzzy (older library)
- **Used for:** Fuzzy string comparison between sentences

### ReportLab
- **What:** Python library to create PDF files
- **Why we used it:** Generates professional-looking reports
- **Used for:** PDF report generation

### Vite
- **What:** A modern frontend build tool
- **Why we used it:** Super fast development server
- **Used for:** Running and building the React frontend

### Axios
- **What:** JavaScript library for making HTTP requests
- **Why we used it:** Clean API, handles errors well
- **Used for:** Frontend calling the backend API

---

# 5. SYSTEM ARCHITECTURE

## What Is Architecture?

Architecture is like a **blueprint of a building**. It shows how different parts connect.

## Our System Has 3 Layers

```
┌─────────────────────────────────────────────────────┐
│                   USER'S BROWSER                    │
│              React Frontend (Port 5173)             │
│  Home | Analyze | Results | History | Documents     │
└────────────────────┬────────────────────────────────┘
                     │  HTTP Requests (Axios)
                     │
┌────────────────────▼────────────────────────────────┐
│               BACKEND SERVER (Port 8000)            │
│                 FastAPI + Python                    │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐ │
│  │  Routes  │  │ Services │  │    Utilities       │ │
│  │ /analyze │  │  TF-IDF  │  │  Text Extractor   │ │
│  │/documents│  │  N-grams │  │  File Handler     │ │
│  │ /reports │  │  Fuzzy   │  │  PDF Generator    │ │
│  └──────────┘  └──────────┘  └───────────────────┘ │
└────────────────────┬────────────────────────────────┘
                     │  SQLAlchemy ORM
                     │
┌────────────────────▼────────────────────────────────┐
│                   DATABASE                          │
│                SQLite (.db file)                    │
│                                                     │
│  ┌──────────────┐    ┌─────────────────────────┐   │
│  │   Analysis   │    │    Reference Documents  │   │
│  │   History    │    │                         │   │
│  └──────────────┘    └─────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## How a Request Flows

```
User types text → Clicks Analyze
      ↓
React sends POST /api/analyze
      ↓
FastAPI receives request
      ↓
Loads reference documents from SQLite
      ↓
Runs TF-IDF + N-gram + Fuzzy algorithms
      ↓
Calculates weighted combined score
      ↓
Saves result to database
      ↓
Returns JSON response
      ↓
React displays Results page
```

---

# 6. HOW NLP WORKS IN THIS PROJECT

## What Is NLP?

NLP stands for **Natural Language Processing**. It's the field of AI that deals with understanding human language (text and speech).

Think of it like teaching a computer to **read and understand** what we write.

## Step-by-Step: How We Process Text

### Step 1: Text Input
```
Raw Input: "Machine Learning is a branch of AI that helps computers learn!"
```

### Step 2: Normalization (Cleaning)
Convert to lowercase, remove special characters:
```
After: "machine learning is a branch of ai that helps computers learn"
```

### Step 3: Tokenization (Splitting into Words)
```
Tokens: ["machine", "learning", "is", "a", "branch", "of", "ai", 
         "that", "helps", "computers", "learn"]
```

### Step 4: Stopword Removal
Remove common words (is, a, of, that) that carry no meaning:
```
After: ["machine", "learning", "branch", "ai", "helps", "computers", "learn"]
```

### Step 5: Sentence Splitting
For longer documents, split into individual sentences:
```
Sentence 1: "Machine learning is a branch of AI."
Sentence 2: "It helps computers learn from data."
```

### Step 6: Algorithm Processing
Feed cleaned text into TF-IDF, N-gram, and Fuzzy algorithms.

---

# 7. ALGORITHM DEEP DIVE

## Algorithm 1: TF-IDF (Weight: 50%)

### What Does TF-IDF Stand For?
**TF** = Term Frequency  
**IDF** = Inverse Document Frequency

### Simple Explanation
TF-IDF tells us **how important a word is** in a document.

**TF (Term Frequency)** = How many times a word appears in the document
```
Document: "cat cat dog cat"
TF("cat") = 3/4 = 0.75  (appears 3 times out of 4 total words)
TF("dog") = 1/4 = 0.25
```

**IDF (Inverse Document Frequency)** = How rare the word is across ALL documents
```
If "cat" appears in most documents → low IDF (not important, too common)
If "blockchain" appears in few documents → high IDF (important, rare word)
```

**TF-IDF Score = TF × IDF**

Words that are **frequent in one doc** but **rare across all docs** get HIGH scores.
Words like "the", "is", "and" get very LOW scores (common everywhere).

### Cosine Similarity
After converting text to TF-IDF numbers, we measure similarity using **cosine similarity**:
```
Think of each document as an arrow in space.
If two arrows point in the same direction → similar documents
If they point in opposite directions → very different documents
Cosine similarity = cos(angle between them) → 0 to 1
```

### Why 50% Weight?
TF-IDF is best at capturing **topic-level similarity** — it catches when two documents discuss the same subject even with different words. It's our most reliable algorithm.

---

## Algorithm 2: N-Gram Similarity (Weight: 20%)

### What Is an N-Gram?

An N-gram is a **sequence of N consecutive words**.

```
Text: "artificial intelligence is amazing"

Unigrams (N=1): ["artificial", "intelligence", "is", "amazing"]

Bigrams (N=2):  ["artificial intelligence", "intelligence is", "is amazing"]

Trigrams (N=3): ["artificial intelligence is", "intelligence is amazing"]
```

### How We Use It

We use **Bigrams (N=2)** — pairs of consecutive words.

**Jaccard Similarity Formula:**
```
Jaccard = (Common N-grams) / (All unique N-grams)

Example:
Text1 bigrams: {"machine learning", "learning is", "is powerful"}
Text2 bigrams: {"machine learning", "learning was", "was useful"}

Common: {"machine learning"} = 1
All unique: {"machine learning", "learning is", "is powerful", "learning was", "was useful"} = 5

Jaccard = 1/5 = 0.20 = 20%
```

### Why Is This Useful?
N-grams catch **exact phrase copying**. If someone copies "machine learning algorithms use statistical techniques" directly, the bigrams will match perfectly.

### Why Only 20% Weight?
N-grams miss **paraphrased content** — if you change word order or synonyms, bigrams won't match. That's why it's a supporting algorithm, not the main one.

---

## Algorithm 3: Fuzzy Matching (Weight: 30%)

### What Is Fuzzy Matching?

Fuzzy matching measures similarity between strings **character by character**, allowing for small differences.

```
"machine learning"  vs  "machine leraning"  → 94% match (typo)
"artificial intelligence"  vs  "AI"  → 0% match (too different)
```

### How We Use It

We compare **each sentence** from the submitted document against each sentence in reference documents.

**Token Set Ratio** (what we use):
1. Split both sentences into words (tokens)
2. Find common words
3. Calculate ratio = common / total

```
Sentence A: "Deep learning uses neural networks"
Sentence B: "Neural networks are used in deep learning"

Common words: {deep, learning, neural, networks} = 4 words
Total unique: {deep, learning, uses, neural, networks, are, used, in} = 8 words
Score = 4/8 = 50%... but token_set_ratio handles ordering → gets ~85%
```

### Sentence Coverage Score
Our final fuzzy score = (sentences that matched / total sentences) × average match quality

```
If 8 out of 10 sentences match at 90% average:
Fuzzy Score = (8/10) × 90 = 72%
```

### Why 30% Weight?
Fuzzy matching is good at catching **minor modifications** — changed word order, slight rephrasing. But it can produce false positives on short texts, so we weight it less than TF-IDF.

---

## Final Combined Score

```
Combined Score = (TF-IDF × 0.50) + (N-gram × 0.20) + (Fuzzy × 0.30)

Example:
TF-IDF = 89.87%  →  89.87 × 0.50 = 44.94
N-gram = 64.13%  →  64.13 × 0.20 = 12.83
Fuzzy  = 99.37%  →  99.37 × 0.30 = 29.81

Combined = 44.94 + 12.83 + 29.81 = 87.57% → "Potential Plagiarism"
```

---

# 8. PROJECT FOLDER STRUCTURE

```
Combat/                          ← Root project folder
│
├── README.md                    ← Main documentation
├── DEMO_GUIDE.md               ← Demonstration guide
├── PROJECT_REPORT.md           ← This file
├── .gitignore                   ← Files to ignore in git
│
├── backend/                     ← Python FastAPI server
│   ├── app/                     ← Main application code
│   │   ├── __init__.py
│   │   ├── main.py             ← App entry point, CORS setup
│   │   ├── config.py           ← Settings (weights, thresholds)
│   │   │
│   │   ├── api/                ← API route handlers
│   │   │   ├── routes_analysis.py   ← /analyze endpoints
│   │   │   ├── routes_documents.py  ← /documents endpoints
│   │   │   └── routes_reports.py    ← /reports endpoints
│   │   │
│   │   ├── models/             ← Database models
│   │   │   ├── database.py     ← SQLAlchemy models + DB setup
│   │   │   └── schemas.py      ← Pydantic request/response schemas
│   │   │
│   │   ├── services/           ← Business logic (NLP algorithms)
│   │   │   ├── preprocessing.py      ← Text cleaning & tokenization
│   │   │   ├── tfidf_similarity.py   ← TF-IDF algorithm
│   │   │   ├── ngram_similarity.py   ← N-gram algorithm
│   │   │   ├── fuzzy_matching.py     ← Fuzzy matching algorithm
│   │   │   ├── plagiarism_engine.py  ← Combines all 3 algorithms
│   │   │   └── report_generator.py  ← PDF report creation
│   │   │
│   │   └── utils/              ← Helper functions
│   │       ├── text_extractor.py    ← Extract text from PDF/DOCX/TXT
│   │       └── helpers.py           ← File handling, validation
│   │
│   ├── datasets/               ← Sample data
│   │   ├── sample_documents/   ← 5 reference documents
│   │   └── test_documents/     ← 4 test cases
│   │
│   ├── tests/                  ← Unit tests (100+ tests)
│   │   ├── test_preprocessing.py
│   │   ├── test_similarity.py
│   │   └── test_api.py
│   │
│   ├── venv/                   ← Python virtual environment
│   ├── requirements.txt        ← Python dependencies list
│   ├── evaluation.py           ← System accuracy tester
│   └── pytest.ini             ← Test configuration
│
└── frontend/                   ← React.js web interface
    ├── src/
    │   ├── main.jsx            ← React entry point
    │   ├── App.jsx             ← Routing setup
    │   ├── index.css           ← Global styles
    │   │
    │   ├── pages/              ← Web pages
    │   │   ├── Home.jsx/.css        ← Landing page
    │   │   ├── Analyze.jsx/.css     ← Analysis input page
    │   │   ├── Results.jsx/.css     ← Results display page
    │   │   ├── History.jsx/.css     ← Past analyses page
    │   │   └── Documents.jsx/.css   ← Reference docs manager
    │   │
    │   ├── components/         ← Reusable UI parts
    │   │   ├── Navbar.jsx/.css      ← Navigation bar
    │   │
    │   └── services/           ← API communication
    │       └── api.js               ← All backend API calls
    │
    ├── package.json            ← Node.js dependencies
    ├── vite.config.js          ← Vite build configuration
    └── index.html              ← HTML template
```

---

# 9. DATABASE DESIGN

## What Is a Database?

A database is like a **spreadsheet** that stores information permanently. Even if you close the app, data remains.

## Our Tables

### Table 1: reference_documents
Stores the reference documents uploaded by the teacher.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Unique ID (auto) |
| filename | String | File name |
| original_filename | String | Original uploaded name |
| file_extension | String | .txt, .pdf, .docx |
| file_size | Integer | Size in bytes |
| text_content | Text | Full extracted text |
| word_count | Integer | Number of words |
| sentence_count | Integer | Number of sentences |
| upload_date | DateTime | When uploaded |

### Table 2: analysis_history
Stores every plagiarism check result.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Unique ID (auto) |
| document_name | String | Name of analyzed document |
| analysis_date | DateTime | When analyzed |
| overall_similarity | Float | Final combined score (%) |
| tfidf_score | Float | TF-IDF component score |
| ngram_score | Float | N-gram component score |
| fuzzy_score | Float | Fuzzy matching score |
| classification | String | Category label |
| total_matches | Integer | Number of matched sentences |
| sources | JSON | Which references matched |
| sentence_matches | JSON | Matched sentence pairs |
| submitted_text | Text | The original submitted text |

### Table 3: analysis_reports
Stores generated PDF reports.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Unique ID (auto) |
| analysis_id | Integer | Links to analysis_history |
| report_filename | String | PDF file name |
| generation_date | DateTime | When created |
| file_path | String | Where PDF is saved |

---

# 10. API ENDPOINTS

## What Is an API?

API stands for **Application Programming Interface**. Think of it as a **menu at a restaurant** — you place an order (request), the kitchen (server) prepares it, and you get your food (response).

## Our API Routes

### Analysis Endpoints

| Method | URL | What It Does |
|--------|-----|--------------|
| POST | /api/analyze | Analyze pasted text |
| POST | /api/analyze/file | Analyze uploaded file |
| GET | /api/analyze/history | Get all past analyses |
| GET | /api/analyze/history/{id} | Get one analysis detail |
| DELETE | /api/analyze/history/{id} | Delete an analysis |
| GET | /api/analyze/statistics | Get system stats |

### Document Endpoints

| Method | URL | What It Does |
|--------|-----|--------------|
| GET | /api/documents | List all reference docs |
| POST | /api/documents/upload | Upload a reference doc |
| DELETE | /api/documents/{id} | Delete a reference doc |
| GET | /api/documents/statistics/summary | Document stats |

### Report Endpoints

| Method | URL | What It Does |
|--------|-----|--------------|
| POST | /api/reports/generate | Generate PDF report |
| GET | /api/reports/download/{id} | Download PDF |
| GET | /api/reports/analysis/{id} | Reports for an analysis |

## Example API Call

**Request (Frontend → Backend):**
```json
POST /api/analyze
{
  "text": "Machine learning is a subset of artificial intelligence...",
  "document_name": "My Assignment"
}
```

**Response (Backend → Frontend):**
```json
{
  "analysis_id": 5,
  "document_name": "My Assignment",
  "overall_similarity": 87.57,
  "classification": "Potential Plagiarism",
  "scores": {
    "tfidf": 89.87,
    "ngram": 64.13,
    "fuzzy": 99.37
  },
  "sources": [
    {"name": "document_01_ai_ml.txt", "similarity": 87.57}
  ],
  "total_matches": 12
}
```

---

# 11. FRONTEND PAGES

## Page 1: Home (/)

**What it shows:**
- Project title and description
- Key features with icons
- Statistics (total analyses, documents, average similarity)
- "Start Analyzing" button

**Purpose:** First impression — explains the project to users

---

## Page 2: Analyze (/analyze)

**What it shows:**
- Two tabs: "Paste Text" and "Upload File"
- Text area for direct input
- File upload area (drag & drop or click)
- "Analyze for Plagiarism" button
- Loading spinner during analysis

**Purpose:** Main input page for submitting documents

---

## Page 3: Results (/results/:id)

**What it shows:**
- Document information (name, date, word count)
- Large similarity percentage with color coding
- Classification badge (e.g., "Potential Plagiarism")
- Three component scores (TF-IDF, N-gram, Fuzzy)
- Matching sources list with individual scores
- Match statistics (total matches, high similarity count)
- "Download Report" button
- Disclaimer notice

**Color coding:**
- 🔴 Red → 80-100% (Potential Plagiarism)
- 🟠 Orange → 60-80% (High Similarity)
- 🟡 Yellow → 40-60% (Moderate Similarity)
- 🟢 Light Green → 20-40% (Low Similarity)
- 💚 Dark Green → 0-20% (Mostly Original)

---

## Page 4: History (/history)

**What it shows:**
- List of all past analyses
- Each entry: document name, date, similarity %, classification
- Click to view full details
- Delete button for each entry
- Pagination for large lists

**Purpose:** Track all submissions over time

---

## Page 5: Documents (/documents)

**What it shows:**
- List of all uploaded reference documents
- Document details: name, size, word count, upload date
- Upload new reference document button
- Delete reference document button
- Statistics summary

**Purpose:** Manage the reference database

---

# 12. HOW TO RUN THE PROJECT

## Prerequisites

- Python 3.8 or higher installed
- Node.js 16 or higher installed
- Internet connection (for first-time package install)

## Step 1: Backend Setup

```powershell
# Open Terminal 1
cd C:\Users\bhanu\OneDrive\Desktop\Combat\backend

# Activate virtual environment
.\venv\Scripts\activate

# Start the backend server
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 2: Frontend Setup

```powershell
# Open Terminal 2
cd C:\Users\bhanu\OneDrive\Desktop\Combat\frontend

# Start the frontend
npm run dev
```

You should see:
```
VITE v5.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

## Step 3: Open the App

Open your browser and go to: **http://localhost:5173**

## Step 4: Upload Reference Documents

1. Click "Documents" in the navbar
2. Upload the 5 files from:
   ```
   backend\datasets\sample_documents\
   ```

## Step 5: Run Your First Analysis

1. Click "Analyze"
2. Paste any text (minimum 50 characters)
3. Click "Analyze for Plagiarism"
4. View your results!

---

# 13. TEST RESULTS & EVALUATION

## Test Cases

We created 4 test documents to verify the system works correctly.

### Test 1: High Similarity (Copied Content)
```
File: high_similarity_text.txt
Content: Directly copied from the AI/ML reference document

Expected: >75% similarity
Actual:   87.57%  ✅ PASS
Category: Potential Plagiarism
```

### Test 2: Moderate Similarity (Paraphrased Content)
```
File: moderate_similarity_text.txt
Content: Same topic as AI/ML doc but different words

Expected: 30-65% similarity
Actual:   37.13%  ✅ PASS
Category: Low Similarity
```

### Test 3: Low Similarity (Different Topic)
```
File: low_similarity_text.txt
Content: About Ancient Rome (completely different topic)

Expected: 0-25% similarity
Actual:   3.34%   ✅ PASS
Category: Mostly Original
```

### Test 4: Original Content
```
File: original_text.txt
Content: About Renewable Energy (original writing)

Expected: 0-30% similarity
Actual:   14.96%  ✅ PASS
Category: Mostly Original
```

## Overall System Accuracy

```
✅ Tests Passed: 4/4
📊 Accuracy: 100%
```

## Component Performance

| Algorithm | Average Score | Behavior |
|-----------|--------------|----------|
| TF-IDF | 48% average | Good semantic detection |
| N-gram | 17% average | Phrase-level matching |
| Fuzzy | 25% average | Sentence-level coverage |

---

# 14. LIMITATIONS

Every system has limitations. Being honest about them shows maturity.

| Limitation | Explanation | Workaround |
|------------|-------------|------------|
| Local references only | Only compares against uploaded docs, not the internet | Upload more reference documents |
| English only | NLTK stopwords are English-only | Add multilingual support |
| Short text issues | Very short texts (<50 chars) may give inaccurate scores | Require minimum text length |
| No code detection | Can't detect code plagiarism | Add AST-based code comparison |
| No image detection | Can't detect image copying | Outside project scope |
| Paraphrase limits | Heavy paraphrasing may lower score | Use BERT embeddings in future |

---

# 15. FUTURE IMPROVEMENTS

If we had more time, we would add:

### Short Term (1-3 months)
1. **User accounts** — Login system for teachers/students
2. **Batch upload** — Analyze 50 files at once
3. **Email reports** — Send PDF directly to email
4. **Dark mode** — UI theme toggle

### Medium Term (3-6 months)
1. **Internet search** — Compare against live web content
2. **Better paraphrase detection** — Use BERT/sentence-transformers
3. **Citation detection** — Identify and exclude proper citations
4. **Multiple languages** — Support Hindi, Telugu, etc.

### Long Term (6+ months)
1. **LMS Integration** — Plug into Moodle, Canvas, Google Classroom
2. **Code plagiarism** — Detect copied code with AST comparison
3. **Mobile app** — React Native mobile version
4. **Blockchain certificates** — Tamper-proof originality certificates

---

# 16. VIVA QUESTIONS & ANSWERS

## Basic Level

**Q: What is plagiarism?**
A: Plagiarism is copying someone else's work (text, ideas, code) and presenting it as your own without proper attribution or credit.

**Q: What does NLP stand for?**
A: Natural Language Processing — the branch of AI that deals with teaching computers to understand human language.

**Q: Name the three algorithms used.**
A: TF-IDF (50%), N-gram Similarity (20%), and Fuzzy Matching (30%).

**Q: What does TF-IDF stand for?**
A: Term Frequency – Inverse Document Frequency. TF measures how often a word appears in a document; IDF measures how rare the word is across all documents.

**Q: What is an N-gram?**
A: A sequence of N consecutive words. "machine learning" is a bigram (N=2). "machine learning is" is a trigram (N=3).

**Q: What is fuzzy matching?**
A: A technique that compares strings character by character, allowing for small differences like typos or word order changes.

## Intermediate Level

**Q: Why do you use three algorithms instead of one?**
A: Each algorithm catches different types of plagiarism. TF-IDF catches semantic similarity, N-grams catch exact phrase copying, and Fuzzy matching catches minor modifications. Combining them gives better accuracy than any single algorithm.

**Q: Why is TF-IDF weight 50% and not higher?**
A: TF-IDF is our most reliable algorithm for semantic understanding. But it alone could miss exact phrase copies (N-grams catch those) or slightly modified text (Fuzzy catches that). The 50-20-30 split was tuned through testing to give best overall accuracy.

**Q: What is cosine similarity?**
A: A mathematical measure of similarity between two vectors (lists of numbers). Two documents are converted to TF-IDF number vectors, and cosine similarity measures the angle between them. If the angle is 0°, the documents are identical (score = 1.0). If angle is 90°, they are completely different (score = 0.0).

**Q: What is the difference between stopwords and keywords?**
A: Stopwords are common words (the, is, and, or, but) that appear everywhere and carry no meaning — we remove them. Keywords are important, meaningful words (algorithm, neural, blockchain) that help identify topics.

**Q: Why SQLite instead of MySQL or PostgreSQL?**
A: SQLite is file-based (no server to install), perfect for a standalone student project. For production at scale, we would migrate to PostgreSQL for better concurrent access and performance.

## Advanced Level

**Q: What is the time complexity of your system?**
A: For a query of length n, and m reference documents each of average length k words:
- Preprocessing: O(n)
- TF-IDF: O(n + mk) fit, O(n) transform
- N-gram: O(n × k) per document → O(m × n × k) total
- Fuzzy: O(sentences_query × sentences_ref) per document
- Overall: approximately O(m × n × k)

For our test (5 refs, ~500 words each): runs in ~1-2 seconds.

**Q: How does your system handle paraphrasing?**
A: TF-IDF is the key algorithm here. Because TF-IDF measures term importance rather than exact word matches, documents with similar vocabulary and topics score similarly even with different sentence structures. N-grams will have lower scores for paraphrased content, but the TF-IDF score (50% weight) still captures the semantic overlap.

**Q: How would you scale this system for 10,000 users?**
A: Several strategies:
1. Replace SQLite with PostgreSQL for concurrent access
2. Pre-compute and cache TF-IDF vectors for reference documents
3. Use Celery + Redis for background task processing
4. Add a load balancer for multiple FastAPI instances
5. Use Elasticsearch for vector similarity search at scale
6. Consider BERT embeddings for better semantic understanding

**Q: What are the ethical considerations in plagiarism detection?**
A: 
1. False positives can unfairly accuse innocent students
2. System should flag for human review, not automatically punish
3. Common knowledge phrases should be excluded
4. Cultural differences in citation practices should be considered
5. Data privacy — submitted texts should be protected

---

# 17. CONCLUSION

## What We Achieved

This project successfully demonstrates an **AI-powered plagiarism detection system** that:

1. ✅ Implements **3 NLP algorithms** (TF-IDF, N-grams, Fuzzy Matching) in a combined pipeline
2. ✅ Achieves **100% accuracy** on test cases (4/4 tests pass)
3. ✅ Provides a **full-stack web application** (React + FastAPI)
4. ✅ Generates **professional PDF reports** with color-coded analysis
5. ✅ Stores **complete history** of all analyses in a database
6. ✅ Supports **multiple file formats** (TXT, PDF, DOCX)
7. ✅ Has **100+ unit tests** ensuring code reliability

## Key Learning Outcomes

Through this project, we learned:

- **NLP concepts**: How computers process and understand text
- **Machine Learning**: TF-IDF vectorization and cosine similarity
- **Full-stack development**: Building both backend APIs and frontend UI
- **Database design**: Relational schema design with SQLAlchemy
- **API design**: RESTful principles and FastAPI
- **Software engineering**: Modular code, unit testing, documentation

## Final Message

This project is more than just a plagiarism detector — it's a demonstration of how **multiple AI techniques can be combined** to solve a real-world problem. The system is transparent (you can see WHY something was flagged), configurable (weights can be tuned), and extensible (designed for future improvements).

---

*Report prepared for BTech CSE Project Demonstration*  
*System: Combat Online Plagiarism with AI*  
*Status: Complete and Functional*
