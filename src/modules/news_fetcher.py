import feedparser # type: ignore
from newspaper import Article # type: ignore
import urllib.parse
import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
import re

def get_bbc_news_content(topic, max_results=5):
    """Fetches news articles from BBC News search and extracts full content."""
    try:
        search_url = f"https://www.bbc.com/search?q={urllib.parse.quote_plus(topic)}"
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        return search_url
    except Exception as e:
        print(f"Error fetching BBC news search: {e}")
        return None


def extract_hrefs(url):
    """Extract article links from BBC search results."""
    if not url:
        return []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        hrefs = [a.get('href') for a in soup.find_all('a') if a.get('href')]

        # Filter hrefs containing "/news/articles/" or "/news/"
        filtered_hrefs = [href for href in hrefs if "/news/" in href and "article" in href.lower()]

        # Prepend "https://www.bbc.com/" to relative links
        full_links = ["https://www.bbc.com" + href if href.startswith("/") else href for href in filtered_hrefs]
        
        # Remove duplicates
        full_links = list(set(full_links))

        return full_links[:10]  # Return max 10 links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []


def extract_paragraphs(url):
    """Extract paragraphs from an article."""
    if not url:
        return ""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all <p> elements and return their text as a single string
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
        content = "\n".join(paragraphs)
        
        return content if content else "[No content extracted]"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return ""


def get_news_content(topic):
    """Main function to fetch news content for a topic."""
    try:
        news_url = get_bbc_news_content(topic)
        if not news_url:
            return []
        
        links = extract_hrefs(news_url)
        
        if not links:
            print(f"No news articles found for {topic}")
            return []
        
        content_list = []  # List to store extracted news content
        
        for link in links[:5]:  # Limit to 5 articles
            information = extract_paragraphs(link)
            if information and len(information) > 50:  # Only add if meaningful content
                content_list.append(information)
        
        return content_list
    except Exception as e:
        print(f"Error in get_news_content: {e}")
        return []
