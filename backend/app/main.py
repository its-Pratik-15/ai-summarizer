from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from .routers import summary_router

load_dotenv()

app = FastAPI()

# Configure CORS with environment variable support
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5174")
origins = [
    frontend_url,
    "http://localhost:5173",  # Vite dev server default
    "http://localhost:5174",  # Vite dev server alternate
    "http://localhost:3000",  # React default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(summary_router.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Summarizer Backend!"}
