import re
import numpy as np
import pandas as pd
import nltk
import networkx as nx

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# ── 1. Load & inspect ─────────────────────────────────────────────────────────
df = pd.read_csv("tennis_articles.csv")
print("Shape:", df.shape)
print(df.head())
print(df.info())

df.drop(columns=["article_title"], inplace=True)

# ── 2. Sentence tokenization ──────────────────────────────────────────────────
sentences = []
for text in df["article_text"].dropna():
    sentences.extend(sent_tokenize(text))

print(f"\nTotal sentences: {len(sentences)}")

# ── 3. Load GloVe embeddings ──────────────────────────────────────────────────
import os, zipfile, urllib.request

GLOVE_ZIP = "glove.6B.zip"
GLOVE_FILE = "glove.6B.100d.txt"

if not os.path.exists(GLOVE_FILE):
    if not os.path.exists(GLOVE_ZIP):
        print("Downloading GloVe embeddings (this may take a while)...")
        urllib.request.urlretrieve(
            "https://nlp.stanford.edu/data/glove.6B.zip", GLOVE_ZIP
        )
    print("Extracting glove.6B.100d.txt ...")
    with zipfile.ZipFile(GLOVE_ZIP, "r") as z:
        z.extract(GLOVE_FILE)

print("Loading GloVe vectors...")
glove = {}
with open(GLOVE_FILE, encoding="utf-8") as f:
    for line in f:
        parts = line.split()
        glove[parts[0]] = np.array(parts[1:], dtype=float)

print(f"Loaded {len(glove):,} word vectors.")

# ── 4. Clean sentences ────────────────────────────────────────────────────────
stop_words = set(stopwords.words("english"))

def clean(sentence):
    sentence = re.sub(r"[^a-zA-Z\s]", "", sentence)   # remove punctuation & numbers
    sentence = sentence.lower()
    words = sentence.split()
    words = [w for w in words if w not in stop_words]
    return words

cleaned = [clean(s) for s in sentences]

# ── 5. Sentence vectorization ─────────────────────────────────────────────────
DIM = 100

def vectorize(words):
    vecs = [glove[w] for w in words if w in glove]
    if not vecs:
        return np.zeros(DIM)
    return np.mean(vecs, axis=0)

sentence_vectors = [vectorize(words) for words in cleaned]

# ── 6. Similarity matrix ──────────────────────────────────────────────────────
n = len(sentences)
sim_matrix = np.zeros((n, n))

def cosine_similarity(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return np.dot(a, b) / denom

for i in range(n):
    for j in range(n):
        if i != j:
            sim_matrix[i][j] = cosine_similarity(sentence_vectors[i], sentence_vectors[j])

# ── 7. PageRank ───────────────────────────────────────────────────────────────
graph = nx.from_numpy_array(sim_matrix)
scores = nx.pagerank(graph)

# ── 8. Summarize ──────────────────────────────────────────────────────────────
TOP_N = 10
ranked = sorted(scores, key=scores.get, reverse=True)[:TOP_N]
ranked.sort()  # restore reading order

print("\n" + "="*60)
print(f"SUMMARY (top {TOP_N} sentences)")
print("="*60)
for idx in ranked:
    print(f"- {sentences[idx]}")