# Page Pulse – Website Audit Tool 🚀

> **Production-Ready Technical SEO & Web Performance Auditor**  
> Built for the **Digital Heroes Training Task** | Visit [Digital Heroes](https://digitalheroesco.com)

---

## 📌 Project Overview

**Page Pulse** is a lightweight, high-performance web application designed to perform real-time technical SEO and performance audits on any public website URL. By submitting a URL, the tool fetches the webpage DOM via an asynchronous backend pipeline, parses essential search engine optimization signals using BeautifulSoup4, calculates an aggregate **SEO Score (0–100)**, and presents the findings in a modern, responsive Dark Blue & White dashboard interface.

---

## ✨ Features

- **Real-Time Web Scraping & DOM Analysis**: Measures server response time in milliseconds and analyzes page structural elements.
- **Key Technical Metrics Extracted**:
  1. **HTTP Status Code** (e.g. `200 OK`, `404 Not Found`, `500 Server Error`)
  2. **Response Time** (in milliseconds, formatted e.g. `315 ms`)
  3. **Page Title** (`<title>` tag content verification)
  4. **Meta Description** (`<meta name="description">` extraction)
  5. **H1 Tag Counter** (Validates heading structure hierarchy)
  6. **Total Image Counter**
  7. **Missing Image Alt Text Detector** (Accessibility audit)
  8. **Approximate Word Count** (Filters script/style nodes to calculate text copy density)
  9. **Canonical URL** (`<link rel="canonical">` verification)
  10. **Robots Directives** (`<meta name="robots">` search indexing parameters)
- **Bonus Feature – SEO Score (/100)**: Evaluates technical health across 5 weighted rules (+20 points each) with a animated circular progress gauge and itemized breakdown.
- **Robust Fault Tolerance & Error Handling**: Never crashes. Gracefully catches invalid URL schemas, DNS failures, connection timeouts, SSL certificate mismatches, 404/500 errors, and non-HTML binary media (e.g. PDFs, images).
- **Modern Responsive Dashboard**: Built with Vanilla CSS, glassmorphism, pulse animations, toast alert system, sample URL chips, and a one-click summary report copy tool.

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI**: Modern, high-performance Python web framework.
- **Requests**: HTTP client for remote server fetching.
- **BeautifulSoup4**: HTML parser for DOM inspection.
- **Uvicorn / Gunicorn**: ASGI server implementation for production deployment.

### Frontend
- **HTML5**: Semantic document layout.
- **CSS3**: Vanilla CSS styling system with CSS variables, Glassmorphism, and keyframe animations (No React/Tailwind).
- **Vanilla JavaScript**: Asynchronous `fetch` calls, SVG circular gauge calculation, DOM rendering, and toast alerts.

### Testing & Deployment
- **Pytest** & **FastAPI TestClient**: Automated unit testing.
- **Render**: Cloud application hosting via `Procfile` & `runtime.txt`.

---

## 📂 Project Structure

```text
page-pulse/
├── app.py                  # Core FastAPI application, routes, and web scraper logic
├── requirements.txt        # Python dependency manifest
├── Procfile                # Render web process entrypoint
├── runtime.txt             # Environment Python runtime declaration
├── .gitignore              # Version control ignore definitions
├── README.md               # Complete project documentation
├── templates/
│   └── index.html          # Semantic HTML5 single-page dashboard template
├── static/
│   ├── style.css           # Glassmorphism & Dark Blue design system stylesheet
│   └── script.js           # Client-side controller and animation script
└── tests/
    └── test_app.py         # Pytest automated test suite
```

---

## ⚙️ Installation & Running Locally

### Prerequisites
- Python 3.9+ installed on your system.
- `pip` package manager.

### Step-by-Step Setup

1. **Clone or Download the Repository**
   ```bash
   cd page-pulse
   ```

2. **Create and Activate a Virtual Environment (Optional but recommended)**
   ```bash
   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows:
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Application**
   ```bash
   python app.py
   ```

5. **Access the Interface**
   Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## 📑 API Documentation

### `POST /analyze`

Accepts a target URL in the request payload and returns a comprehensive technical audit report.

#### Request Body
```json
{
  "url": "https://example.com"
}
```

#### Successful Response (`200 OK`)
```json
{
  "success": true,
  "status": 200,
  "response_time": "315 ms",
  "title": "Example Domain",
  "meta_description": "This domain is for use in illustrative examples in documents.",
  "h1_count": 1,
  "total_images": 0,
  "images_without_alt": 0,
  "word_count": 342,
  "canonical": "https://example.com/",
  "robots": "index, follow",
  "seo_score": 100,
  "score_breakdown": {
    "title": { "pass": true, "points": 20, "message": "Page title is present" },
    "meta_description": { "pass": true, "points": 20, "message": "Meta description is present" },
    "h1": { "pass": true, "points": 20, "message": "H1 heading structure present (1 found)" },
    "alt_text": { "pass": true, "points": 20, "message": "No images on page (accessibility satisfied)" },
    "word_count": { "pass": true, "points": 20, "message": "Sufficient copy length (342 words)" }
  },
  "target_url": "https://example.com",
  "error": null
}
```

#### Error Response (`400 Bad Request` or Structured Exception)
```json
{
  "success": false,
  "status": 400,
  "error": "Invalid URL schema. Please include http:// or https://",
  "url": "invalid-url"
}
```

---

## 🎨 Key Design & Architectural Decisions

1. **FastAPI ASGI Architecture over Flask**: Chosen for its high concurrency performance, native Pydantic data validation, built-in OpenAPI documentation, and effortless integration with Uvicorn for production readiness on Render.
2. **BeautifulSoup4 DOM Filtering**: To calculate accurate word counts, Page Pulse explicitly strips `<script>`, `<style>`, `<noscript>`, `<header>`, `<footer>`, and `<nav>` elements from the parse tree prior to text extraction. This prevents inline code and navigation menus from skewing true copy metrics.
3. **Graceful Exception Mapping (Zero-Crash Guarantee)**: Network requests are wrapped in dedicated exception blocks (`requests.exceptions.MissingSchema`, `Timeout`, `SSLError`, `ConnectionError`). Rather than returning unhandled 500 stack traces, the API transforms infrastructure errors into structured JSON responses consumable by the frontend toast alert system.
4. **Vanilla CSS Glassmorphism & Zero Heavy Frameworks**: Avoided bulky frontend frameworks to deliver near-instant load times (`< 100ms`). CSS custom properties and backdrop blur filters deliver a sleek, modern visual aesthetic while keeping the application bundle ultra-lightweight.

---

## 🧪 Running Unit Tests

Page Pulse includes automated test coverage written with `pytest` and `fastapi.testclient`.

Run the test suite using:
```bash
pytest tests/test_app.py -v
```

### Test Coverage Highlights:
- ✅ **Valid URL Analysis**: Verifies HTML parsing, metric calculations, and score weighting.
- ✅ **Invalid URL Formats**: Ensures empty and malformed URLs return HTTP 400 responses.
- ✅ **404 Page Handling**: Validates correct extraction when target servers return 404 pages.
- ✅ **Timeout Exception Simulation**: Confirms 504 status and error messaging when network timeout triggers.
- ✅ **Non-HTML Rejection**: Verifies rejection of PDF/Image binary media types.

---

## 🚀 Deployment Guide (Render)

This repository is **GitHub Ready** and pre-configured for direct deployment on **Render**:

1. Push your repository to GitHub.
2. Log into your [Render Dashboard](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Render automatically detects:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT` (via `Procfile`)
5. Click **Create Web Service** to deploy live!

---

## 🔮 Future Improvements

- **Lighthouse Performance Integration**: Integrate Google PageSpeed Insights API for Core Web Vitals (LCP, CLS, INP) metrics.
- **PDF Audit Report Export**: Allow users to download printable PDF audit certificates.
- **Historical Audit Tracking**: Save past URL scans using SQLite / PostgreSQL database integration.
- **Broken Link Checker**: Recursively inspect `<a>` tags on the target page to detect 404 hyperlinks.

---

## 🖼️ Screenshots Placeholder

*(Dashboard Preview - Dark Blue Theme with SVG Score Gauge and Metric Cards Grid)*

```text
 +-----------------------------------------------------------------------+
 |  [Pulse Dot] Page Pulse - Technical SEO & Web Auditor                 |
 |                                                                       |
 |  Enter Website URL: [ https://example.com           ] [ Analyze ]     |
 |                                                                       |
 |  +-----------------------------------------------------------------+  |
 |  | SEO SCORE: 90/100 [Excellent]                                   |  |
 |  | ✓ Page Title present (+20)                                      |  |
 |  | ✓ Meta description present (+20)                                |  |
 |  | ✓ H1 heading present (+20)                                      |  |
 |  +-----------------------------------------------------------------+  |
 |                                                                       |
 |  +--------------------+ +--------------------+ +-------------------+  |
 |  | Server Status: 200 | | Word Count: 523   | | H1 Count: 1       |  |
 |  | Speed: 315 ms      | | Title: Example   | | Status: Optimal   |  |
 |  +--------------------+ +--------------------+ +-------------------+  |
 +-----------------------------------------------------------------------+
```

---

<div align="center">

Built for **Digital Heroes Training Task**  
🔗 [https://digitalheroesco.com](https://digitalheroesco.com)

</div>
