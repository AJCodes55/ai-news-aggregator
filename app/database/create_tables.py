import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.models import (
    Base,
    YouTubeVideo,
    OpenAIArticle,
    AnthropicArticle,
    XPost,
    Digest
)
from app.database.connection import engine

if __name__ == "__main__":
    # Import all models so they are registered with Base.metadata
    # This is necessary for SQLAlchemy to discover all tables
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
