# AI Knowledge Graph

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-brightgreen)](https://fastapi.tiangolo.com/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3-orange)](https://groq.com/)

Transform uploaded PDFs and text documents into interactive, connected concept graphs using AI-powered entity and relation extraction. Instead of flat search results, visualize knowledge as an interconnected graph of entities and relationships.

## 🎯 Overview

This project enables users to upload PDF documents or input text, which are processed using a large language model (LLM) to extract factual entities and relations. The output is a knowledge graph represented as JSON (nodes and links), suitable for visualization in web interfaces.


https://github.com/user-attachments/assets/51144edf-29e7-419d-a215-5994ac69a6e5

Key capabilities:
- **PDF Processing**: Extract text from multi-page PDFs and process in parallel.
- **Text Chunking**: Intelligently split long text into overlapping chunks to maintain context.
- **LLM Extraction**: Use Groq's Llama 3.3 model to extract high-confidence subject-predicate-object triples.
- **Graph Merging**: Deduplicate and merge partial graphs from chunks/pages.
- **API-Driven**: FastAPI backend for easy integration.
- **Web Frontend**: Simple HTML/JS interface for uploads and graph rendering.

Ideal for researchers, students, or anyone needing to explore document insights visually.

## ✨ Features

- 📄 **PDF & Text Upload**: Handle PDFs via file upload or raw text input.
- 🧠 **AI-Powered Extraction**: Extracts only explicit facts (no hallucinations) with confidence scores.
- 🔗 **Knowledge Graph Generation**: Outputs standardized graph JSON (nodes with labels/types, links with relations/confidence).
- ⚡ **Parallel Processing**: Multi-threaded page processing for efficiency.
- 🌐 **CORS-Enabled API**: Ready for local frontend development.
- 📊 **Visualizable Output**: Compatible with libraries like D3.js, Cytoscape, or Force Graph.

## 🏗️ Architecture

The project is split into backend (Python/FastAPI) and frontend (HTML/JS).

### Backend Flow
1. **Input**: Text or PDF upload.
2. **Preprocessing**:
   - For PDFs: Extract text per page using PyPDF.
   - Chunk text into ~1200-char segments with sentence overlap.
3. **Extraction**:
   - For each chunk: Prompt Groq LLM (Llama 3.3 70B) to extract facts as JSON triples (subject, predicate, object, confidence).
   - Derive entities (subjects/objects) and relations (predicates).
4. **Merging**: Combine partial graphs, deduplicating by key and maximizing confidence.
5. **Output**: Build normalized graph JSON with nodes (id, label, type) and links (source, target, relation, confidence).

### Key Modules
- `main.py`: FastAPI app with `/graph` (text) and `/graph/pdf` endpoints.
- `app/core/`: PDF loading (`document_loader.py`), chunking (`chunker.py`), pipeline (`pdf_pipeline.py`).
- `app/extractor/`: LLM fact extraction (`llm_extractor.py`), graph merging (`graph_merge.py`).
- `app/utils/`: Graph JSON builder (`graph_builder.py`).

### Frontend
- `frontend/index.html`: Basic upload form and graph visualization (using vanilla JS and a graph library like D3).
- Serves as a client to the backend API.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (free tier available at [console.groq.com](https://console.groq.com))
- Git

### Installation
1. Clone the repo:
   ```
   git clone https://github.com/Zan-Shivam/AI-Knowledge-Graph.git
   cd AI-Knowledge-Graph
   ```

2. Set up virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies (create `requirements.txt` if needed):
   ```
   pip install fastapi uvicorn openai pypdf
   ```

   Full `requirements.txt`:
   ```
   fastapi==0.104.1
   uvicorn==0.24.0
   openai==1.3.7
   pypdf==3.17.1
   ```

4. Set environment variable:
   ```
   export GROQ_API_KEY="your_groq_api_key_here"
   ```

### Running the Backend
```
uvicorn main:app --reload --port 8000
```
- API docs: http://127.0.0.1:8000/docs

### Running the Frontend
Serve the `frontend/` directory (e.g., using VS Code Live Server on port 5500):
- Open `frontend/index.html` in a browser.
- It will connect to the backend at `http://127.0.0.1:8000`.

## 📖 Usage

### API Endpoints

| Endpoint          | Method | Description                          | Request Body/Example                  | Response                  |
|-------------------|--------|--------------------------------------|---------------------------------------|---------------------------|
| `/graph`         | POST   | Generate graph from text            | `{"text": "Your document text here"}` | `{"nodes": [...], "links": [...]}` |
| `/graph/pdf`     | POST   | Generate graph from PDF upload      | Multipart file upload (`file`)       | `{"nodes": [...], "links": [...]}` |

- **Graph Format**:
  ```json
  {
    "nodes": [
      {"id": "entity_id", "label": "Entity Label", "type": "EntityType"}
    ],
    "links": [
      {"source": "src_id", "target": "tgt_id", "relation": "has_relation", "confidence": 0.95}
    ]
  }
  ```

### Example: Text Input
```bash
curl -X POST "http://127.0.0.1:8000/graph" \
  -H "Content-Type: application/json" \
  -d '{"text": "FastAPI was created by Sebastian Ramirez. It is built on Starlette."}'
```

### Example: PDF Upload
Use tools like Postman or the frontend UI to upload a PDF file.

### Frontend Demo
1. Open `frontend/index.html`.
2. Paste text or upload PDF.
3. Submit → View interactive graph.

## 🔧 Customization

- **LLM Model**: Change in `llm_extractor.py` (e.g., switch to OpenAI GPT).
- **Chunk Size**: Adjust `MAX_CHARS` in `chunker.py`.
- **Confidence Threshold**: Modify `conf < 0.6` in `llm_extractor.py`.
- **Visualization**: Enhance frontend with libraries like [vis.js](https://visjs.org/) or [Cytoscape.js](https://js.cytoscape.org/).

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, PyPDF, OpenAI/Groq SDK
- **AI**: Groq (Llama 3.3 70B for fast inference)
- **Frontend**: HTML, JavaScript (assumed D3.js or similar for graphs)
- **Other**: ThreadPoolExecutor for parallelism

## ⚠️ Limitations

- Relies on LLM for extraction; accuracy depends on prompt and model.
- PDFs with images/tables may lose fidelity (text-only extraction).
- No built-in auth; for production, add security.
- Graph visualization is basic; extend for large graphs.

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit changes (`git commit -m 'Add amazing feature'`).
4. Push (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

Feedback and PRs welcome! Issues for bugs/features.

---

*Built with ❤️ by Shivam. Questions? Open an issue!*
