"""
Evaluation Script for Plagiarism Detection System
Tests accuracy and performance of the NLP pipeline.
"""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.plagiarism_engine import plagiarism_engine
from app.services.preprocessing import preprocessor
from app.utils.text_extractor import text_extractor


class PlagiarismEvaluator:
    """
    Evaluates the plagiarism detection system accuracy.
    """
    
    def __init__(self):
        self.results = []
        self.test_cases = []
    
    def load_test_documents(self):
        """Load test documents from datasets directory."""
        base_path = Path(__file__).parent / "datasets"
        
        # Load reference documents
        ref_path = base_path / "sample_documents"
        reference_files = list(ref_path.glob("*.txt"))
        
        reference_texts = []
        reference_names = []
        
        for ref_file in reference_files:
            with open(ref_file, 'r', encoding='utf-8') as f:
                reference_texts.append(f.read())
                reference_names.append(ref_file.name)
        
        print(f"✓ Loaded {len(reference_texts)} reference documents")
        
        # Load test documents
        test_path = base_path / "test_documents"
        
        # Define expected results for each test document
        self.test_cases = [
            {
                "file": "high_similarity_text.txt",
                "expected_range": (75, 95),
                "expected_classification": ["High Similarity", "Potential Plagiarism"],
                "description": "High similarity test (copied content)"
            },
            {
                "file": "moderate_similarity_text.txt",
                "expected_range": (30, 65),
                "expected_classification": ["Moderate Similarity", "High Similarity", "Low Similarity"],
                "description": "Moderate similarity test (paraphrased content)"
            },
            {
                "file": "low_similarity_text.txt",
                "expected_range": (0, 25),
                "expected_classification": ["Mostly Original", "Low Similarity"],
                "description": "Low similarity test (different topic)"
            },
            {
                "file": "original_text.txt",
                "expected_range": (0, 30),
                "expected_classification": ["Mostly Original", "Low Similarity"],
                "description": "Original content test"
            }
        ]
        
        return reference_texts, reference_names
    
    def evaluate_test_case(self, test_case, reference_texts, reference_names):
        """
        Evaluate a single test case.
        
        Args:
            test_case: Test case dictionary
            reference_texts: List of reference texts
            reference_names: List of reference names
            
        Returns:
            Evaluation result dictionary
        """
        test_file = Path(__file__).parent / "datasets" / "test_documents" / test_case["file"]
        
        # Load test text
        with open(test_file, 'r', encoding='utf-8') as f:
            query_text = f.read()
        
        print(f"\n{'='*70}")
        print(f"Testing: {test_case['description']}")
        print(f"File: {test_case['file']}")
        print(f"{'='*70}")
        
        # Perform analysis
        result = plagiarism_engine.analyze_document(
            query_text=query_text,
            reference_texts=reference_texts,
            reference_names=reference_names
        )
        
        similarity = result["overall_similarity"]
        classification = result["classification"]
        
        # Check if results are in expected range
        expected_min, expected_max = test_case["expected_range"]
        in_range = expected_min <= similarity <= expected_max
        classification_correct = classification in test_case["expected_classification"]
        
        # Display results
        print(f"\n📊 Results:")
        print(f"  Overall Similarity: {similarity:.2f}%")
        print(f"  Classification: {classification}")
        print(f"  TF-IDF Score: {result['scores']['tfidf']:.2f}%")
        print(f"  N-Gram Score: {result['scores']['ngram']:.2f}%")
        print(f"  Fuzzy Score: {result['scores']['fuzzy']:.2f}%")
        print(f"  Matched Sentences: {result['total_matches']}")
        print(f"  High Similarity Matches: {result['high_similarity_matches']}")
        
        print(f"\n✓ Expected Range: {expected_min}-{expected_max}%")
        print(f"✓ Expected Classifications: {', '.join(test_case['expected_classification'])}")
        
        if in_range:
            print(f"✅ PASS: Similarity within expected range")
        else:
            print(f"❌ FAIL: Similarity outside expected range")
        
        if classification_correct:
            print(f"✅ PASS: Classification correct")
        else:
            print(f"❌ FAIL: Classification incorrect")
        
        # Top matching sources
        if result["sources"]:
            print(f"\n📚 Top Matching Sources:")
            for i, source in enumerate(result["sources"][:3], 1):
                print(f"  {i}. {source['name']}: {source['similarity']:.2f}%")
        
        return {
            "test_case": test_case["file"],
            "description": test_case["description"],
            "similarity": similarity,
            "classification": classification,
            "expected_range": test_case["expected_range"],
            "in_range": in_range,
            "classification_correct": classification_correct,
            "passed": in_range and classification_correct,
            "component_scores": result["scores"],
            "matches": result["total_matches"]
        }
    
    def run_evaluation(self):
        """Run complete evaluation suite."""
        print("="*70)
        print(" AI PLAGIARISM DETECTION SYSTEM - EVALUATION")
        print("="*70)
        
        # Load documents
        reference_texts, reference_names = self.load_test_documents()
        
        # Run test cases
        for test_case in self.test_cases:
            result = self.evaluate_test_case(test_case, reference_texts, reference_names)
            self.results.append(result)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print evaluation summary."""
        print("\n" + "="*70)
        print(" EVALUATION SUMMARY")
        print("="*70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        accuracy = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Overall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests} ✅")
        print(f"  Failed: {failed_tests} ❌")
        print(f"  Accuracy: {accuracy:.1f}%")
        
        print(f"\n📊 Detailed Results:")
        print(f"  {'Test Case':<40} {'Similarity':<12} {'Status':<8}")
        print(f"  {'-'*60}")
        
        for result in self.results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"  {result['test_case']:<40} {result['similarity']:>6.2f}% {status:>12}")
        
        print(f"\n💡 Algorithm Performance:")
        avg_tfidf = sum(r["component_scores"]["tfidf"] for r in self.results) / len(self.results)
        avg_ngram = sum(r["component_scores"]["ngram"] for r in self.results) / len(self.results)
        avg_fuzzy = sum(r["component_scores"]["fuzzy"] for r in self.results) / len(self.results)
        
        print(f"  Average TF-IDF Score: {avg_tfidf:.2f}%")
        print(f"  Average N-Gram Score: {avg_ngram:.2f}%")
        print(f"  Average Fuzzy Score: {avg_fuzzy:.2f}%")
        
        print(f"\n📝 Notes:")
        print(f"  - Similarity ranges are heuristic and may vary by ±5%")
        print(f"  - System is designed to err on the side of caution")
        print(f"  - Human review is always recommended for final decisions")
        
        if accuracy >= 75:
            print(f"\n✅ System performance is ACCEPTABLE for demonstration purposes")
        else:
            print(f"\n⚠️  System performance needs improvement")
        
        print("\n" + "="*70)


def test_individual_components():
    """Test individual NLP components."""
    print("\n" + "="*70)
    print(" COMPONENT TESTS")
    print("="*70)
    
    from app.services.tfidf_similarity import TfidfSimilarityAnalyzer
    from app.services.ngram_similarity import NgramSimilarityAnalyzer
    from app.services.fuzzy_matching import FuzzyMatchingAnalyzer
    
    test_text1 = "Machine learning is a branch of artificial intelligence."
    test_text2 = "Machine learning is a field of artificial intelligence."
    
    print("\n🔬 Testing with sample sentences:")
    print(f"  Text 1: {test_text1}")
    print(f"  Text 2: {test_text2}")
    
    # TF-IDF Test
    print("\n📊 TF-IDF Test:")
    tfidf = TfidfSimilarityAnalyzer()
    tfidf.fit_references([test_text1])
    tfidf_sim = tfidf.calculate_similarity(test_text2)[0]
    print(f"  Similarity: {tfidf_sim*100:.2f}%")
    print(f"  Status: {'✅ Working' if tfidf_sim > 0.5 else '❌ Issue detected'}")
    
    # N-Gram Test
    print("\n📊 N-Gram Test:")
    ngram = NgramSimilarityAnalyzer(n=2)
    ngram_sim = ngram.calculate_similarity(test_text1, test_text2)
    print(f"  Similarity: {ngram_sim*100:.2f}%")
    print(f"  Status: {'✅ Working' if ngram_sim > 0.3 else '❌ Issue detected'}")
    
    # Fuzzy Matching Test
    print("\n📊 Fuzzy Matching Test:")
    fuzzy = FuzzyMatchingAnalyzer()
    fuzzy_sim = fuzzy.weighted_ratio(test_text1, test_text2)
    print(f"  Similarity: {fuzzy_sim:.2f}%")
    print(f"  Status: {'✅ Working' if fuzzy_sim > 70 else '❌ Issue detected'}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("\n🚀 Starting Plagiarism Detection System Evaluation...\n")
    
    # Test individual components first
    try:
        test_individual_components()
    except Exception as e:
        print(f"\n❌ Component test failed: {e}")
        sys.exit(1)
    
    # Run full evaluation
    try:
        evaluator = PlagiarismEvaluator()
        evaluator.run_evaluation()
        
        # Exit with appropriate code
        passed = sum(1 for r in evaluator.results if r["passed"])
        if passed == len(evaluator.results):
            print("\n✅ All tests passed successfully!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {len(evaluator.results) - passed} test(s) failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
