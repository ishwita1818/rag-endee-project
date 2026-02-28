from flask import Flask, request, jsonify, render_template_string
from query import search_endee, generate_answer

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>RAG System with Endee</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 850px; margin: 60px auto; padding: 20px; background: #f0f4f8; }
        h1 { color: #2d3748; }
        .search-box { display: flex; gap: 10px; margin: 20px 0; }
        input[type=text] { flex: 1; padding: 12px; font-size: 16px; border: 1px solid #cbd5e0; border-radius: 8px; }
        button { padding: 12px 24px; background: #4c51bf; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
        button:hover { background: #434190; }
        .answer-box { background: white; border-left: 4px solid #4c51bf; padding: 20px; border-radius: 8px; margin: 15px 0; }
        .chunk { background: white; padding: 15px; border-radius: 8px; margin: 8px 0; border: 1px solid #e2e8f0; }
        .score { background: #ebf8ff; color: #2b6cb0; padding: 2px 8px; border-radius: 12px; font-size: 13px; }
        .source { color: #718096; font-size: 13px; }
        .loading { color: #718096; font-style: italic; }
    </style>
</head>
<body>
    <h1>🔍 Document Q&A with Endee Vector DB</h1>
    <p>Ask questions about your uploaded documents. Results are powered by semantic vector search.</p>
    <div class="search-box">
        <input type="text" id="question" placeholder="e.g. What is RAG? What is Endee?"
               onkeydown="if(event.key==='Enter') ask()" />
        <button onclick="ask()">Ask</button>
    </div>
    <div id="output"></div>
    <script>
        async function ask() {
            const q = document.getElementById('question').value.trim();
            if (!q) return;
            document.getElementById('output').innerHTML = '<p class="loading">Searching Endee...</p>';
            const res = await fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: q})
            });
            const data = await res.json();
            let html = '';
            if (data.answer) {
                html += `<div class="answer-box"><b>🤖 AI Answer:</b><br><br>${data.answer}</div>`;
            }
            html += '<h3>📚 Retrieved Chunks from Endee:</h3>';
            data.chunks.forEach((c, i) => {
                html += `<div class="chunk">
                    <span class="score">Score: ${c.score.toFixed(3)}</span>
                    <span class="source"> | ${c.source}</span>
                    <p>${c.text}</p>
                </div>`;
            });
            document.getElementById('output').innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "")
    results = search_endee(question, top_k=3)
    chunks = [{
        "text": r.get("meta", {}).get("text", "") if isinstance(r, dict) else r.meta.get("text", ""),
        "source": r.get("meta", {}).get("source", "unknown") if isinstance(r, dict) else r.meta.get("source", "unknown"),
        "score": r.get("similarity", 0) if isinstance(r, dict) else r.similarity
    } for r in results]
    answer = generate_answer(question, results)
    return jsonify({"chunks": chunks, "answer": answer})

if __name__ == "__main__":
    print("Starting web app at http://localhost:5000")
    app.run(debug=True, port=5000)