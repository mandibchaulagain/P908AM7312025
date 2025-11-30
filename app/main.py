# FastAPI app initialization

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordRequestForm
from database.connection import connection_pool, DatabaseConnectionError
from api.v1.auth import router as auth_router
import logging
from api.v1 import crop, train

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    if not connection_pool:
        logger.error("Failed to initialize database connection pool!")
        raise RuntimeError("Database connection failed")
    
    logger.info("Application startup: Connection pool ready")
    
    yield
    
    # Shutdown
    if connection_pool:
        logger.info("Closing connection pool...")
        # connection_pool.close()
        logger.info("Connection pool closed")

app = FastAPI(
    title="Crop Prediction API",
    description="API for crop prediction with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:8000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(crop.router)
app.include_router(train.router)

@app.on_event("startup")
def startup_event():
    os.makedirs("model_artifacts", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    from ml.predictor import CropPredictor
    CropPredictor.get_instance()

@app.get("/health", tags=["Health Check"])
async def health_check():
    """Endpoint to verify service health"""
    try:
        # Test database connection
        with connection_pool.get_connection() as conn:
            conn.ping(reconnect=True)
            return {
                "status": "healthy",
                "database": "connected",
                "pool_size": connection_pool.pool_size
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
