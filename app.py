"""
Page Pulse - Website Audit Tool Backend
Built with FastAPI, BeautifulSoup4, and Requests.
Provides complete technical SEO auditing, performance metrics, and graceful error handling.
"""

import os
import re
import time
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import requests

# Initialize FastAPI app
app = FastAPI(
    title="Page Pulse API",
    description="Website Audit Tool API for technical SEO & performance reporting",
    version="1.0.0",
)

# Enable CORS for external access / testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount Static and Template directories
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


class AuditRequest(BaseModel):
    url: str = Field(..., description="Target website URL to analyze", json_schema_extra={"example": "https://example.com"})


def normalize_url(raw_url: str) -> str:
    """
    Normalizes input URL strings.
    Prepends 'https://' if no protocol scheme is specified.
    Strips whitespace.
    """
    url = raw_url.strip()
    if not url:
        raise ValueError("URL cannot be empty.")
    
    # Prepend scheme if missing
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url

    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("Invalid URL format. Please provide a valid domain name.")
        
    return url


def calculate_seo_score(
    title: Optional[str],
    meta_description: Optional[str],
    h1_count: int,
    total_images: int,
    images_without_alt: int,
    word_count: int
) -> Tuple[int, Dict[str, Any]]:
    """
    Calculates SEO score (/100) based on standard audit rules:
    - Title exists (+20)
    - Meta description exists (+20)
    - H1 exists (+20)
    - Images have alt text (+20)
    - Word count > 300 (+20)
    Returns (total_score, breakdown_dictionary).
    """
    score = 0
    breakdown = {}

    # Rule 1: Title exists & non-empty
    has_title = bool(title and title.strip() and title != "Missing title tag")
    if has_title:
        score += 20
        breakdown["title"] = {"pass": True, "points": 20, "message": "Page title is present"}
    else:
        breakdown["title"] = {"pass": False, "points": 0, "message": "Missing page title tag"}

    # Rule 2: Meta description exists & non-empty
    has_meta_desc = bool(meta_description and meta_description.strip() and meta_description != "Missing meta description")
    if has_meta_desc:
        score += 20
        breakdown["meta_description"] = {"pass": True, "points": 20, "message": "Meta description is present"}
    else:
        breakdown["meta_description"] = {"pass": False, "points": 0, "message": "Missing meta description"}

    # Rule 3: H1 exists
    has_h1 = h1_count > 0
    if has_h1:
        score += 20
        breakdown["h1"] = {"pass": True, "points": 20, "message": f"H1 heading structure present ({h1_count} found)"}
    else:
        breakdown["h1"] = {"pass": False, "points": 0, "message": "No H1 heading found on page"}

    # Rule 4: Images have alt text
    if total_images == 0:
        images_pass = True
        msg = "No images on page (accessibility satisfied)"
    elif images_without_alt == 0:
        images_pass = True
        msg = f"All {total_images} images have alt text"
    else:
        images_pass = False
        msg = f"{images_without_alt} of {total_images} image(s) missing alt attribute"

    if images_pass:
        score += 20
        breakdown["alt_text"] = {"pass": True, "points": 20, "message": msg}
    else:
        breakdown["alt_text"] = {"pass": False, "points": 0, "message": msg}

    # Rule 5: Word count > 300
    has_good_wordcount = word_count > 300
    if has_good_wordcount:
        score += 20
        breakdown["word_count"] = {"pass": True, "points": 20, "message": f"Sufficient copy length ({word_count} words)"}
    else:
        breakdown["word_count"] = {"pass": False, "points": 0, "message": f"Low word count ({word_count} words, recommended > 300)"}

    return score, breakdown


def perform_website_audit(target_url: str) -> Dict[str, Any]:
    """
    Fetches the web page at target_url using Requests and audits its content with BeautifulSoup.
    Catches all network and parsing exceptions cleanly without crashing.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 PagePulse/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    start_time = time.perf_counter()

    try:
        response = requests.get(target_url, timeout=10, headers=headers, allow_redirects=True)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000)
    except requests.exceptions.MissingSchema:
        return {
            "success": False,
            "status": 400,
            "error": "Invalid URL schema. Please include http:// or https://",
            "url": target_url
        }
    except requests.exceptions.InvalidURL:
        return {
            "success": False,
            "status": 400,
            "error": "Invalid URL format or domain name could not be parsed.",
            "url": target_url
        }
    except requests.exceptions.SSLError:
        return {
            "success": False,
            "status": 495,
            "error": "SSL verification failed for target server.",
            "url": target_url
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "status": 502,
            "error": "Failed to establish network connection. Check domain validity and DNS settings.",
            "url": target_url
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "status": 504,
            "error": "Connection timed out while waiting for server response (10s timeout).",
            "url": target_url
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "success": False,
            "status": 500,
            "error": f"Network request error: {str(req_err)}",
            "url": target_url
        }

    # Verify response Content-Type is HTML
    content_type = response.headers.get("Content-Type", "").lower()
    is_html = "text/html" in content_type or "application/xhtml+xml" in content_type
    
    if not is_html:
        return {
            "success": False,
            "status": response.status_code,
            "error": f"Target URL returned non-HTML content type: '{content_type or 'Unknown'}'. "
                     "Page Pulse can only audit HTML web pages.",
            "url": target_url
        }

    # Parse HTML using BeautifulSoup
    try:
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Status code
        http_status = response.status_code

        # 2. Response Time
        response_time_str = f"{elapsed_ms} ms"

        # 3. Page Title
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if (title_tag and title_tag.get_text()) else "Missing title tag"

        # 4. Meta Description
        meta_desc_tag = (
            soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)}) or
            soup.find("meta", attrs={"property": re.compile(r"^og:description$", re.I)})
        )
        meta_description = meta_desc_tag.get("content", "").strip() if (meta_desc_tag and meta_desc_tag.get("content")) else "Missing meta description"

        # 5. Number of H1 tags
        h1_count = len(soup.find_all("h1"))

        # 6. Total Images & 7. Images Missing Alt Text
        images = soup.find_all("img")
        total_images = len(images)
        images_without_alt = 0
        for img in images:
            alt = img.get("alt")
            if alt is None or not str(alt).strip():
                images_without_alt += 1

        # 8. Approximate Word Count
        # Remove script and style elements from word count calculation
        for script_or_style in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            script_or_style.decompose()
        text_content = soup.get_text(separator=" ")
        words = re.findall(r"\b\w+\b", text_content)
        word_count = len(words)

        # 9. Canonical URL
        canonical_tag = soup.find("link", attrs={"rel": re.compile(r"^canonical$", re.I)})
        canonical = canonical_tag.get("href", "").strip() if (canonical_tag and canonical_tag.get("href")) else "Not specified"

        # 10. Robots Meta Tag
        robots_tag = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
        robots = robots_tag.get("content", "").strip() if (robots_tag and robots_tag.get("content")) else "Not specified"

        # 11. SEO Score & Breakdown
        seo_score, score_breakdown = calculate_seo_score(
            title=title,
            meta_description=meta_description,
            h1_count=h1_count,
            total_images=total_images,
            images_without_alt=images_without_alt,
            word_count=word_count
        )

        return {
            "success": True,
            "status": http_status,
            "response_time": response_time_str,
            "title": title,
            "meta_description": meta_description,
            "h1_count": h1_count,
            "total_images": total_images,
            "images_without_alt": images_without_alt,
            "word_count": word_count,
            "canonical": canonical,
            "robots": robots,
            "seo_score": seo_score,
            "score_breakdown": score_breakdown,
            "target_url": target_url,
            "error": None
        }

    except Exception as parse_err:
        return {
            "success": False,
            "status": 500,
            "error": f"Failed to parse webpage content: {str(parse_err)}",
            "url": target_url
        }


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """
    Renders the main single-page audit tool frontend interface.
    """
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/analyze")
async def analyze_endpoint(payload: AuditRequest):
    """
    POST /analyze API endpoint.
    Accepts JSON body: {"url": "https://example.com"}
    Returns structured audit report or informative error payload without crashing.
    """
    raw_url = payload.url
    if not raw_url or not raw_url.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "status": 400,
                "error": "URL parameter cannot be empty.",
                "url": ""
            }
        )

    try:
        normalized_url = normalize_url(raw_url)
    except ValueError as val_err:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "status": 400,
                "error": str(val_err),
                "url": raw_url
            }
        )

    report = perform_website_audit(normalized_url)
    
    # Return 200 OK with the report payload (even if target site returned 404/500 or error, so client UI gets clean report structure)
    return JSONResponse(status_code=status.HTTP_200_OK, content=report)


if __name__ == "__main__":
    import uvicorn
    # Local direct execution server launcher
    print("🚀 Starting Page Pulse Server on http://127.0.0.1:8000 ...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
