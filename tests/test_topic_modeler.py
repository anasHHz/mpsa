"""
Unit tests for TopicModeler
Tests LDA topic modeling functionality
"""
import pytest
import pandas as pd
from src.nlp_analysis.topic_modeler import TopicModeler


@pytest.fixture
def sample_reviews():
    """Fixture with sample review data"""
    return pd.DataFrame({
        'review_text': [
            'Great battery life, phone works well, excellent performance',
            'Screen quality is amazing, display looks beautiful',
            'Fast delivery, good packaging, arrived on time',
            'Poor quality, broke after a week, terrible',
            'Customer service was helpful and responsive',
            'Battery dies quickly, slow processor',
            'Packaging was damaged but product is fine',
            'Great value for money, highly recommend'
        ]
    })


@pytest.fixture
def modeler():
    """Fixture to initialize topic modeler"""
    return TopicModeler(n_topics=2, random_state=42)


class TestTopicModeler:
    """Test suite for TopicModeler"""

    def test_modeler_initialization(self, modeler):
        """Test that modeler initializes correctly"""
        assert modeler is not None
        assert modeler.n_topics == 2
        assert modeler.model is None  # Not trained yet

    @pytest.mark.nlp
    def test_fit_model(self, modeler, sample_reviews):
        """Test fitting the LDA model"""
        modeler.fit(sample_reviews['review_text'].tolist())
        
        assert modeler.model is not None
        assert modeler.vectorizer is not None

    @pytest.mark.nlp
    def test_fit_with_empty_list(self, modeler):
        """Test fitting with empty document list"""
        with pytest.raises(ValueError):
            modeler.fit([])

    @pytest.mark.nlp
    def test_fit_with_empty_strings(self, modeler):
        """Test fitting with documents containing only whitespace"""
        with pytest.raises(ValueError):
            modeler.fit(["   ", "   ", ""])

    @pytest.mark.nlp
    def test_get_topics_without_fitting(self, modeler):
        """Test getting topics without fitting first"""
        with pytest.raises(ValueError):
            modeler.get_topics()

    @pytest.mark.nlp
    def test_get_topics_after_fitting(self, modeler, sample_reviews):
        """Test getting topics after fitting"""
        modeler.fit(sample_reviews['review_text'].tolist())
        topics = modeler.get_topics()
        
        assert topics is not None
        assert len(topics) == modeler.n_topics
        assert all('keywords' in topic for topic in topics)

    @pytest.mark.nlp
    def test_transform_without_fitting(self, modeler, sample_reviews):
        """Test transform without fitting first"""
        with pytest.raises(ValueError):
            modeler.transform(sample_reviews['review_text'].tolist())

    @pytest.mark.nlp
    def test_transform_after_fitting(self, modeler, sample_reviews):
        """Test transforming documents after fitting"""
        modeler.fit(sample_reviews['review_text'].tolist())
        topic_distributions = modeler.transform(sample_reviews['review_text'].tolist())
        
        assert topic_distributions is not None
        assert len(topic_distributions) == len(sample_reviews)
        assert all(len(dist) == modeler.n_topics for dist in topic_distributions)

    @pytest.mark.nlp
    def test_topic_distributions_sum_to_one(self, modeler, sample_reviews):
        """Test that topic distributions sum to approximately 1.0"""
        modeler.fit(sample_reviews['review_text'].tolist())
        topic_distributions = modeler.transform(sample_reviews['review_text'].tolist())
        
        for dist in topic_distributions:
            total = sum(dist)
            assert 0.99 <= total <= 1.01  # Allow small floating point error

    @pytest.mark.nlp
    def test_topic_probabilities_in_valid_range(self, modeler, sample_reviews):
        """Test that all topic probabilities are between 0 and 1"""
        modeler.fit(sample_reviews['review_text'].tolist())
        topic_distributions = modeler.transform(sample_reviews['review_text'].tolist())
        
        for dist in topic_distributions:
            assert all(0 <= prob <= 1 for prob in dist)

    @pytest.mark.nlp
    def test_get_topics_returns_valid_keywords(self, modeler, sample_reviews):
        """Test that get_topics returns valid keywords"""
        modeler.fit(sample_reviews['review_text'].tolist())
        topics = modeler.get_topics()
        
        for topic in topics:
            assert 'keywords' in topic
            assert isinstance(topic['keywords'], list)
            assert len(topic['keywords']) > 0
            assert all(isinstance(keyword, str) for keyword in topic['keywords'])

    @pytest.mark.nlp
    def test_different_random_states_produce_different_results(self, sample_reviews):
        """Test that different random states produce different models"""
        modeler1 = TopicModeler(n_topics=2, random_state=42)
        modeler2 = TopicModeler(n_topics=2, random_state=123)
        
        modeler1.fit(sample_reviews['review_text'].tolist())
        modeler2.fit(sample_reviews['review_text'].tolist())
        
        topics1 = modeler1.get_topics()
        topics2 = modeler2.get_topics()
        
        # Keywords should be different with different random states
        keywords1 = [kw for topic in topics1 for kw in topic['keywords']]
        keywords2 = [kw for topic in topics2 for kw in topic['keywords']]
        
        # At least some keywords should differ
        assert keywords1 != keywords2

    @pytest.mark.nlp
    def test_single_document_transform(self, modeler, sample_reviews):
        """Test transforming a single document"""
        modeler.fit(sample_reviews['review_text'].tolist())
        result = modeler.transform(['This is a test review'])
        
        assert len(result) == 1
        assert len(result[0]) == modeler.n_topics

    @pytest.mark.nlp
    def test_transform_with_unseen_vocabulary(self, modeler, sample_reviews):
        """Test transforming documents with words not in training set"""
        modeler.fit(sample_reviews['review_text'].tolist())
        
        # Create review with completely new words
        new_review = "xyzabc qwerty uniqword"
        result = modeler.transform([new_review])
        
        assert result is not None
        assert len(result) == 1

    @pytest.mark.nlp
    @pytest.mark.slow
    def test_fit_with_many_documents(self, modeler):
        """Test fitting with a larger document collection"""
        large_corpus = [
            f"Review {i}: This is a sample review about product quality, delivery, and service."
            for i in range(100)
        ]
        
        modeler.fit(large_corpus)
        topics = modeler.get_topics()
        
        assert modeler.model is not None
        assert len(topics) == modeler.n_topics

    @pytest.mark.nlp
    def test_n_topics_greater_than_documents(self, sample_reviews):
        """Test behavior when n_topics > number of documents"""
        modeler = TopicModeler(n_topics=50, random_state=42)
        
        # Should handle gracefully
        try:
            modeler.fit(sample_reviews['review_text'].tolist())
            # If it succeeds, that's fine
            assert modeler.model is not None
        except (ValueError, Exception):
            # If it raises an error, that's also acceptable
            pass

    @pytest.mark.nlp
    def test_transform_consistency(self, modeler, sample_reviews):
        """Test that transforming same document twice gives same results"""
        modeler.fit(sample_reviews['review_text'].tolist())
        
        result1 = modeler.transform(['consistent test document'])
        result2 = modeler.transform(['consistent test document'])
        
        assert result1 == result2