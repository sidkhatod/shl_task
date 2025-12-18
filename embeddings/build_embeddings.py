import json
import numpy as np
from sentence_transformers import SentenceTransformer

from embeddings.text_builder import build_assessment_text

# ----------------------------
# CONFIG
# ----------------------------
PARSED_JSON = "data/parsed/parsed_assessments.json"
EMBEDDINGS_OUT = "data/embeddings/catalogue_embeddings.npy"
META_OUT = "data/embeddings/catalogue_metadata.json"

MODEL_NAME = "all-MiniLM-L6-v2"

# ----------------------------
# Load data
# ----------------------------
with open(PARSED_JSON, "r") as f:
    all_assessments = json.load(f)

print(f"Loaded {len(all_assessments)} assessments")

# ----------------------------
# Build texts
# ----------------------------
texts = [build_assessment_text(a) for a in all_assessments]

# ----------------------------
# Encode
# ----------------------------
model = SentenceTransformer(MODEL_NAME)

embeddings = model.encode(
    texts,
    normalize_embeddings=True,
    batch_size=32,
    show_progress_bar=True
)

embeddings = np.array(embeddings)

# ----------------------------
# Save outputs
# ----------------------------
np.save(EMBEDDINGS_OUT, embeddings)

with open(META_OUT, "w") as f:
    json.dump(all_assessments, f, indent=2)

print("Saved embeddings →", EMBEDDINGS_OUT)
print("Saved metadata →", META_OUT)
