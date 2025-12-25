from typing import Optional
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agent.digest_agent import DigestAgent
from app.database.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_digests(limit: Optional[int] = None) -> dict:
    agent = DigestAgent()
    repo = Repository()
    
    articles = repo.get_articles_without_digest(limit=limit)
    total = len(articles)
    processed = 0
    failed = 0
    
    logger.info(f"Starting digest processing for {total} articles")
    
    # Check if we should wait before starting (to let rate limits reset)
    if total > 0:
        logger.info("💡 Tip: If you've recently hit rate limits, wait 2-5 minutes before starting")
    
    for idx, article in enumerate(articles, 1):
        article_type = article["type"]
        article_id = article["id"]
        article_title = article["title"][:60] + "..." if len(article["title"]) > 60 else article["title"]
        
        logger.info(f"[{idx}/{total}] Processing {article_type}: {article_title} (ID: {article_id})")
        
        try:
            digest_result = agent.generate_digest(
                title=article["title"],
                content=article["content"],
                article_type=article_type
            )
            
            if digest_result:
                repo.create_digest(
                    article_type=article_type,
                    article_id=article_id,
                    url=article["url"],
                    title=digest_result.title,
                    summary=digest_result.summary,
                    published_at=article.get("published_at")
                )
                processed += 1
                logger.info(f"✓ Successfully created digest for {article_type} {article_id}")
            else:
                failed += 1
                logger.warning(f"✗ Failed to generate digest for {article_type} {article_id}")
        except Exception as e:
            # Check if it's a rate limit error (429)
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str or "too many requests" in error_str:
                wait_time = 180  # Wait 3 minutes on rate limit (rate limit window is typically 1 minute)
                logger.warning(f"✗ Rate limit exceeded for {article_type} {article_id}.")
                logger.warning(f"  Your rate limit quota has been exhausted. Waiting {wait_time} seconds for reset...")
                logger.warning(f"  💡 After this wait, try processing just 1 article: python app/services/process_digest.py 1")
                time.sleep(wait_time)
                # Retry this article (don't increment failed counter yet)
                logger.info(f"Retrying {article_type} {article_id} after rate limit wait...")
                try:
                    digest_result = agent.generate_digest(
                        title=article["title"],
                        content=article["content"],
                        article_type=article_type
                    )
                    if digest_result:
                        repo.create_digest(
                            article_type=article_type,
                            article_id=article_id,
                            url=article["url"],
                            title=digest_result.title,
                            summary=digest_result.summary,
                            published_at=article.get("published_at")
                        )
                        processed += 1
                        logger.info(f"✓ Successfully created digest for {article_type} {article_id} after retry")
                    else:
                        failed += 1
                        logger.warning(f"✗ Failed to generate digest for {article_type} {article_id} after retry")
                except Exception as retry_e:
                    failed += 1
                    logger.error(f"✗ Error retrying {article_type} {article_id}: {retry_e}")
                    # If rate limit again, wait even longer
                    if "429" in str(retry_e).lower() or "rate limit" in str(retry_e).lower():
                        logger.warning("Rate limit hit again. Consider processing fewer articles or waiting longer.")
                        time.sleep(300)  # Wait 5 more minutes
            else:
                failed += 1
                logger.error(f"✗ Error processing {article_type} {article_id}: {e}")
        
        # Add delay between requests to avoid rate limits
        # Free tier: ~3 requests/minute = 20 seconds delay minimum
        # New API keys often have stricter limits - using 30 seconds for safety
        # Paid tier users can reduce this to 5-10 seconds
        if idx < total:
            time.sleep(30)  # Increased to 30 seconds for free/new API keys
    
    logger.info(f"Processing complete: {processed} processed, {failed} failed out of {total} total")
    
    return {
        "total": total,
        "processed": processed,
        "failed": failed
    }


if __name__ == "__main__":
    import sys
    
    # Allow limiting number of articles to process (useful for new API keys with strict rate limits)
    # Usage: python process_digest.py 3  (process only 3 articles)
    # For free tier/new API keys, start with 2-3 articles at a time
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    
    if limit:
        logger.info(f"Processing with limit: {limit} articles")
    else:
        logger.warning("⚠️  No limit specified. For new/free tier API keys, use: python process_digest.py 3")
        logger.info("Processing all articles (may hit rate limits with new API keys)")
    
    result = process_digests(limit=limit)
    print(f"\n=== Results ===")
    print(f"Total articles: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")
    
    if result['failed'] > 0:
        print("\n⚠️  Some articles failed to process due to rate limits.")
        print("💡 Solutions:")
        print("   1. Wait 5-10 minutes for your rate limit quota to reset")
        print("   2. Then try processing 1 article: python app/services/process_digest.py 1")
        print("   3. Wait 1-2 minutes between each batch")
        print("   4. Check your rate limits at: https://aistudio.google.com/app/apikey")