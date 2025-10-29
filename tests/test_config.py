"""
Unit tests for configuration module
Tests all configuration classes and methods
"""
import pytest
from src.utils.config import (
    ScrapingConfig, AnalysisConfig, PlatformConfig, 
    LoggingConfig, get_amazon_url
)


class TestScrapingConfig:
    """Test suite for ScrapingConfig"""

    def test_scraping_config_initialization(self):
        """Test that ScrapingConfig initializes with correct defaults"""
        config = ScrapingConfig()
        
        assert config.USER_AGENT is not None
        assert isinstance(config.USER_AGENT, str)
        assert config.REQUEST_TIMEOUT > 0
        assert config.RETRIES >= 0

    def test_scraping_config_custom_values(self):
        """Test ScrapingConfig with custom values"""
        config = ScrapingConfig(
            USER_AGENT="CustomAgent/1.0",
            REQUEST_TIMEOUT=30,
            RETRIES=5
        )
        
        assert config.USER_AGENT == "CustomAgent/1.0"
        assert config.REQUEST_TIMEOUT == 30
        assert config.RETRIES == 5


class TestAnalysisConfig:
    """Test suite for AnalysisConfig"""

    def test_analysis_config_initialization(self):
        """Test that AnalysisConfig initializes correctly"""
        config = AnalysisConfig()
        
        assert config.MAX_REVIEWS > 0
        assert config.MIN_REVIEWS >= 0
        assert config.LANGUAGE == "en"
        assert config.FINBERT_MODEL is not None

    def test_analysis_config_custom_values(self):
        """Test AnalysisConfig with custom values"""
        config = AnalysisConfig(
            MAX_REVIEWS=500,
            MIN_REVIEWS=10,
            LANGUAGE="es"
        )
        
        assert config.MAX_REVIEWS == 500
        assert config.MIN_REVIEWS == 10
        assert config.LANGUAGE == "es"

    def test_analysis_config_finbert_model(self):
        """Test that FinBERT model is properly configured"""
        config = AnalysisConfig()
        
        assert "finbert" in config.FINBERT_MODEL.lower()


class TestPlatformConfig:
    """Test suite for PlatformConfig"""

    def test_platform_config_initialization(self):
        """Test that PlatformConfig initializes correctly"""
        config = PlatformConfig()
        
        assert hasattr(config, 'AMAZON_URLS')
        assert isinstance(config.AMAZON_URLS, dict)

    def test_amazon_urls_structure(self):
        """Test that AMAZON_URLS has expected structure"""
        config = PlatformConfig()
        
        # Should have entries for different regions
        assert len(config.AMAZON_URLS) > 0
        assert all(isinstance(url, str) for url in config.AMAZON_URLS.values())

    def test_get_amazon_url_valid_platform(self):
        """Test get_amazon_url with valid platform"""
        url = get_amazon_url("com")
        
        assert url is not None
        assert isinstance(url, str)
        assert "amazon" in url.lower()

    def test_get_amazon_url_default_platform(self):
        """Test get_amazon_url with default platform"""
        url = get_amazon_url()
        
        assert url is not None
        assert isinstance(url, str)

    def test_get_amazon_url_invalid_platform(self):
        """Test get_amazon_url with invalid platform"""
        # Should either return default or raise appropriate error
        try:
            url = get_amazon_url("invalid_platform")
            assert url is not None
        except (KeyError, ValueError):
            pass  # Expected behavior


class TestLoggingConfig:
    """Test suite for LoggingConfig"""

    def test_logging_config_initialization(self):
        """Test that LoggingConfig initializes correctly"""
        config = LoggingConfig()
        
        assert config.LOG_LEVEL is not None
        assert config.LOG_FILE is not None
        assert config.LOG_FORMAT is not None

    def test_logging_config_valid_log_level(self):
        """Test that LOG_LEVEL is a valid logging level"""
        config = LoggingConfig()
        
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert config.LOG_LEVEL in valid_levels

    def test_logging_config_custom_values(self):
        """Test LoggingConfig with custom values"""
        config = LoggingConfig(
            LOG_LEVEL="DEBUG",
            LOG_FILE="custom.log"
        )
        
        assert config.LOG_LEVEL == "DEBUG"
        assert config.LOG_FILE == "custom.log"

    def test_logging_format_is_string(self):
        """Test that log format is properly configured"""
        config = LoggingConfig()
        
        assert isinstance(config.LOG_FORMAT, str)
        assert len(config.LOG_FORMAT) > 0


class TestConfigIntegration:
    """Integration tests for configuration module"""

    def test_all_configs_can_be_instantiated(self):
        """Test that all config classes can be instantiated"""
        scraping = ScrapingConfig()
        analysis = AnalysisConfig()
        platform = PlatformConfig()
        logging_config = LoggingConfig()
        
        assert scraping is not None
        assert analysis is not None
        assert platform is not None
        assert logging_config is not None

    def test_configs_are_independent(self):
        """Test that modifying one config doesn't affect others"""
        config1 = ScrapingConfig(REQUEST_TIMEOUT=10)
        config2 = ScrapingConfig(REQUEST_TIMEOUT=20)
        
        assert config1.REQUEST_TIMEOUT == 10
        assert config2.REQUEST_TIMEOUT == 20

    def test_analysis_config_constraints(self):
        """Test that AnalysisConfig enforces logical constraints"""
        config = AnalysisConfig()
        
        # MIN_REVIEWS should typically be less than MAX_REVIEWS
        assert config.MIN_REVIEWS <= config.MAX_REVIEWS