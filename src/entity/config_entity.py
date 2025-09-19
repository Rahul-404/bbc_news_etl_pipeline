import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass
class MongoDBConfig:
    """
    Configuration for MongoDB connection and document schema.

    Environment Variables
    ---------------------
    MONGODB_DATABASE_NAME : str
        Name of the MongoDB database (default: 'BBC_NEWS_DATABASE').

    MONGODB_COLLECTION_NAME : str
        Name of the MongoDB collection (default: 'RAW_BBC_NEWS_COLLECTION').

    Attributes
    ----------
    MONGODB_DATABASE_NAME : str
        MongoDB database name.

    MONGODB_COLLECTION_NAME : str
        MongoDB collection name.

    MONGO_DOC_DATE_KEY : str
        Key name for the document's published date (default: 'published').

    MONGO_DOC_CATEGORY_KEY : str
        Key name for the document's category field (default: 'category').

    MONGO_DOC_SUB_CATEGORY_KEY : str
        Key name for the document's sub-category field (default: 'sub_category').

    MONGO_DOC_ARTICLE_URL_KEY : str
        Key name for the document's article URL (default: 'url').
    """
    MONGODB_DATABASE_NAME: str = os.getenv("MONGODB_DATABASE_NAME", "BBC_NEWS_DATABASE")
    MONGODB_COLLECTION_NAME: str = os.getenv("MONGODB_COLLECTION_NAME", "RAW_BBC_NEWS_COLLECTION")
    MONGO_DOC_DATE_KEY: str = "published"
    MONGO_DOC_CATEGORY_KEY: str = "category"          # Fixed typo here
    MONGO_DOC_SUB_CATEGORY_KEY: str = "sub_category"  # Fixed typo here
    MONGO_DOC_ARTICLE_URL_KEY: str = "url"
    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", 27017))
    MONGODB_URI: str = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
