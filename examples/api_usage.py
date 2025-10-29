"""
Example scripts for using MPSA REST API

Before running these examples:
1. Start the API server: python api_server.py
2. Or use Docker: docker-compose up
3. API will be available at http://localhost:8000
4. Documentation available at http://localhost:8000/docs

Examples:
- Single sentiment analysis
- Batch sentiment analysis
- Topic modeling
- Combined analysis
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

# Colors for console output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print(f"{text}")
    print(f"{'=' * 60}{Colors.END}\n")


def print_result(result):
    """Pretty print API result"""
    print(Colors.GREEN + json.dumps(result, indent=2) + Colors.END)


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ API is running{Colors.END}")
            print_result(response.json())
            return True
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ API is not running at {BASE_URL}{Colors.END}")
        print("Start it with: python api_server.py")
        return False


def example_single_sentiment():
    """Example 1: Analyze sentiment of a single review"""
    print_header("Example 1: Single Sentiment Analysis")
    
    text = "This product is absolutely amazing! Best purchase ever, highly recommend!"
    
    print(f"Text: {Colors.YELLOW}{text}{Colors.END}\n")
    
    response = requests.post(
        f"{BASE_URL}/sentiment/single",
        json={"text": text}
    )
    
    if response.status_code == 200:
        print("Response:")
        print_result(response.json())
    else:
        print(f"{Colors.RED}Error: {response.status_code}{Colors.END}")
        print(response.json())


def example_batch_sentiment():
    """Example 2: Analyze sentiment of multiple reviews"""
    print_header("Example 2: Batch Sentiment Analysis")
    
    texts = [
        "Great product! Very satisfied with my purchase.",
        "Terrible quality. Broke after one week.",
        "It's okay. Nothing special but does the job.",
        "Excellent customer service and fast shipping!",
        "Waste of money. Total disappointment.",
    ]
    
    print(f"Analyzing {len(texts)} reviews:\n")
    for i, text in enumerate(texts, 1):
        print(f"  {i}. {text}")
    
    print()
    
    response = requests.post(
        f"{BASE_URL}/sentiment/batch",
        json={"texts": texts}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response (batch of {result['count']} reviews):\n")
        
        # Print summary
        positive = sum(1 for r in result['results'] if r['sentiment'] == 'positive')
        negative = sum(1 for r in result['results'] if r['sentiment'] == 'negative')
        neutral = sum(1 for r in result['results'] if r['sentiment'] == 'neutral')
        
        print(f"Summary:")
        print(f"  {Colors.GREEN}Positive: {positive}{Colors.END}")
        print(f"  {Colors.RED}Negative: {negative}{Colors.END}")
        print(f"  {Colors.YELLOW}Neutral: {neutral}{Colors.END}\n")
        
        # Print detailed results
        for i, result in enumerate(result['results'], 1):
            sentiment_icon = {"positive": "✓", "negative": "✗", "neutral": "◇"}
            icon = sentiment_icon.get(result['sentiment'], "?")
            print(f"  {i}. [{icon}] {result['sentiment']} "
                  f"(confidence: {result['confidence']:.2f})")
    else:
        print(f"{Colors.RED}Error: {response.status_code}{Colors.END}")
        print(response.json())


def example_topic_modeling():
    """Example 3: Extract topics from documents"""
    print_header("Example 3: Topic Modeling")
    
    documents = [
        "The battery life is amazing, lasts all day without charging.",
        "Screen display is absolutely beautiful, very bright and clear.",
        "Fast processor, handles everything I throw at it smoothly.",
        "Shipping was incredibly fast, arrived in two days.",
        "Excellent packaging, item arrived in perfect condition.",
        "Customer service was helpful and responsive to my questions.",
        "Disappointing battery performance, drains too quickly.",
        "Slow and sluggish, apps take forever to load.",
        "Screen has dead pixels, very disappointed with quality.",
    ]
    
    print(f"Extracting topics from {len(documents)} documents\n")
    print("Documents:")
    for i, doc in enumerate(documents, 1):
        print(f"  {i}. {doc}")
    
    print()
    
    response = requests.post(
        f"{BASE_URL}/topics/model",
        json={
            "documents": documents,
            "n_topics": 3
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response ({result['n_topics']} topics extracted):\n")
        
        print("Topics:")
        for topic in result['topics']:
            keywords = ", ".join(topic['keywords'][:5])
            print(f"  Topic {topic['topic_id']}: {keywords}")
        
        print("\nDocument-Topic Distribution:")
        for i, doc_topic in enumerate(result['document_topics'], 1):
            topics_str = ", ".join(
                f"Topic {j}: {v:.2f}"
                for j, v in enumerate(doc_topic['topics'].values())
            )
            print(f"  Doc {i}: {topics_str}")
    else:
        print(f"{Colors.RED}Error: {response.status_code}{Colors.END}")
        print(response.json())


def example_combined_analysis():
    """Example 4: Combined sentiment + topic analysis"""
    print_header("Example 4: Combined Analysis (Sentiment + Topics)")
    
    reviews = [
        "Great battery life and excellent build quality!",
        "Terrible screen, fast processor though.",
        "Shipping was quick, good customer service.",
        "Product broke after a week, very disappointed.",
        "Amazing value for money, highly recommend!",
    ]
    
    print(f"Performing combined analysis on {len(reviews)} reviews\n")
    
    response = requests.post(
        f"{BASE_URL}/analyze/batch-with-topics",
        json={"texts": reviews, "n_topics": 2}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response (Topics + Sentiments):\n")
        
        # Print sentiment summary
        summary = result['sentiment_summary']
        print("Sentiment Summary:")
        print(f"  {Colors.GREEN}Positive: {summary['positive']}{Colors.END}")
        print(f"  {Colors.RED}Negative: {summary['negative']}{Colors.END}")
        print(f"  {Colors.YELLOW}Neutral: {summary['neutral']}{Colors.END}")
        print(f"  Average Confidence: {summary['average_confidence']:.2f}\n")
        
        # Print extracted topics
        print("Extracted Topics:")
        for topic in result['extracted_topics']:
            keywords = ", ".join(topic['keywords'][:5])
            print(f"  Topic {topic['topic_id']}: {keywords}")
        
        # Print detailed results
        print("\nDetailed Results:")
        for res in result['results']:
            print(f"\n  Review: {res['text']}")
            print(f"  Sentiment: {res['sentiment']} (confidence: {res['confidence']:.2f})")
            topics = res['topics']
            for topic_name, weight in topics.items():
                print(f"  {topic_name}: {weight:.2f}")
    else:
        print(f"{Colors.RED}Error: {response.status_code}{Colors.END}")
        print(response.json())


def example_error_handling():
    """Example 5: Error handling"""
    print_header("Example 5: Error Handling")
    
    print("Testing various error cases:\n")
    
    # Test 1: Empty text
    print("1. Empty text:")
    response = requests.post(
        f"{BASE_URL}/sentiment/single",
        json={"text": ""}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Message: {response.json()['detail']}\n")
    
    # Test 2: Empty batch
    print("2. Empty batch:")
    response = requests.post(
        f"{BASE_URL}/sentiment/batch",
        json={"texts": []}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Message: {response.json()['detail']}\n")
    
    # Test 3: Invalid topic count
    print("3. Invalid topic count (too many):")
    response = requests.post(
        f"{BASE_URL}/topics/model",
        json={"documents": ["doc1", "doc2"], "n_topics": 50}
    )
    print(f"   Status: {response.status_code}\n")


def example_performance_test():
    """Example 6: Performance testing"""
    print_header("Example 6: Performance Testing")
    
    batch_sizes = [10, 50, 100]
    
    for batch_size in batch_sizes:
        texts = [f"This is review number {i}. It's a great product!" for i in range(batch_size)]
        
        print(f"Testing batch size: {batch_size}")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/sentiment/batch",
            json={"texts": texts}
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            throughput = batch_size / duration
            print(f"  Duration: {duration:.2f}s")
            print(f"  Throughput: {throughput:.1f} reviews/sec\n")
        else:
            print(f"  Error: {response.status_code}\n")


def main():
    """Run all examples"""
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print("MPSA REST API Examples")
    print(f"{'=' * 60}{Colors.END}\n")
    
    # Check API health
    if not check_api_health():
        return
    
    try:
        # Run examples
        example_single_sentiment()
        example_batch_sentiment()
        example_topic_modeling()
        example_combined_analysis()
        example_error_handling()
        example_performance_test()
        
        print_header("All Examples Completed Successfully!")
        print(f"API Documentation: {Colors.YELLOW}{BASE_URL}/docs{Colors.END}")
        print(f"ReDoc: {Colors.YELLOW}{BASE_URL}/redoc{Colors.END}\n")
        
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Request error: {e}{Colors.END}")


if __name__ == "__main__":
    main()