"""
Configuration Module - Centralized Settings
Contains configuration classes for scraping, analysis, and platform settings
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScrapingConfig:
    """
    Configuration for web scraping behavior.
    
    Attributes:
        RATE_LIMIT_DELAY: Seconds to wait between requests (respects server resources)
        MAX_REVIEWS_PER_SOURCE: Maximum reviews to retrieve per source
        USER_AGENT: HTTP User-Agent header value
        RESPECT_ROBOTS_TXT: Whether to check robots.txt before scraping
        REQUEST_TIMEOUT: Timeout in seconds for HTTP requests
        RETRIES: Number of retries for failed requests
    """
    RATE_LIMIT_DELAY: float = 1.0
    MAX_REVIEWS_PER_SOURCE: int = 1000
    USER_AGENT: str = "Business-Strategy-Analyst/1.0 (Educational Project)"
    RESPECT_ROBOTS_TXT: bool = True
    REQUEST_TIMEOUT: int = 30
    RETRIES: int = 3


@dataclass
class AnalysisConfig:
    """
    Configuration for NLP analysis models.
    
    Attributes:
        SENTIMENT_THRESHOLDS: Thresholds for positive/negative classification
        TOPIC_MODEL_PARAMS: Parameters for LDA topic modeling
        FINBERT_MODEL: HuggingFace model ID for FinBERT
    """
    SENTIMENT_THRESHOLDS: Optional[Dict[str, float]] = None
    TOPIC_MODEL_PARAMS: Optional[Dict] = None
    FINBERT_MODEL: str = "ProsusAI/finbert"
    
    def __post_init__(self):
        """Initialize default values for optional fields"""
        if self.SENTIMENT_THRESHOLDS is None:
            self.SENTIMENT_THRESHOLDS = {
                'positive': 0.05,
                'negative': -0.05
            }
        if self.TOPIC_MODEL_PARAMS is None:
            self.TOPIC_MODEL_PARAMS = {
                'n_components': 10,
                'random_state': 42,
                'max_iter': 10
            }


class PlatformConfig:
    """
    Configuration for supported platforms.
    
    This is extensible for future platform additions.
    """
    SUPPORTED_PLATFORMS = ['google_play', 'app_store', 'amazon', 'reddit']
    
    PLATFORM_URLS = {
        'amazon': {
            'in': 'https://www.amazon.in',
            'com': 'https://www.amazon.com',
            'co.uk': 'https://www.amazon.co.uk',
            'de': 'https://www.amazon.de',
            'fr': 'https://www.amazon.fr',
        }
    }
    
    @classmethod
    def get_amazon_url(cls, country_code: str) -> str:
        """Get Amazon URL for a specific country code"""
        url = cls.PLATFORM_URLS['amazon'].get(country_code.lower())
        if not url:
            raise ValueError(f"Unsupported country code: {country_code}")
        return url


class LoggingConfig:
    """Configuration for application logging"""
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'mpsa.log')


# Export default configurations
DEFAULT_SCRAPING_CONFIG = ScrapingConfig()
DEFAULT_ANALYSIS_CONFIG = AnalysisConfig()
DEFAULT_LOGGING_CONFIG = LoggingConfig()