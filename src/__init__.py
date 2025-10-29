"""
Amazon Market Sentiment Analysis Package (MPSA)

Main package for competitive intelligence and sentiment analysis of Amazon reviews.
"""

__version__ = "1.0.0"
__author__ = "Business Intelligence Team"

from src.data_acquisition.amazon_scraper_amzpy import AmazonScraperAmzPy
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer
from src.nlp_analysis.topic_modeler import TopicModeler
from src.visualization.dashboards import BusinessIntelligenceDashboard
from src.utils.config import (
    ScrapingConfig,
    AnalysisConfig,
    PlatformConfig,
    LoggingConfig
)

__all__ = [
    'AmazonScraperAmzPy',
    'FinBertSentimentAnalyzer',
    'TopicModeler',
    'BusinessIntelligenceDashboard',
    'ScrapingConfig',
    'AnalysisConfig',
    'PlatformConfig',
    'LoggingConfig',
]