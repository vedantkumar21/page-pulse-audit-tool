"""
Unit Tests for Page Pulse - Website Audit Tool
Uses Pytest, FastAPI TestClient, and unittest.mock.
"""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest
import requests

from app import app, normalize_url, calculate_seo_score

client = TestClient(app)

# Sample HTML document for mocking valid web responses
SAMPLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page Title</title>
    <meta name="description" content="This is a test meta description for website auditing.">
    <link rel="canonical" href="https://example.com/test-page">
    <meta name="robots" content="index, follow">
</head>
<body>
    <h1>Main H1 Heading</h1>
    <p>""" + ("word " * 350) + """</p>
    <img src="logo.png" alt="Company Logo">
    <img src="banner.png" alt="Promotion Banner">
    <img src="icon.png"> <!-- Missing alt -->
</body>
</html>
"""


def test_read_root():
    """Test that GET / returns 200 OK and renders HTML index page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Page Pulse" in response.text
    assert "Digital Heroes Training Task" in response.text
    assert "digitalheroesco.com" in response.text


def test_normalize_url():
    """Test URL normalization function."""
    assert normalize_url("example.com") == "https://example.com"
    assert normalize_url("http://example.com") == "http://example.com"
    assert normalize_url("https://sub.domain.com/path") == "https://sub.domain.com/path"
    
    with pytest.raises(ValueError):
        normalize_url("")


def test_calculate_seo_score():
    """Test SEO score calculation logic."""
    # Perfect score test
    score, breakdown = calculate_seo_score(
        title="Valid Title",
        meta_description="Valid Meta Description",
        h1_count=1,
        total_images=2,
        images_without_alt=0,
        word_count=500
    )
    assert score == 100
    assert breakdown["title"]["pass"] is True
    assert breakdown["meta_description"]["pass"] is True
    assert breakdown["h1"]["pass"] is True
    assert breakdown["alt_text"]["pass"] is True
    assert breakdown["word_count"]["pass"] is True

    # Poor score test
    score_poor, breakdown_poor = calculate_seo_score(
        title="Missing title tag",
        meta_description="Missing meta description",
        h1_count=0,
        total_images=2,
        images_without_alt=2,
        word_count=100
    )
    assert score_poor == 0
    assert breakdown_poor["title"]["pass"] is False


@patch("requests.get")
def test_analyze_valid_url(mock_get):
    """Test POST /analyze with a valid mocked HTML webpage."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_response.text = SAMPLE_HTML
    mock_get.return_value = mock_response

    response = client.post("/analyze", json={"url": "https://example.com"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == 200
    assert "ms" in data["response_time"]
    assert data["title"] == "Test Page Title"
    assert data["meta_description"] == "This is a test meta description for website auditing."
    assert data["h1_count"] == 1
    assert data["total_images"] == 3
    assert data["images_without_alt"] == 1
    assert data["word_count"] > 300
    assert data["canonical"] == "https://example.com/test-page"
    assert data["robots"] == "index, follow"
    assert data["seo_score"] == 80  # 4 criteria pass (+20 each), 1 image missing alt (-20)


def test_analyze_invalid_url():
    """Test POST /analyze with empty or malformed URL."""
    # Empty payload
    response_empty = client.post("/analyze", json={"url": ""})
    assert response_empty.status_code == 400
    assert response_empty.json()["success"] is False

    # Invalid domain without scheme/host
    response_invalid = client.post("/analyze", json={"url": "   "})
    assert response_invalid.status_code == 400
    assert response_invalid.json()["success"] is False


@patch("requests.get")
def test_analyze_404_url(mock_get):
    """Test POST /analyze when target website returns HTTP 404."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = "<html><head><title>404 Not Found</title></head><body><h1>404</h1></body></html>"
    mock_get.return_value = mock_response

    response = client.post("/analyze", json={"url": "https://example.com/nonexistent"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == 404
    assert data["title"] == "404 Not Found"
    assert data["h1_count"] == 1


@patch("requests.get")
def test_analyze_timeout(mock_get):
    """Test POST /analyze handling when request times out."""
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

    response = client.post("/analyze", json={"url": "https://slow-website.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == 504
    assert "timed out" in data["error"].lower()


@patch("requests.get")
def test_analyze_non_html(mock_get):
    """Test POST /analyze when target URL returns non-HTML content (e.g. PDF)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/pdf"}
    mock_get.return_value = mock_response

    response = client.post("/analyze", json={"url": "https://example.com/document.pdf"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "non-HTML content type" in data["error"]
