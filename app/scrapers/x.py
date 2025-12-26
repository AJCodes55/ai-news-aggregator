from typing import List, Optional
import requests
from html_to_markdown import convert
from .base import BaseScraper, Article


class XPost(Article):
    author: str


class XScraper(BaseScraper):
    @property
    def rss_urls(self) -> List[str]:
        return [
            "https://rss.app/feeds/fCifMnuCaCowLWra.xml",  # GoogleAI
            "https://rss.app/feeds/Q5rW7ItVWp4ku2hB.xml",  # ollama
            "https://rss.app/feeds/yi4TN3YdV6cdfaRy.xml",  # NVIDIAAI
            "https://rss.app/feeds/6tUN75HYDHwtfszj.xml",  # AIatMeta
            "https://rss.app/feeds/XUhcVCEsFbmpnTjs.xml",  # GoogleDeepMind
        ]

    def get_posts(self, hours: int = 24) -> List[XPost]:
        """
        Fetch posts from all configured X.com accounts.
        Only returns posts from the last 24 hours.
        
        Args:
            hours: Number of hours to look back for posts (default: 24)
            
        Returns:
            List of XPost objects filtered to last 24 hours
        """
        # Map RSS URLs to authors - needed because X posts need author info
        url_to_author = {
            "https://rss.app/feeds/fCifMnuCaCowLWra.xml": "GoogleAI",
            "https://rss.app/feeds/Q5rW7ItVWp4ku2hB.xml": "ollama",
            "https://rss.app/feeds/yi4TN3YdV6cdfaRy.xml": "NVIDIAAI",
            "https://rss.app/feeds/6tUN75HYDHwtfszj.xml": "AIatMeta",
            "https://rss.app/feeds/XUhcVCEsFbmpnTjs.xml": "GoogleDeepMind",
        }
        
        # Get base articles using parent's get_articles method
        base_articles = super().get_articles(hours)
        
        # Convert to XPost and assign authors based on URL patterns
        posts = []
        seen_guids = set()
        
        for article in base_articles:
            guid = article.guid
            if guid in seen_guids:
                continue
            seen_guids.add(guid)
            
            # Try to infer author from URL or assign default
            # Since BaseScraper processes all URLs together, we can't easily track
            # which URL an article came from, so we'll use a default or try to infer
            author = "Unknown"
            article_url = article.url if hasattr(article, 'url') else ''
            
            # Try to match author based on URL patterns (if RSS feed URLs appear in article URLs)
            for rss_url, auth in url_to_author.items():
                # Extract feed ID from RSS URL to match with article URLs
                if any(keyword in article_url.lower() for keyword in [auth.lower()]):
                    author = auth
                    break
            
            article_dict = article.model_dump()
            article_dict['author'] = author
            posts.append(XPost(**article_dict))
        
        return posts

    def url_to_markdown(self, url: str) -> Optional[str]:
        """
        Convert a X.com post URL to markdown using html_to_markdown.
        
        Args:
            url: URL of the X.com post
            
        Returns:
            Markdown content as string, or None if conversion fails
        """
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            response.raise_for_status()
            html = response.text
            markdown = convert(html)
            return markdown
        except Exception:
            return None


if __name__ == "__main__":
    scraper = XScraper()
    print("Starting X.com scraper...")
    print("="*60)
    
    # Get posts from the last 24 hours
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
                preview = post.description[:500] + "..." if len(post.description) > 500 else post.description
                print(f"  Preview: {preview}")
    else:
        print("\nNo posts found in the last 24 hours.")