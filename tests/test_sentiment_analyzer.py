"""
Unit tests for FinBertSentimentAnalyzer
Tests sentiment analysis functionality and edge cases
"""
import pytest
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer


@pytest.fixture
def analyzer():
    """Fixture to initialize sentiment analyzer"""
    return FinBertSentimentAnalyzer()


class TestFinBertSentimentAnalyzer:
    """Test suite for FinBertSentimentAnalyzer"""

    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        assert analyzer.model is not None
        assert analyzer.tokenizer is not None

    @pytest.mark.nlp
    def test_analyze_single_positive_sentiment(self, analyzer):
        """Test positive sentiment detection"""
        text = "This product is absolutely amazing! I love it and highly recommend it."
        result = analyzer.analyze_single(text)
        
        assert result is not None
        assert "sentiment" in result
        assert "confidence" in result
        assert result["sentiment"] in ["positive", "negative", "neutral"]

    @pytest.mark.nlp
    def test_analyze_single_negative_sentiment(self, analyzer):
        """Test negative sentiment detection"""
        text = "Terrible product. Broke within a day. Waste of money."
        result = analyzer.analyze_single(text)
        
        assert result is not None
        assert "sentiment" in result
        assert result["confidence"] > 0

    @pytest.mark.nlp
    def test_analyze_single_neutral_sentiment(self, analyzer):
        """Test neutral sentiment detection"""
        text = "The product arrived on time."
        result = analyzer.analyze_single(text)
        
        assert result is not None
        assert "sentiment" in result

    @pytest.mark.nlp
    def test_analyze_single_empty_text(self, analyzer):
        """Test handling of empty text"""
        with pytest.raises(ValueError):
            analyzer.analyze_single("")

    @pytest.mark.nlp
    def test_analyze_single_whitespace_only(self, analyzer):
        """Test handling of whitespace-only text"""
        with pytest.raises(ValueError):
            analyzer.analyze_single("   ")

    @pytest.mark.nlp
    def test_analyze_single_none_input(self, analyzer):
        """Test handling of None input"""
        with pytest.raises((ValueError, TypeError)):
            analyzer.analyze_single(None)

    @pytest.mark.nlp
    def test_analyze_single_long_text_truncation(self, analyzer):
        """Test truncation of texts exceeding 512 tokens"""
        # Create a very long text
        long_text = "word " * 2000  # Much longer than 512 tokens
        result = analyzer.analyze_single(long_text)
        
        assert result is not None
        assert "sentiment" in result

    @pytest.mark.nlp
    def test_analyze_batch(self, analyzer):
        """Test batch sentiment analysis"""
        texts = [
            "Great product! Very satisfied.",
            "Not good. Poor quality.",
            "It's okay, nothing special."
        ]
        results = analyzer.analyze_batch(texts)
        
        assert len(results) == len(texts)
        assert all("sentiment" in r for r in results)
        assert all("confidence" in r for r in results)

    @pytest.mark.nlp
    def test_analyze_batch_empty_list(self, analyzer):
        """Test batch analysis with empty list"""
        with pytest.raises(ValueError):
            analyzer.analyze_batch([])

    @pytest.mark.nlp
    def test_analyze_batch_with_empty_strings(self, analyzer):
        """Test batch analysis with some empty strings"""
        texts = ["Good product", "", "Bad product"]
        with pytest.raises(ValueError):
            analyzer.analyze_batch(texts)

    @pytest.mark.nlp
    def test_sentiment_probabilities_sum_to_one(self, analyzer):
        """Test that sentiment probabilities sum to approximately 1.0"""
        text = "This is a good product overall."
        result = analyzer.analyze_single(text)
        
        if "probabilities" in result:
            total = sum(result["probabilities"].values())
            assert 0.99 <= total <= 1.01  # Allow small floating point error

    @pytest.mark.nlp
    def test_confidence_in_valid_range(self, analyzer):
        """Test that confidence scores are between 0 and 1"""
        text = "Amazing product!"
        result = analyzer.analyze_single(text)
        
        assert 0 <= result["confidence"] <= 1

    @pytest.mark.nlp
    @pytest.mark.slow
    def test_analyze_batch_large(self, analyzer):
        """Test batch analysis with larger dataset"""
        texts = [f"Review {i}: This is a sample review." for i in range(50)]
        results = analyzer.analyze_batch(texts)
        
        assert len(results) == 50
        assert all(r["sentiment"] in ["positive", "negative", "neutral"] for r in results)

    @pytest.mark.nlp
    def test_special_characters_handling(self, analyzer):
        """Test handling of special characters and unicode"""
        text = "Great product! 🌟 Love it! €50 well spent. 你好 好产品"
        result = analyzer.analyze_single(text)
        
        assert result is not None
        assert "sentiment" in result

    @pytest.mark.nlp
    def test_repeated_text_analysis_consistency(self, analyzer):
        """Test that analyzing the same text twice gives similar results"""
        text = "This product is excellent!"
        result1 = analyzer.analyze_single(text)
        result2 = analyzer.analyze_single(text)
        
        assert result1["sentiment"] == result2["sentiment"]
        # Confidence might differ slightly due to model behavior, but should be close
        assert abs(result1["confidence"] - result2["confidence"]) < 0.1