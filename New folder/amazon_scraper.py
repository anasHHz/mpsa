from .base_scraper import BaseScraper
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time
import random

class AmazonScraper(BaseScraper):
    def __init__(self, config=None):
        super().__init__(config)
        self.base_url = "https://www.amazon.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
        }
    
    def scrape_reviews(self, product_id: str, max_reviews: int = None) -> List[Dict]:
        max_reviews = max_reviews or getattr(self.config, "MAX_REVIEWS_PER_SOURCE", 100)
        
        if not self.check_robots_txt(self.base_url):
            print(f"Scraping not allowed for {self.base_url} according to robots.txt")
            return []
        
        all_reviews = []
        page = 1
        
        try:
            while len(all_reviews) < max_reviews:
                url = f"{self.base_url}/product-reviews/{product_id}/"
                params = {
                    'reviewerType': 'all_reviews',
                    'pageNumber': page,
                    'sortBy': 'recent'
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code != 200:
                    print(f"Failed to fetch page {page}. Status code: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                review_elements = soup.find_all('div', {'data-hook': 'review'})
                
                if not review_elements:
                    print(f"No more reviews found on page {page}")
                    break
                
                for review_element in review_elements:
                    if len(all_reviews) >= max_reviews:
                        break
                    
                    review_data = self._parse_review_element(review_element)
                    if review_data:
                        all_reviews.append(review_data)
                
                print(f"Scraped {len(review_elements)} reviews from page {page}")
                page += 1
                
                # Random delay to be polite and avoid being blocked
                time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            print(f"Error scraping Amazon reviews: {e}")
        
        return all_reviews
    
    def _parse_review_element(self, review_element) -> Dict:
        try:
            # Extract review text
            review_text_element = review_element.find('span', {'data-hook': 'review-body'})
            review_text = review_text_element.get_text(strip=True) if review_text_element else ""
            
            # Extract rating
            rating_element = review_element.find('i', {'data-hook': 'review-star-rating'})
            if not rating_element:
                rating_element = review_element.find('i', {'data-hook': 'cmps-review-star-rating'})
            
            rating_text = rating_element.get_text(strip=True) if rating_element else ""
            score = self._extract_rating_from_text(rating_text)
            
            # Extract user name
            user_name_element = review_element.find('span', class_='a-profile-name')
            user_name = user_name_element.get_text(strip=True) if user_name_element else "Anonymous"
            
            # Extract date
            date_element = review_element.find('span', {'data-hook': 'review-date'})
            date_text = date_element.get_text(strip=True) if date_element else ""
            
            # Extract title
            title_element = review_element.find('a', {'data-hook': 'review-title'})
            title = title_element.get_text(strip=True) if title_element else ""
            
            return {
                "review_text": review_text,
                "score": score,
                "userName": user_name,
                "at": date_text,
                "title": title,
                "source": "amazon"
            }
            
        except Exception as e:
            print(f"Error parsing review element: {e}")
            return None
    
    def _extract_rating_from_text(self, rating_text: str) -> float:
        """Extract numeric rating from Amazon's rating text (e.g., '5.0 out of 5 stars')"""
        try:
            if rating_text:
                # Look for patterns like "5.0 out of 5 stars"
                import re
                match = re.search(r'(\d+\.?\d*) out of 5', rating_text)
                if match:
                    return float(match.group(1))
        except Exception as e:
            print(f"Error extracting rating from text: {e}")
        return None