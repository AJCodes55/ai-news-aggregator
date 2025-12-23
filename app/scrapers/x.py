from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
from docling.document_converter import DocumentConverter
from pydantic import BaseModel


class XPost(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    author: str
    category: Optional[str] = None


class XScraper:
    def __init__(self):
        # Direct RSS feed URLs from rss.app
        self.rss_feeds = {
            "GoogleAI": "https://rss.app/feeds/fCifMnuCaCowLWra.xml",
            "ollama": "https://rss.app/feeds/Q5rW7ItVWp4ku2hB.xml",
            "NVIDIAAI": "https://rss.app/feeds/yi4TN3YdV6cdfaRy.xml",
            "AIatMeta": "https://rss.app/feeds/6tUN75HYDHwtfszj.xml",
            "GoogleDeepMind": "https://rss.app/feeds/XUhcVCEsFbmpnTjs.xml",
        }
        self.converter = DocumentConverter()

    def get_posts(self, hours: int = 24) -> List[XPost]:
        """
        Fetch posts from all configured X.com accounts.
        Only returns posts from the last 24 hours.
        
        Args:
            hours: Number of hours to look back for posts (default: 24)
            
        Returns:
            List of XPost objects filtered to last 24 hours
        """
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        posts = []
        seen_guids = set()
        
        for author, rss_url in self.rss_feeds.items():
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
                    
                    published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                    
                    # Only include posts from the last 24 hours
                    if published_time >= cutoff_time:
                        guid = entry.get("id", entry.get("link", ""))
                        if guid not in seen_guids:
                            seen_guids.add(guid)
                            # Extract post content from title or description
                            title = entry.get("title", "")
                            description = entry.get("description", entry.get("summary", ""))
                            
                            posts.append(XPost(
                                title=title,
                                description=description,
                                url=entry.get("link", ""),
                                guid=guid,
                                published_at=published_time,
                                author=author,
                                category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                            ))
                        
            except Exception as e:
                print(f"Error fetching posts for {author}: {type(e).__name__} - {e}")
                continue
        
        return posts

    def url_to_markdown(self, url: str) -> Optional[str]:
        """
        Convert a X.com post URL to markdown using DocumentConverter.
        
        Args:
            url: URL of the X.com post
            
        Returns:
            Markdown content as string, or None if conversion fails
        """
        try:
            result = self.converter.convert(url)
            return result.document.export_to_markdown()
        except Exception:
            return None


if __name__ == "__main__":
    scraper = XScraper()
    print("Starting X.com scraper...")
    print("="*60)
    
    posts: List[XPost] = scraper.get_posts(hours=24)
    
    print("="*60)
    print(f"Found {len(posts)} posts in the last 24 hours")
    
    if posts:
        print("\nSample posts:")
        for post in posts[:5]:
            print(f"\n@{post.author}: {post.title}")
            print(f"  URL: {post.url}")
            print(f"  Published: {post.published_at}")
            if post.description:
                preview = post.description[:150] + "..." if len(post.description) > 150 else post.description
                print(f"  Preview: {preview}")
    else:
        print("\nNo posts found in the last 24 hours.")