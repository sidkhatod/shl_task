import pandas as pd
from collections import defaultdict
from retrieval.recommender import recommend

def extract_slug(url):
    return url.strip("/").split("/")[-1].lower()

def recall_at_k(pred, gt, k=10):
    pred_slugs = {extract_slug(u) for u in pred[:k]}
    gt_slugs = {extract_slug(u) for u in gt}
    return len(pred_slugs & gt_slugs) / len(gt_slugs)

df = pd.read_excel("data/raw/Gen_AI Dataset.xlsx")

gt_by_query = defaultdict(set)
for _, row in df.iterrows():
    gt_by_query[row["Query"]].add(row["Assessment_url"])

recalls = []
for query, gt in gt_by_query.items():
    preds = recommend(query, k=10)
    recalls.append(recall_at_k(preds, gt))

print("Mean Recall@10:", sum(recalls)/len(recalls))
