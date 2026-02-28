import os
from endee import Endee
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "my_documents"

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model ready!")

client = Endee()

def search_endee(question, top_k=3):
    try:
        question_vector = model.encode(question).tolist()
        index = client.get_index(name=INDEX_NAME)
        results = index.query(vector=question_vector, top_k=top_k)
        return results
    except Exception as e:
        print(f"❌ Search error: {e}")
        return []

def generate_answer(question, results):
    try:
        context = "\n\n".join([
            f"[Source: {r.get('meta', {}).get('source', 'unknown') if isinstance(r, dict) else r.meta.get('source', 'unknown')}]\n{r.get('meta', {}).get('text', '') if isinstance(r, dict) else r.meta.get('text', '')}"
            for r in results
        ])
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the context below.
If the answer is not in the context, say "I don't have information about that in the documents."

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            return None
        groq_client = Groq(api_key=groq_key)
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM error: {e}")
        return None

def ask(question):
    print(f"\n{'='*50}")
    print(f"❓ Question: {question}")
    print("🔍 Searching Endee...")
    results = search_endee(question, top_k=3)
    if not results:
        print("❌ No results found.")
        return
    print(f"✅ Found {len(results)} relevant chunks:\n")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] Score: {r.similarity:.3f} | Source: {r.meta.get('source','unknown')}")
        print(f"       {r.meta.get('text','')[:100]}...")
    answer = generate_answer(question, results)
    if answer:
        print(f"\n🤖 AI Answer:\n{answer}")

if __name__ == "__main__":
    print("=" * 50)
    print("  Endee RAG - Ask Questions")
    print("=" * 50)
    print("Type your question and press Enter. Type 'quit' to exit.\n")
    while True:
        question = input("❓ Your question: ").strip()
        if not question:
            continue
        if question.lower() in ["quit", "exit", "q"]:
            print("Bye!")
            break
        ask(question)