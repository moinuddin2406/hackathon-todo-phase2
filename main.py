from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import tasks
from routes import auth
from config import settings
from db import create_db_and_tables
import os

# Create the FastAPI application instance
app = FastAPI(
    title="JWT-Protected Todo API",
    description="A secure, JWT-protected REST API for managing user tasks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Add exposed headers to allow frontend to access authorization headers
    expose_headers=["Authorization"]
)

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Include the auth routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include the task routes with the proper prefix
app.include_router(tasks.router, prefix="/api/{user_id}", tags=["tasks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the JWT-Protected Todo API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Add global exception handlers for common HTTP errors
@app.exception_handler(401)
async def unauthorized_exception_handler(request, exc):
    # Don't apply custom message to auth endpoints
    if request.url.path.startswith('/auth'):
        # Return the original exception detail
        detail = getattr(exc, 'detail', 'Unauthorized')
        return JSONResponse(
            status_code=401,
            content={"detail": detail}
        )
    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized: Invalid or missing JWT token"}
    )

@app.exception_handler(403)
async def forbidden_exception_handler(request, exc):
    return JSONResponse(
        status_code=403,
        content={"detail": "Forbidden: User ID mismatch"}
    )