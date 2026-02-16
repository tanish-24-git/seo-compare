# Enterprise SEO Comparison Engine

A production-grade, containerized SEO intelligence backend built with FastAPI, Docker Compose, Playwright, and Celery.

## 🚀 Features
- **Async Deep Crawling**: Depth-controlled site exploration using Playwright.
- **100-Parameter Extraction**: Comprehensive SEO audit matrix (Technical, YMYL, E-E-A-T, Content, India-specific).
- **Comparison Engine**: Weighted gap analysis comparing competitors vs. Bajaj Life baseline.
- **Task Queue**: Redis-backed Celery workers for heavy extraction tasks.
- **Enterprise Design**: Clean Architecture, SOLID principles, and full Dockerization.

## 🛠 Tech Stack
- **Backend**: FastAPI
- **Scraping**: Playwright + BeautifulSoup4
- **Queue/Cache**: Redis + Celery
- **Database**: PostgreSQL (Active/Ready)
- **Containerization**: Docker Compose

## 📦 Getting Started

### 1. Build and Start the Containers
```bash
docker-compose up --build
```

### 2. Extract Bajaj Life Baseline
Once the server is running, trigger the initial baseline extraction:
```bash
curl -X POST "http://localhost:8000/api/v1/extract/baseline"
```
The result will be stored in `/app/data/baseline/bajajlife_full_seo.json`.

### 3. Extract a Competitor
```bash
curl -X POST "http://localhost:8000/api/v1/extract/competitor?url=https://www.competitor.com"
```

### 4. Comparison API
Access the auto-generated documentation at [http://localhost:8000/docs](http://localhost:8000/docs) to see all available endpoints for comparison and reporting.

## 🗂 Project Structure
```
/app
├── core/       # Configuration and Worker setup
├── api/        # REST Endpoints
├── services/   # Crawler, Extractor, and Comparator Logic
├── models/     # SEO Parameter Schemas (100 parameters)
├── data/       # Local JSON Storage (mounted volumes)
└── main.py     # Entry point
```
