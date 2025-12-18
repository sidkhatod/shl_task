import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from retrieval.recommender import recommend

# ----------------------------
# FastAPI App
# ----------------------------
app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0.0"
)

# ----------------------------
# Request / Response Schemas
# ----------------------------
class RecommendRequest(BaseModel):
    query: str


class RecommendationItem(BaseModel):
    assessment_url: str


class RecommendResponse(BaseModel):
    query: str
    recommendations: list[RecommendationItem]


# ----------------------------
# Health Check Endpoint
# ----------------------------
@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}


# ----------------------------
# Recommendation Endpoint
# ----------------------------
@app.post("/recommend", response_model=RecommendResponse)
def recommend_assessments(req: RecommendRequest):
    """
    Accepts a natural language query and returns
    recommended assessment URLs.
    """
    query = req.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        urls = recommend(query, k=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not urls:
        raise HTTPException(status_code=404, detail="No recommendations found")

    return {
        "query": query,
        "recommendations": [
            {"assessment_url": url} for url in urls
        ]
    }
