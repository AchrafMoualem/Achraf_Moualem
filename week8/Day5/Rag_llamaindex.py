from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# ── Models ────────────────────────────────────────────────────────────────────
Settings.llm = HuggingFaceLLM(
    model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    tokenizer_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    context_window=2048,
    max_new_tokens=256,
    device_map="auto",
)

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ── Load documents ────────────────────────────────────────────────────────────
documents = SimpleDirectoryReader("papers").load_data()
print(f"Loaded {len(documents)} document(s).")

# ── Build & persist index ─────────────────────────────────────────────────────
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist(persist_dir="./index_store")
print("Index saved to ./index_store")

# ── Query ─────────────────────────────────────────────────────────────────────
engine = index.as_query_engine()

questions = [
    "What are the main points in the article?",
    "What is the tone of the article?",
    "Give a summary of the document in 5 bullet points.",
]

for q in questions:
    print(f"\nQ: {q}")
    print(f"A: {engine.query(q)}")