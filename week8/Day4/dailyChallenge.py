from dotenv import load_dotenv
import os
import time
import requests
import tempfile
import pandas as pd
import torch
from pinecone import Pinecone, ServerlessSpec
from transformers import AutoTokenizer, AutoModel

load_dotenv()

# ── Client ────────────────────────────────────────────────────────────────────
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])


# ═════════════════════════════════════════════════════════════════════════════
# PART 1 — Basic reranking (Apple fruit vs Apple Inc.)
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("PART 1 — Basic Reranking")
print("="*60)

query = "Tell me about Apple's products"

documents = [
    "An apple is a sweet, edible fruit produced by an apple tree.",
    "Apple Inc. makes popular products like the iPhone, iPad, and MacBook.",
    "Apples come in many varieties such as Fuji, Gala, and Granny Smith.",
    "Apple's latest Mac computers use their custom M-series chips for high performance.",
    "Eating an apple a day is often associated with good health habits.",
]

reranked = pc.inference.rerank(
    model="bge-reranker-v2-m3",
    query=query,
    documents=[{"id": str(i), "text": doc} for i, doc in enumerate(documents)],
    top_n=3,
)

print(f"Query: {query}\n")
for i, m in enumerate(reranked.data):
    print(f"{i+1}. Score: {m.score:.4f}")
    print(f"   Text: {m.document.text}\n")


# ═════════════════════════════════════════════════════════════════════════════
# PART 2 — Serverless index + medical notes search & reranking
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("PART 2 — Medical Notes: Semantic Search + Reranking")
print("="*60)

# ── Index config ──────────────────────────────────────────────────────────────
cloud      = os.getenv("PINECONE_CLOUD", "aws")
region     = os.getenv("PINECONE_REGION", "us-east-1")
index_name = "medical-notes-index"
spec       = ServerlessSpec(cloud=cloud, region=region)

if pc.has_index(name=index_name):
    pc.delete_index(name=index_name)

pc.create_index(name=index_name, dimension=384, metric="cosine", spec=spec)
print("Index created.")

# ── Load & upsert data ────────────────────────────────────────────────────────
url = (
    "https://raw.githubusercontent.com/pinecone-io/examples/"
    "refs/heads/master/docs/data/sample_notes_data.jsonl"
)

with tempfile.TemporaryDirectory() as tmp:
    file_path = os.path.join(tmp, "sample_notes_data.jsonl")
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, "wb") as f:
        f.write(response.content)
    df = pd.read_json(file_path, orient="records", lines=True)

print("Data shape:", df.shape)

index = pc.Index(name=index_name)
index.upsert_from_dataframe(df)

while True:
    count = index.describe_index_stats().total_vector_count
    print(f"Vector count: {count}")
    if count > 0:
        break
    time.sleep(5)

print("Index ready!")

# ── Embedding model ───────────────────────────────────────────────────────────
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer  = AutoTokenizer.from_pretrained(MODEL_NAME)
embed_model = AutoModel.from_pretrained(MODEL_NAME)

def get_embedding(text):
    encoded = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        output = embed_model(**encoded)
    return output.last_hidden_state[0].mean(dim=0)

# ── Semantic search ───────────────────────────────────────────────────────────
question = "patient has chest pain"
results  = index.query(vector=[get_embedding(question).tolist()], top_k=5, include_metadata=True)
sorted_matches = sorted(results["matches"], key=lambda x: x["score"], reverse=True)

print(f"\nQuestion: '{question}'\nInitial Results:")
for i, m in enumerate(sorted_matches):
    print(f"  {i+1}. ID: {m['id']}  Score: {m['score']:.4f}")
    print(f"     Metadata: {m['metadata']}\n")

# ── Rerank ────────────────────────────────────────────────────────────────────
transformed_documents = [
    {
        "id": m["id"],
        "reranking_field": "; ".join(f"{k}: {v}" for k, v in m["metadata"].items()),
    }
    for m in results["matches"]
]

refined_query = "patient experiencing acute chest pain and shortness of breath"

reranked_results = pc.inference.rerank(
    model="bge-reranker-v2-m3",
    query=refined_query,
    documents=transformed_documents,
    rank_fields=["reranking_field"],
    top_n=3,
    return_documents=True,
)

print(f"\nRefined Query: '{refined_query}'\nReranked Results:")
for i, m in enumerate(reranked_results.data):
    print(f"  {i+1}. ID: {m.document.id}  Score: {m.score:.4f}")
    print(f"     {m.document.reranking_field}\n")

# ── Clean up ──────────────────────────────────────────────────────────────────
pc.delete_index(name=index_name)
print("Index deleted.")