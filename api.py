import os
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from db import init_db, get_original_url
from pilot import pilot
from main import is_valid_url

# Load environment variables
load_dotenv()

# Initialize DB on startup
try:
    init_db()
except Exception as e:
    print(f"[Error] Failed to initialize database: {e}")

app = FastAPI(
    title="Pilot URL Shortener",
    description="A microservice for shortening URLs and handling redirects",
    version="1.0.0"
)

class URLRequest(BaseModel):
    url: str

class URLResponse(BaseModel):
    short_url: str

@app.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(request: URLRequest):
    """
    Accepts a long URL and returns the shortened pilot URL.
    """
    url = request.url.strip()
    
    # Prepend https:// if a scheme is missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    if not is_valid_url(url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL provided")

    try:
        short_url = pilot(url)
        return URLResponse(short_url=short_url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@app.get("/{short_code}")
def redirect_to_original(short_code: str):
    """
    Takes a short code, looks up the original URL, and issues a 302 Redirect.
    """
    original_url = get_original_url(short_code)
    
    if not original_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
        
    return RedirectResponse(url=original_url, status_code=status.HTTP_302_FOUND)
