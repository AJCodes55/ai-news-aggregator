from typing import Optional
import logging

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from app.scrapers.x import XScraper
from app.database.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_x_markdown(limit: Optional[int] = None) -> dict:
    scraper = XScraper()
    repo = Repository()
    
    posts = repo.get_x_posts_without_markdown(limit=limit)
    
    if not posts:
        logger.warning("No X posts found in database without markdown. Make sure you've run the scraper (runner.py) to add posts to the database first.")
        return {
            "total": 0,
            "processed": 0,
            "failed": 0
        }
    
    logger.info(f"Found {len(posts)} X posts without markdown to process")
    processed = 0
    failed = 0
    
    for idx, post in enumerate(posts, 1):
        logger.info(f"[{idx}/{len(posts)}] Processing post: {post.title[:60]}...")
        markdown = scraper.url_to_markdown(post.url)
        try:
            if markdown:
                repo.update_x_post_markdown(post.guid, markdown)
                processed += 1
                logger.info(f"✓ Successfully processed post {post.guid}")
            else:
                failed += 1
                logger.warning(f"✗ Failed to get markdown for post {post.guid}")
        except Exception as e:
            failed += 1
            logger.error(f"✗ Error processing post {post.guid}: {e}")
            continue
    
    logger.info(f"Processing complete: {processed} processed, {failed} failed out of {len(posts)} total")
    
    return {
        "total": len(posts),
        "processed": processed,
        "failed": failed
    }


if __name__ == "__main__":
    result = process_x_markdown()
    print(f"\n=== Results ===")
    print(f"Total posts: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")
    
    if result['total'] == 0:
        print("\n⚠️  No posts found in database. Make sure to run 'python app/runner.py' first to scrape and save X posts to the database.")

