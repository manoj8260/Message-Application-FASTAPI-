import uvicorn
import logging
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from router.ws_router import router as websocket_router


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
    docs_url="/docs",
    redoc_url="/redoc"
)
# Mount static files (for CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Include WebSocket router
app.include_router(websocket_router,prefix='/api',tags=["WebSocket"])

templates = Jinja2Templates(
    directory="templates"
)

@app.get('/')
async def get_chat_page(request : Request):
    """
    Serve the main chat page.
    """
    return templates.TemplateResponse(
        request ,
        'chat.html',
        {}
    )
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
        port=8001,
        reload=True,
        log_level="info"
    )

