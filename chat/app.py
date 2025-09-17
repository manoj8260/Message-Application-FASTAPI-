import uvicorn
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from router.ws_router import ws_router 
from router.api_router import api_router
from middleware import register_middleware


@asynccontextmanager
async def life_span(app:FastAPI):
    print("✅ Starting chat server...")
    
    # await init_db()
    yield
    
    print("🛑 Stopping chat server...")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Create FastAPI instance
version = "1.0.0"
app = FastAPI(
    title="WebSocket Chat Application",
    description="A real-time chat application using FastAPI and WebSockets",
    version=version,
    lifespan=life_span,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Include WebSocket router
app.include_router(ws_router, prefix='/ws', tags=["WebSocket"])
app.include_router(api_router,prefix='/api',tags=["Api"])

# register middleware
register_middleware(app)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Status of the application
    """
    return {"status": "healthy", "message": "Chat application is running"}    
    

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="localhost",
        port=8003,
        reload=True,
        log_level="info"
    )

