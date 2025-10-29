"""
Sentiment Analysis Module - FinBERT Implementation
Provides accurate sentiment classification for financial/business text
"""
import pandas as pd
from typing import List, Dict, Optional, Tuple
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class FinBertSentimentAnalyzer:
    """
    FinBERT-based sentiment analyzer optimized for financial and business reviews.
    
    Uses the pre-trained FinBERT model from Hugging Face for accurate sentiment
    classification with confidence scores.
    """
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize the FinBERT sentiment analyzer.
        
        Args:
            model_name: Hugging Face model identifier for FinBERT
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        self.labels = ['negative', 'neutral', 'positive']
    
    def analyze_single(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores and label
        """
        if not text or not isinstance(text, str) or len(text.strip()) == 0:
            return {
                'sentiment_label': 'neutral',
                'sentiment_score': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'positive': 0.0,
                'confidence': 1.0
            }
        
        try:
            inputs = self.tokenizer(
                text[:512],  # FinBERT max length
                return_tensors='pt',
                truncation=True,
                max_length=512
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)[0].cpu().numpy()
            
            label_idx = np.argmax(probabilities)
            label = self.labels[label_idx]
            
            # Calculate sentiment score: positive(+1) vs negative(-1)
            sentiment_score = float(probabilities[2] - probabilities[0])
            
            return {
                'sentiment_label': label,
                'sentiment_score': sentiment_score,
                'negative': float(probabilities[0]),
                'neutral': float(probabilities[1]),
                'positive': float(probabilities[2]),
                'confidence': float(probabilities[label_idx])
            }
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {
                'sentiment_label': 'neutral',
                'sentiment_score': 0.0,
                'negative': 0.33,
                'neutral': 0.34,
                'positive': 0.33,
                'confidence': 0.0
            }
    
    def analyze_batch(self, texts: List[str], batch_size: int = 32) -> pd.DataFrame:
        """
        Analyze sentiment for multiple texts efficiently.
        
        Args:
            texts: List of texts to analyze
            batch_size: Number of texts to process at once
            
        Returns:
            DataFrame with sentiment analysis results
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                result = self.analyze_single(text)
                result['review_text'] = text
                results.append(result)
        
        return pd.DataFrame(results)
