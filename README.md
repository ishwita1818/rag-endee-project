# 🔍 SmartDoc AI — Document Q&A with Vector Search

Ask questions about your documents and get AI-powered answers instantly.

## 🎯 What It Does
Upload any document → Ask a question in plain English → Get a precise AI answer backed by real sources.

## 🛠️ Tech Stack
| Component | Technology |
|---|---|
| Vector Database | Endee |
| Embeddings | SentenceTransformers |
| Language Model | LLaMA 3.3 70B (Groq) |
| Backend | Flask + Python |
| Deployment | Docker |

## 🏗️ Architecture
```
User Question → Vector Embedding → Endee Similarity Search → Top Chunks → LLaMA 3.3 → Answer
```

## 💡 Why It's Impressive
- 🔒 Fully local — documents never leave your machine
- ⚡ Millisecond search across thousands of documents
- 🧠 Understands meaning, not just keywords
- 🐳 One command Docker deployment

## 🔮 Future Plans
- PDF & Word document support
- Cloud deployment
- Multi-user support

---
*Built with ❤️ using [Endee Vector Database](https://github.com/endee-io/endee)*
