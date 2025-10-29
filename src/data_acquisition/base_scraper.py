"""
Base Scraper Module - Abstract Base Class
Provides common scraping functionality and ethical guidelines
"""
import time
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from ..utils.config import ScrapingConfig
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for web scrapers.
    
    Implements common functionality including:
    - Rate limiting to respect server resources
    - robots.txt compliance checking
    - Session management with proper headers
    """
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        """
        Initialize the base scraper.
        
        Args:
            config: ScrapingConfig instance (uses default if None)
        """
        self.config = config or ScrapingConfig()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.config.USER_AGENT})
        logger.info(f"Initialized BaseScraper with User-Agent: {self.config.USER_AGENT}")
    
    def check_robots_txt(self, base_url: str) -> bool:
        """
        Check if scraping is allowed by robots.txt.
        
        Args:
            base_url: Base URL to check robots.txt for
            
        Returns:
            True if scraping is allowed, False otherwise
        """
        if not self.config.RESPECT_ROBOTS_TXT:
            logger.debug(f"Skipping robots.txt check (RESPECT_ROBOTS_TXT=False)")
            return True
        
        try:
            parser = RobotFileParser()
            parser.set_url(f"{base_url}/robots.txt")
            parser.read()
            allowed = parser.can_fetch(self.config.USER_AGENT, base_url)
            logger.info(f"robots.txt check for {base_url}: {'allowed' if allowed else 'denied'}")
            return allowed
        except Exception as e:
            logger.warning(f"Error checking robots.txt: {e}")
            return True  # Default to allowing if we can't check
    
    @abstractmethod
    def scrape_reviews(
        self, 
        product_identifier: str, 
        max_reviews: int = None
    ) -> List[Dict]:
        """
        Abstract method to be implemented by subclasses.
        
        Args:
            product_identifier: Identifier for the product to scrape
            max_reviews: Maximum number of reviews to retrieve
            
        Returns:
            List of review dictionaries
        """
        pass
    
    def rate_limit(self):
        """
        Implement rate limiting to respect server resources.
        
        Uses the configured RATE_LIMIT_DELAY to space out requests.
        """
        time.sleep(self.config.RATE_LIMIT_DELAY)
        logger.debug(f"Rate limit applied: {self.config.RATE_LIMIT_DELAY}s delay")