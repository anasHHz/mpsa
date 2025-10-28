# src/data_acquisition/base_scraper.py
import time
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from ..utils.config import ScrapingConfig

class BaseScraper(ABC):
    def __init__(self, config: ScrapingConfig = None):
        self.config = config or ScrapingConfig()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.config.USER_AGENT})
    
    def check_robots_txt(self, base_url: str) -> bool:
        """Check robots.txt before scraping"""
        if not self.config.RESPECT_ROBOTS_TXT:
            return True
            
        parser = RobotFileParser()
        parser.set_url(f"{base_url}/robots.txt")
        parser.read()
        return parser.can_fetch(self.config.USER_AGENT, base_url)
    
    @abstractmethod
    def scrape_reviews(self, product_identifier: str, max_reviews: int = None) -> List[Dict]:
        pass
    
    def rate_limit(self):
        """Respect rate limiting"""
        time.sleep(self.config.RATE_LIMIT_DELAY)