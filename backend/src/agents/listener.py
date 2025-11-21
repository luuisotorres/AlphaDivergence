import os
import random
import time
import praw
import requests
from dotenv import load_dotenv
from src.services.llm import LLMService
from src.utils.logger import get_logger
from src.utils.security import sanitize_error_message

load_dotenv()
logger = get_logger(__name__)

class ListenerAgent:
    def __init__(self, reddit_client_id: str = None, reddit_client_secret: str = None, 
                 reddit_user_agent: str = None, openai_key: str = None, gemini_key: str = None):
        self.name = "The Listener"
        self.llm = LLMService(openai_key=openai_key, gemini_key=gemini_key)
        
        # Initialize Reddit - Priority: Passed credentials → Environment variables
        self.reddit = None
        reddit_client_id = reddit_client_id or os.getenv("REDDIT_CLIENT_ID")
        reddit_client_secret = reddit_client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        reddit_user_agent = reddit_user_agent or os.getenv("REDDIT_USER_AGENT", "AlphaDivergence/1.0")
        
        if reddit_client_id and reddit_client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    user_agent=reddit_user_agent
                )
            except Exception as e:
                sanitized_error = sanitize_error_message(e, [reddit_client_id, reddit_client_secret])
                logger.error(f"[{self.name}] Failed to initialize Reddit: {sanitized_error}")

    def _fetch_reddit_rss(self, token_symbol: str):
        """
        Fetches Reddit posts via public RSS feeds (No API Key required).
        """
        logger.info(f"[{self.name}] Fetching Reddit via RSS (Fallback Mode)...")
        
        # We'll search a combined feed of relevant subreddits
        subreddits = "CryptoMoonShots+SatoshiStreetBets+Cryptocurrency+Solana+ethtrader+defi+altcoin+memecoin+basechain+bnb"
        rss_url = f"https://www.reddit.com/r/{subreddits}/search.rss?q={token_symbol}&restrict_sr=1&sort=new&limit=10"
        
        try:
            # User-Agent is required by Reddit even for RSS
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(rss_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"[{self.name}] RSS Fetch Failed: {response.status_code}")
                return None

            # Simple XML parsing (avoiding heavy xml libraries if possible, but xml.etree is stdlib)
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            posts = []
            # Reddit RSS uses Atom format usually
            # Namespace map might be needed, but let's try simple tag search
            # Atom namespace: {http://www.w3.org/2005/Atom}
            
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text
                link = entry.find('atom:link', ns).attrib.get('href')
                # RSS doesn't give score easily in the standard fields, sometimes in content
                # We'll assume a base score for visibility
                
                posts.append({
                    "title": title,
                    "url": link,
                    "score": 10, # Placeholder as RSS doesn't guarantee score
                    "selftext": "" # RSS content is HTML, skipping for now to keep it simple
                })
                
            return posts

        except Exception as e:
            logger.error(f"[{self.name}] Error parsing RSS: {e}")
            return None

    def _fetch_reddit_sentiment(self, token_symbol: str):
        """Fetches real posts from Reddit and analyzes sentiment using LLM."""
        
        posts_to_analyze = []
        
        # Try API first
        if self.reddit:
            logger.info(f"[{self.name}] Searching Reddit (API) for ${token_symbol}...")
            subreddits = [
                "CryptoMoonShots", "SatoshiStreetBets", "Cryptocurrency", "Solana",
                "ethtrader", "defi", "altcoin", "memecoin", "basechain", "bnb"
            ]
            try:
                subreddit_str = "+".join(subreddits)
                for submission in self.reddit.subreddit(subreddit_str).search(token_symbol, limit=10, time_filter="week"):
                    posts_to_analyze.append({
                        "title": submission.title,
                        "url": submission.url,
                        "score": submission.score,
                        "selftext": submission.selftext
                    })
            except Exception as e:
                logger.error(f"[{self.name}] Reddit API Error: {e}")
        
        # Fallback to RSS if API failed or not configured
        if not posts_to_analyze:
            rss_posts = self._fetch_reddit_rss(token_symbol)
            if rss_posts:
                posts_to_analyze = rss_posts

        if not posts_to_analyze:
            logger.warning(f"[{self.name}] No Reddit posts found (API & RSS failed).")
            return {
                "posts": 0,
                "upvotes": 0,
                "sentiment_score": 0.5,
                "top_posts": []
            }

        total_upvotes = 0
        sentiment_scores = []
        top_posts_data = []

        for post in posts_to_analyze:
            total_upvotes += post["score"]
            
            # Analyze sentiment
            text_content = f"{post['title']} {post.get('selftext', '')[:200]}"
            analysis = self.llm.analyze_sentiment(text_content)
            sentiment_scores.append(analysis.get("sentiment_score", 0.5))
            
            top_posts_data.append({
                "title": post["title"],
                "url": post["url"],
                "score": post["score"],
                "sentiment": analysis.get("sentiment_label", "Neutral")
            })

        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5

        return {
            "posts": len(posts_to_analyze),
            "upvotes": total_upvotes,
            "sentiment_score": avg_sentiment,
            "top_posts": top_posts_data
        }

    def analyze_sentiment(self, token_symbol: str):
        """
        Aggregates sentiment from social sources (Reddit) and calculates a hype score.
        """
        logger.info(f"[{self.name}] Starting analysis for {token_symbol}...")
        
        reddit_data = self._fetch_reddit_sentiment(token_symbol)

        # Calculate Hype Score based on Reddit only
        # If we have real Reddit data, weight it heavily
        if reddit_data["posts"] > 0:
            # Simple formula: Upvotes + Posts * 10
            raw_score = (reddit_data["upvotes"] * 2) + (reddit_data["posts"] * 20)
        else:
            # Fallback/Low signal
            raw_score = 0

        normalized_score = min(100, max(0, raw_score))
        
        # Adjust by sentiment
        final_hype_score = int(normalized_score * reddit_data["sentiment_score"])

        trending_volume = "Low"
        if final_hype_score > 80:
            trending_volume = "High"
        elif final_hype_score > 40:
            trending_volume = "Medium"

        return {
            "token": token_symbol,
            "hype_score": final_hype_score,
            "trending_volume": trending_volume,
            "details": {
                "reddit_data": reddit_data
            }
        }
