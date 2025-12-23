import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

SYSTEM_PROMPT = """
You extract knowledge graphs from text.

Return ONLY valid JSON with this structure:
{
  "entities": [{"id": "...", "type": "..."}],
  "relations": [
    {"source": "...", "target": "...", "relation": "...", "confidence": 0.0}
  ]
}

Rules:
- Do not explain
- Do not add text outside JSON
- Use short, canonical relation names
"""

def extract_with_llm(text: str):
    payload = {
        "model": MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\nText:\n{text}",
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()

    raw = response.json()["response"]
    print("RAW LLM OUTPUT:\n", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"entities": [], "relations": []}
