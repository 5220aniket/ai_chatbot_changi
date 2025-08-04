# src/api.py

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import sys
import logging
from pathlib import Path

# Project structure
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Directories
STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("changi-api")

# Check static/templates
if not STATIC_DIR.exists():
    logger.warning(f"[Warning] Static directory missing: {STATIC_DIR}")
if not TEMPLATES_DIR.exists():
    logger.warning(f"[Warning] Templates directory missing: {TEMPLATES_DIR}")

# Import chatbot
try:
    from src.chatbot import ChangiChatbot
except ImportError:
    from chatbot import ChangiChatbot

# Initialize FastAPI
app = FastAPI(title="Changi Airport Assistant")

# Static and templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Load Chatbot
try:
    chatbot = ChangiChatbot()
except Exception as e:
    logger.error(f"❌ Chatbot initialization failed: {e}")
    chatbot = None

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask(request: Request, question: str = Form(...)):
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot is not available.")
    try:
        logger.info(f"📨 Question received: {question}")
        answer = chatbot.get_changi_info(question)
        return JSONResponse(content={"answer": answer})
    except Exception as e:
        logger.error(f"❌ Error during QA: {e}")
        raise HTTPException(status_code=500, detail="Error generating answer")

@app.get("/health")
async def health():
    return {"status": "healthy" if chatbot else "unhealthy"}

# For development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
