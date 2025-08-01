import mysql.connector.pooling
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class DatabaseConnectionError(Exception):
    """Custom exception for database connection issues"""
    pass

def get_db_config() -> Dict[str, Any]:
    """Get and validate database configuration"""
    config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "pool_name": "auth_pool",
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "autocommit": True
    }
    
    if None in [config['user'], config['password'], config['database']]:
        raise ValueError("Missing required database configuration in .env file")
    
    return config

def create_connection_pool() -> Optional[mysql.connector.pooling.MySQLConnectionPool]:
    """Create and verify the connection pool"""
    try:
        config = get_db_config()
        pool = mysql.connector.pooling.MySQLConnectionPool(**config)
        
        # Test the connection
        test_conn = pool.get_connection()
        test_conn.ping(reconnect=True, attempts=3, delay=5)
        test_conn.close()
        
        logger.info("Database connection pool established successfully")
        return pool
    except mysql.connector.Error as err:
        logger.error(f"Database connection failed: {err}")
        raise DatabaseConnectionError(f"Could not connect to database: {err}") from err

# Initialize connection pool
try:
    connection_pool = create_connection_pool()
except DatabaseConnectionError as e:
    logger.critical(f"Critical database error: {e}")
    connection_pool = None
    # Consider whether to exit the application here if DB is critical