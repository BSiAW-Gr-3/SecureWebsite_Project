"""
Main FastAPI application
"""
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from handlers.logger import init_logger, log_message
from schemas.schemas import LogMessage
from handlers.database import init_db
from routes import auth, chat

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_logger()
    yield
    # Shutdown
    pass

# Create FastAPI app
app = FastAPI(title="Forum API", lifespan=lifespan)

# Handle validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler to sanitize validation errors and hide sensitive data"""
    errors = []
    for error in exc.errors():
        if 'password' in error.get('loc', []):
            error_dict = {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
            }
        else:
            error_dict = error
        errors.append(error_dict)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
    )

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:8080",
        "https://rybmw.space",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monitor session
@app.middleware("http")
async def monitor_session(request: Request, call_next):
    """Middleware to log requests and responses"""
    if request.url.path.startswith("/api/ws") or request.url.path.startswith("/api/token"):
        return await call_next(request)
    
    response = await call_next(request)

    if not request.url.path.startswith("/api/token"):
        msg = LogMessage.from_middleware(request, response)
        await log_message(msg.to_message)
        
    return response 

# Include routers 
app.include_router(auth.router, tags=["Authentication"])
app.include_router(chat.router, tags=["Chat"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Forum API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    