from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database.connection import init_db
from routes import auth_router
from errors import AuthOrUserException


@asynccontextmanager
async def life_span(app:FastAPI):
    print("✅ Starting the server...")
    
    # await init_db()
    yield
    
    print("🛑 Stopping the server...")

version ='v1'
app =FastAPI(
    title='Messenger-Auth',
    description='None',
    version=version,
    lifespan=life_span 
)

@app.exception_handler(AuthOrUserException)
async def exception_handler(request : Request, exc :  AuthOrUserException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.__class__.__name__ ,
            'message' : exc.message,
            'resulation' : exc.resulation
        }
    )


app.include_router(auth_router,prefix=f'/api/{version}/auth' , tags=['User'])