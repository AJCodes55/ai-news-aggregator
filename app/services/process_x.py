from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.x import XScraper
from app.database.repository import Repository
from .base import BaseProcessService


class XMarkdownProcessor(BaseProcessService):
    def __init__(self):
        super().__init__()
        self.scraper = XScraper()
        self.repo = Repository()

    def get_items_to_process(self, limit: Optional[int] = None) -> list:
        return self.repo.get_x_posts_without_markdown(limit=limit)

    def process_item(self, item) -> Optional[str]:
        return self.scraper.url_to_markdown(item.url)

    def save_result(self, item, result: str) -> bool:
        return self.repo.update_x_post_markdown(item.guid, result)


def process_x_markdown(limit: Optional[int] = None) -> dict:
    processor = XMarkdownProcessor()
    return processor.process(limit=limit)


if __name__ == "__main__":
    result = process_x_markdown()
    print(f"Total posts: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")

