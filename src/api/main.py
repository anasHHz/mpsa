"""
FastAPI REST API for Amazon Market Sentiment Analysis
Provides programmatic access to sentiment analysis and topic modeling
"""
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer
from src.nlp_analysis.topic_modeler import TopicModeler
from src.utils.config import AnalysisConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instances
sentiment_analyzer: Optional[FinBertSentimentAnalyzer] = None
topic_modeler: Optional[TopicModeler] = None


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup
    logger.info("Starting up MPSA API server...")
    global sentiment_analyzer, topic_modeler
    try:
        sentiment_analyzer = FinBertSentimentAnalyzer()
        topic_modeler = TopicModeler(n_topics=5)
        logger.info("Models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down MPSA API server...")


# Initialize FastAPI app
app = FastAPI(
    title="Amazon Market Sentiment Analysis API",
    description="REST API for analyzing Amazon customer reviews",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class SentimentRequest(BaseModel):
    """Request model for sentiment analysis"""
    text: str = Field(..., min_length=1, description="Text to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This product is amazing! Highly recommend."
            }
        }


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis"""
    text: str
    sentiment: str
    confidence: float
    probabilities: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This product is amazing!",
                "sentiment": "positive",
                "confidence": 0.95,
                "probabilities": {
                    "positive": 0.95,
                    "negative": 0.03,
                    "neutral": 0.02
                }
            }
        }


class BatchSentimentRequest(BaseModel):
    """Request model for batch sentiment analysis"""
    texts: List[str] = Field(..., min_items=1, description="List of texts to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "Great product!",
                    "Terrible quality.",
                    "It's okay."
                ]
            }
        }


class BatchSentimentResponse(BaseModel):
    """Response model for batch sentiment analysis"""
    count: int
    results: List[SentimentResponse]


class TopicModelingRequest(BaseModel):
    """Request model for topic modeling"""
    documents: List[str] = Field(..., min_items=3, description="Documents to model")
    n_topics: int = Field(5, ge=2, le=20, description="Number of topics to extract")
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    "Document about product quality",
                    "Review of shipping speed",
                    "Customer service feedback"
                ],
                "n_topics": 3
            }
        }


class TopicResponse(BaseModel):
    """Response model for topic information"""
    topic_id: int
    keywords: List[str]
    weight: Optional[float] = None


class TopicModelingResponse(BaseModel):
    """Response model for topic modeling results"""
    n_documents: int
    n_topics: int
    topics: List[TopicResponse]
    document_topics: List[dict]


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "MPSA API is running"
    }


# Sentiment analysis endpoints
@app.post("/sentiment/single", response_model=SentimentResponse, tags=["Sentiment"])
async def analyze_sentiment_single(request: SentimentRequest):
    """
    Analyze sentiment of a single text
    
    - **text**: Text to analyze
    """
    try:
        if not sentiment_analyzer:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        result = sentiment_analyzer.analyze_single(request.text)
        return SentimentResponse(text=request.text, **result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/sentiment/batch", response_model=BatchSentimentResponse, tags=["Sentiment"])
async def analyze_sentiment_batch(request: BatchSentimentRequest):
    """
    Analyze sentiment of multiple texts
    
    - **texts**: List of texts to analyze
    """
    try:
        if not sentiment_analyzer:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        results = sentiment_analyzer.analyze_batch(request.texts)
        response_items = [
            SentimentResponse(text=text, **result)
            for text, result in zip(request.texts, results)
        ]
        
        return BatchSentimentResponse(
            count=len(response_items),
            results=response_items
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing batch: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Topic modeling endpoints
@app.post("/topics/model", response_model=TopicModelingResponse, tags=["Topics"])
async def model_topics(request: TopicModelingRequest):
    """
    Extract topics from documents using LDA
    
    - **documents**: List of documents to model
    - **n_topics**: Number of topics to extract
    """
    try:
        modeler = TopicModeler(n_topics=request.n_topics, random_state=42)
        modeler.fit(request.documents)
        
        topics = modeler.get_topics()
        topic_distributions = modeler.transform(request.documents)
        
        response_topics = [
            TopicResponse(
                topic_id=i,
                keywords=topic['keywords']
            )
            for i, topic in enumerate(topics)
        ]
        
        doc_topics = [
            {
                "document": doc,
                "topics": {
                    f"topic_{i}": dist
                    for i, dist in enumerate(distribution)
                }
            }
            for doc, distribution in zip(request.documents, topic_distributions)
        ]
        
        return TopicModelingResponse(
            n_documents=len(request.documents),
            n_topics=request.n_topics,
            topics=response_topics,
            document_topics=doc_topics
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error modeling topics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Statistics endpoints
@app.post("/analyze/batch-with-topics", tags=["Analysis"])
async def analyze_batch_with_topics(
    request: BatchSentimentRequest,
    n_topics: int = 3
):
    """
    Complete analysis: sentiment + topic modeling
    
    - **texts**: Texts to analyze
    - **n_topics**: Number of topics to extract
    """
    try:
        # Sentiment analysis
        sentiment_results = sentiment_analyzer.analyze_batch(request.texts)
        
        # Topic modeling
        modeler = TopicModeler(n_topics=n_topics, random_state=42)
        modeler.fit(request.texts)
        topics = modeler.get_topics()
        topic_distributions = modeler.transform(request.texts)
        
        # Combine results
        combined_results = []
        for i, (text, sentiment_result, topic_dist) in enumerate(
            zip(request.texts, sentiment_results, topic_distributions)
        ):
            combined_results.append({
                "index": i,
                "text": text,
                "sentiment": sentiment_result["sentiment"],
                "confidence": sentiment_result["confidence"],
                "probabilities": sentiment_result.get("probabilities", {}),
                "topics": {
                    f"topic_{j}": float(dist)
                    for j, dist in enumerate(topic_dist)
                }
            })
        
        return {
            "n_documents": len(request.texts),
            "n_topics": n_topics,
            "extracted_topics": topics,
            "results": combined_results,
            "sentiment_summary": {
                "positive": sum(1 for r in sentiment_results if r["sentiment"] == "positive"),
                "negative": sum(1 for r in sentiment_results if r["sentiment"] == "negative"),
                "neutral": sum(1 for r in sentiment_results if r["sentiment"] == "neutral"),
                "average_confidence": sum(r["confidence"] for r in sentiment_results) / len(sentiment_results)
            }
        }
    
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions"""
    return HTTPException(status_code=400, detail=str(exc))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )