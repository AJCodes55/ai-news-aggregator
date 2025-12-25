from typing import List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import YOUTUBE_CHANNELS
from app.scrapers.youtube import YouTubeScraper, ChannelVideo
from app.scrapers.openai import OpenAIScraper, OpenAIArticle
from app.scrapers.anthropic import AnthropicScraper, AnthropicArticle
from app.scrapers.x import XScraper, XPost
from app.database.repository import Repository


def run_scrapers(hours: int = 24) -> dict:
    youtube_scraper = YouTubeScraper()
    openai_scraper = OpenAIScraper()
    anthropic_scraper = AnthropicScraper()
    x_scraper = XScraper()
    repo = Repository()
    
    youtube_videos = []
    video_dicts = []
    for channel_id in YOUTUBE_CHANNELS:
        videos = youtube_scraper.get_latest_videos(channel_id, hours=hours)
        youtube_videos.extend(videos)
        video_dicts.extend([
            {
                "video_id": v.video_id,
                "title": v.title,
                "url": v.url,
                "channel_id": channel_id,
                "published_at": v.published_at,
                "description": v.description,
                "transcript": v.transcript
            }
            for v in videos
        ])
    
    openai_articles = openai_scraper.get_articles(hours=hours)
    anthropic_articles = anthropic_scraper.get_articles(hours=hours)
    x_posts = x_scraper.get_posts(hours=hours)
    
    if video_dicts:
        repo.bulk_create_youtube_videos(video_dicts)
    
    if openai_articles:
        article_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in openai_articles
        ]
        repo.bulk_create_openai_articles(article_dicts)
    
    if anthropic_articles:
        article_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in anthropic_articles
        ]
        repo.bulk_create_anthropic_articles(article_dicts)
    
    if x_posts:
        post_dicts = [
            {
                "guid": p.guid,
                "title": p.title,
                "url": p.url,
                "published_at": p.published_at,
                "description": p.description,
                "author": p.author,
                "category": p.category
            }
            for p in x_posts
        ]
        repo.bulk_create_x_posts(post_dicts)
    
    return {
        "youtube": youtube_videos,
        "openai": openai_articles,
        "anthropic": anthropic_articles,
        "x": x_posts,
    }


if __name__ == "__main__":
    results = run_scrapers(hours=50)
    print(f"YouTube videos: {len(results['youtube'])}")
    print(f"OpenAI articles: {len(results['openai'])}")
    print(f"Anthropic articles: {len(results['anthropic'])}")
    print(f"X.com posts: {len(results['x'])}")
