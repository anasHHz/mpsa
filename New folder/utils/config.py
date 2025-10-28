# src/utils/config.py
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ScrapingConfig:
    RATE_LIMIT_DELAY: float = 1.0
    MAX_REVIEWS_PER_SOURCE: int = 1000
    USER_AGENT: str = "Business-Strategy-Analyst/1.0 (Educational Project)"
    RESPECT_ROBOTS_TXT: bool = True

@dataclass
class AnalysisConfig:
    SENTIMENT_THRESHOLDS: Dict[str, float] = None
    TOPIC_MODEL_PARAMS: Dict = None
    
    def __post_init__(self):
        if self.SENTIMENT_THRESHOLDS is None:
            self.SENTIMENT_THRESHOLDS = {
                'positive': 0.05,
                'negative': -0.05
            }
        if self.TOPIC_MODEL_PARAMS is None:
            self.TOPIC_MODEL_PARAMS = {
                'n_components': 10,
                'random_state': 42
            }

class PlatformConfig:
    SUPPORTED_PLATFORMS = ['google_play', 'app_store', 'amazon', 'reddit']