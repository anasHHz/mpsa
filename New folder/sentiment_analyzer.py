# src/nlp_analysis/sentiment_analyzer.py
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from typing import Dict, List, Tuple
import numpy as np

class SentimentAnalyzer:
    def __init__(self, method: str = "vader"):
        self.method = method
        if method == "vader":
            self.analyzer = SentimentIntensityAnalyzer()
        elif method == "transformers":
            self.analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
    def _categorize_sentiment(self, score: float) -> str:
        """Categorize sentiment based on compound score."""
        if score >= 0.05:
            return "positive"
        elif score <= -0.05:
            return "negative"
        else:
            return "neutral"
    def analyze_text(self, text: str) -> Dict:
        if self.method == "vader":
            scores = self.analyzer.polarity_scores(text)
            # unify key name to 'sentiment_score' for downstream plotting/joins
            return {
                'sentiment_score': scores['compound'],
                'sentiment': self._categorize_sentiment(scores['compound'])
            }
        else:
            result = self.analyzer(text)[0]
            # map transformer labels to a signed numeric score for consistency
            label = result.get('label', '').upper()
            score = float(result.get('score', 0.0))
            if label == 'POSITIVE':
                signed_score = score
            elif label == 'NEGATIVE':
                signed_score = -score
            else:
                signed_score = 0.0
            return {
                'sentiment_score': signed_score,
                'label': label,
                'score': score
            }
    
    def analyze_batch(self, texts: List[str]) -> pd.DataFrame:
        results = []
        for text in texts:
            if pd.isna(text) or text.strip() == "":
                continue
            result = self.analyze_text(text)
            # ensure join key matches original DataFrame column name used in main.py/dashboard
            result['review_text'] = text
            results.append(result)
        
        return pd.DataFrame(results)