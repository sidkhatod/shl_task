import csv
import pandas as pd
from collections import defaultdict

from retrieval.recommender import recommend

# ----------------------------
# CONFIG
# ----------------------------
INPUT_XLSX = "data/raw/Gen_AI Dataset.xlsx"
OUTPUT_CSV = "data/submissions/Siddharth_Khatod.csv"  # rename if required
TOP_K = 10


# ----------------------------
# Load dataset
# ----------------------------
df = pd.read_excel(INPUT_XLSX)

if "Query" not in df.columns or "Assessment_url" not in df.columns:
    raise ValueError("Input dataset must contain 'Query' and 'Assessment_url' columns")

print(f"Loaded dataset with {len(df)} rows")
print(f"Unique queries: {df['Query'].nunique()}")


# ----------------------------
# Collect unique queries
# ----------------------------
queries = df["Query"].drop_duplicates().tolist()


# ----------------------------
# Generate recommendations
# ----------------------------
rows = []

for query in queries:
    print(f"[INFO] Generating recommendations for query:\n{query}\n")

    try:
        recommendations = recommend(query, k=TOP_K)
    except Exception as e:
        print(f"[ERROR] Recommendation failed for query: {query}")
        print(e)
        recommendations = []

    for url in recommendations:
        rows.append({
            "Query": query,
            "Assessment_url": url
        })


# ----------------------------
# Write submission CSV
# ----------------------------
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["Query", "Assessment_url"]
    )
    writer.writeheader()
    writer.writerows(rows)

print("\n[SUCCESS]")
print(f"Submission CSV saved to → {OUTPUT_CSV}")
print(f"Total rows written: {len(rows)}")
