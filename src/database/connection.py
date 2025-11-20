"""
MongoDB connection management
"""
import os
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Global client instance
_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def get_mongodb_client() -> MongoClient:
    """Get or create MongoDB client"""
    global _client
    
    if _client is None:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        try:
            # For MongoDB Atlas, handle SSL/TLS certificate issues
            # In development, allow invalid certificates (not recommended for production)
            client_options = {
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 5000
            }
            
            # Check if it's an Atlas connection (mongodb+srv:// or contains ssl=true)
            is_atlas = "mongodb+srv://" in mongodb_uri or "ssl=true" in mongodb_uri.lower()
            
            # For development, allow invalid certificates if SSL verification fails
            # In production, you should install proper CA certificates
            if is_atlas:
                # Try with SSL verification first
                try:
                    _client = MongoClient(mongodb_uri, **client_options)
                    _client.admin.command('ping')
                    logger.info("Successfully connected to MongoDB Atlas with SSL verification")
                except Exception as ssl_error:
                    if "CERTIFICATE_VERIFY_FAILED" in str(ssl_error):
                        logger.warning("SSL certificate verification failed. Using tlsAllowInvalidCertificates=True for development.")
                        logger.warning("⚠️  WARNING: This is not secure for production! Install proper CA certificates.")
                        # Retry with invalid certificates allowed (development only)
                        client_options["tlsAllowInvalidCertificates"] = True
                        _client = MongoClient(mongodb_uri, **client_options)
                        _client.admin.command('ping')
                        logger.info("Successfully connected to MongoDB Atlas (SSL verification disabled)")
                    else:
                        raise
            else:
                # Local MongoDB connection
                _client = MongoClient(mongodb_uri, **client_options)
                _client.admin.command('ping')
                logger.info("Successfully connected to MongoDB")
                
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    return _client


def get_database() -> Database:
    """Get database instance"""
    global _database
    
    if _database is None:
        client = get_mongodb_client()
        database_name = os.getenv("DATABASE_NAME", "OzProd")
        _database = client[database_name]
        logger.info(f"Using database: {database_name}")
    
    return _database


def get_collection(collection_name: str) -> Collection:
    """Get a collection from the database"""
    db = get_database()
    return db[collection_name]


def close_connection():
    """Close MongoDB connection"""
    global _client, _database
    
    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")

