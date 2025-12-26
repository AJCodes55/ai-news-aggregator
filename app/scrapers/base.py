from datetime import datetime, timezone
from typing import List, Optional
from abc import ABC, abstractmethod
import feedparser
from pydantic import BaseModel


class Article(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class BaseScraper(ABC):
    @property
    @abstractmethod
    def rss_urls(self) -> List[str]:
        """Return a list of RSS feed URLs to scrape"""
        pass

    def get_articles(self, hours: int = 24) -> List[Article]:
        """
        Fetch articles from all configured RSS feeds.
        Only returns articles from the last N hours.
        
        Args:
            hours: Number of hours to look back for articles (default: 24)
            
        Returns:
            List of Article objects filtered to last N hours
        """
        now = datetime.now(timezone.utc)
        cutoff_time = now.timestamp() - (hours * 3600)
        articles = []
        seen_guids = set()
        
        for rss_url in self.rss_urls:
            try:
                feed = feedparser.parse(rss_url)
                
                if not feed.entries:
                    continue
                
                for entry in feed.entries:
                    published_parsed = getattr(entry, "published_parsed", None)
                    if not published_parsed:
                        # Try other date fields
                        published_parsed = getattr(entry, "updated_parsed", None)
                    
                    if not published_parsed:
                        continue
                    
                    # Parse the datetime from the parsed tuple
                    try:
                        published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                    except (TypeError, ValueError):
                        # Skip entries with invalid date format
                        continue
                    
                    # Only include articles from the last N hours
                    if published_time.timestamp() >= cutoff_time:
                        guid = entry.get("id", entry.get("link", ""))
                        if guid not in seen_guids:
                            seen_guids.add(guid)
                            articles.append(Article(
                                title=entry.get("title", ""),
                                description=entry.get("description", entry.get("summary", "")),
                                url=entry.get("link", ""),
                                guid=guid,
                                published_at=published_time,
                                category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                            ))
            except Exception:
                # Skip failed feeds
                continue
        
        return articles
