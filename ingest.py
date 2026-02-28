import os
from endee import Endee
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "my_documents"
EMBEDDING_DIM = 384

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")

# Connect to Endee
client = Endee()

def create_index():
    try:
        client.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            space_type="cosine",
            precision="float32"
        )
        print("✅ Index created!")
    except Exception as e:
        print(f"ℹ️ Index note: {e}")

def split_into_chunks(text, chunk_size=60):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def ingest_file(filepath):
    print(f"\n📄 Processing: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    chunks = split_into_chunks(text)
    print(f"   → Split into {len(chunks)} chunks")

    index = client.get_index(name=INDEX_NAME)

    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        vectors.append({
            "id": f"{os.path.basename(filepath).replace('.', '_')}_{i}",
            "vector": embedding,
            "meta": {
                "text": chunk,
                "source": os.path.basename(filepath)
            }
        })

    index.upsert(vectors)
    print(f"   ✅ Successfully stored {len(vectors)} chunks in Endee!")

if __name__ == "__main__":
    print("=" * 50)
    print("  Endee RAG - Document Ingestion")
    print("=" * 50)
    create_index()
    data_dir = "data"
    files_found = 0
    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        if os.path.isfile(filepath) and filename.endswith(".txt"):
            ingest_file(filepath)
            files_found += 1
    if files_found == 0:
        print("⚠️ No .txt files found in data/ folder!")
    else:
        print(f"\n🎉 Done! {files_found} file(s) ingested into Endee.")