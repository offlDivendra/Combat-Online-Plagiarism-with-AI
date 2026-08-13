# Sample Documents Dataset

This directory contains sample documents for testing and demonstrating the plagiarism detection system.

## Directory Structure

### sample_documents/
Reference documents covering various topics:
- **document_01_ai_ml.txt** - Artificial Intelligence and Machine Learning
- **document_02_climate_change.txt** - Climate Change and Environmental Impact
- **document_03_cybersecurity.txt** - Cybersecurity in the Digital Age
- **document_04_education_technology.txt** - Educational Technology and Digital Learning
- **document_05_blockchain.txt** - Blockchain Technology and Decentralized Systems

### test_documents/
Test documents with varying levels of similarity for demonstration:
- **original_text.txt** - Original content about renewable energy
- **high_similarity_text.txt** - High similarity to document_01_ai_ml.txt (~80-90% expected)
- **moderate_similarity_text.txt** - Moderate similarity to document_01_ai_ml.txt (~40-60% expected)
- **low_similarity_text.txt** - Low similarity (completely different topic: Ancient Rome)

## Usage

### Loading Reference Documents

Upload the reference documents to the system via:
1. API: POST `/api/documents/upload`
2. Frontend: Documents page upload interface

### Running Demo Tests

1. Upload all reference documents from `sample_documents/`
2. Test with documents from `test_documents/` to see different similarity levels
3. Compare the **high_similarity_text.txt** against the references to see ~80%+ match
4. Compare the **moderate_similarity_text.txt** to see ~40-60% match
5. Compare the **low_similarity_text.txt** to see minimal similarity

## Document Characteristics

### Reference Documents
- Average length: 300-400 words
- Topics: Technology, science, and social issues
- Writing style: Academic/informative
- All original content (not copyrighted)

### Test Documents
- **high_similarity_text.txt**: Contains multiple sentences directly copied from document_01_ai_ml.txt
- **moderate_similarity_text.txt**: Paraphrased version with similar concepts but different wording
- **low_similarity_text.txt**: Completely different topic to show system can distinguish unrelated content
- **original_text.txt**: Unique content for comparison

## Expected Results

When analyzing **high_similarity_text.txt**:
- Overall Similarity: 75-90%
- Classification: High Similarity or Potential Plagiarism
- Sentence Matches: 8-12 high-confidence matches
- Top Source: document_01_ai_ml.txt

When analyzing **moderate_similarity_text.txt**:
- Overall Similarity: 40-60%
- Classification: Moderate Similarity
- Sentence Matches: 3-6 moderate-confidence matches
- Fuzzy matching score higher than exact matches

When analyzing **low_similarity_text.txt**:
- Overall Similarity: 5-20%
- Classification: Mostly Original or Low Similarity
- Sentence Matches: 0-2 low-confidence matches
- No significant source matches

## Notes

- All documents are original content created for this project
- Documents are designed to test different aspects of the NLP pipeline
- Similarity percentages may vary slightly depending on configuration weights
- These documents are safe to use for educational and demonstration purposes
