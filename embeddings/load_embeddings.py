import json
import numpy as np

EMBEDDINGS_PATH = "data/embeddings/catalogue_embeddings.npy"
META_PATH = "data/embeddings/catalogue_metadata.json"

def load_catalogue():
    embeddings = np.load(EMBEDDINGS_PATH)
    with open(META_PATH, "r") as f:
        metadata = json.load(f)

    return embeddings, metadata
