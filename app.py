# app.py
from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

# Globals (EMPTY at startup)
model = None
catalogue_embeddings = None
all_assessments = None


def load_resources():
    global model, catalogue_embeddings, all_assessments

    if model is None:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        import json

        model = SentenceTransformer("all-MiniLM-L6-v2")

        with open("data/parsed/parsed_assessments.json") as f:
            all_assessments = json.load(f)

        catalogue_embeddings = np.load(
            "data/embeddings/catalogue_embeddings.npy"
        )


class RecommendRequest(BaseModel):
    query: str
    k: int = 10


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend")
def recommend(req: RecommendRequest):
    load_resources()  # 👈 LOAD ONLY WHEN CALLED

    from retrieval.recommender import recommend_assessments
    results = recommend_assessments(
        req.query,
        req.k,
        model,
        catalogue_embeddings,
        all_assessments
    )

    return {
        "query": req.query,
        "recommendations": results
    }
