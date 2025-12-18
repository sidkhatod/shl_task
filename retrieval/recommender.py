import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from embeddings.load_embeddings import load_catalogue
from embeddings.text_builder import normalize_text
from llm.gemini_query_understanding import parse_query_with_gemini
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
catalogue_embeddings, all_assessments = load_catalogue()

def recommend(query: str, k: int = 10) -> list[str]:
    q_emb = model.encode(
        [normalize_text(query)],
        normalize_embeddings=True
    )

    sims = cosine_similarity(q_emb, catalogue_embeddings)[0]
    top_idx = np.argsort(sims)[::-1][:30]

    candidates = []
    for i in top_idx:
        a = all_assessments[i].copy()
        a["semantic_score"] = sims[i]
        candidates.append(a)

    q_struct = parse_query_with_gemini(query)

    scored = []
    for a in candidates:
        score = a["semantic_score"]

        for skill in q_struct["hard_skills"]:
            if skill.lower() in a["assessment_name"].lower():
                score += 0.15
            if skill.lower() in a["description"].lower():
                score += 0.10

        if q_struct["soft_skills"] and "P" in a["test_types"]:
            score += 0.20

        if q_struct["max_duration_minutes"] and a["duration_minutes"]:
            if a["duration_minutes"] <= q_struct["max_duration_minutes"]:
                score += 0.10

        scored.append((score, a))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [a["assessment_url"] for _, a in scored[:k]]
