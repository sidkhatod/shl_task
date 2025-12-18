# SHL Assessment Recommendation System

## Overview
This project implements a web-based Retrieval-Augmented Generation (RAG) system to recommend SHL assessments based on natural language hiring queries.

## Key Features
- Robust crawler for SHL product catalog
- Accurate assessment metadata parsing
- Semantic search using Sentence Transformers
- Query understanding via Gemini LLM
- Recall@10 evaluation on provided dataset
- REST API for recommendations

## Tech Stack
Python, FastAPI, SentenceTransformers, Gemini API, BeautifulSoup, scikit-learn

## Running Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Set `GEMINI_API_KEY` as environment variable
3. Run API: `uvicorn app:app --host 0.0.0.0 --port 8000`

## API Endpoints
- GET /health
- POST /recommend

## Submission
- CSV generated via `generate_submission_csv.py`
- API deployed on Render
