from openai import OpenAI
import os
import json

# --- Groq client (OpenAI-compatible) ---
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# --- Strong extraction prompt ---
SYSTEM_PROMPT = """
You are an information extraction engine.

Extract ONLY factual entities and explicit relationships stated in the text.

OUTPUT ONLY valid JSON that matches this EXACT schema:

{
  "entities": [
    { "id": "string", "type": "string" }
  ],
  "relations": [
    {
      "source": "string",
      "target": "string",
      "relation": "string",
      "confidence": number
    }
  ]
}

RULES:
- Do NOT infer or assume anything
- Do NOT invent relationships
- Use concise entity names
- Relation must be a short verb phrase (snake_case preferred)
- confidence must be between 0 and 1
- If unsure, OMIT the entity or relation
- Output raw JSON only.
- Do NOT use markdown code fences.
- Do NOT wrap the output in ``` blocks.
"""

def _strip_code_fences(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        # Remove starting ```
        text = text.split("```", 1)[1]

        # Remove trailing ```
        if "```" in text:
            text = text.rsplit("```", 1)[0]

    return text.strip()

def _clean_output(data: dict) -> dict:
    clean_entities = []
    clean_relations = []

    seen_entities = set()

    for e in data.get("entities", []):
        if not e.get("id"):
            continue
        eid = e["id"].strip()
        if eid not in seen_entities:
            seen_entities.add(eid)
            clean_entities.append({
                "id": eid,
                "type": e.get("type", "Unknown")
            })

    for r in data.get("relations", []):
        src = r.get("source")
        tgt = r.get("target")
        rel = r.get("relation")

        if not src or not tgt or not rel:
            continue

        if src == tgt:
            continue

        if len(rel.split("_")) > 4:
            continue

        if r.get("confidence", 0) < 0.6:
            continue

        clean_relations.append({
            "source": src.strip(),
            "target": tgt.strip(),
            "relation": rel.strip(),
            "confidence": float(r.get("confidence", 1))
        })

    return {
        "entities": clean_entities,
        "relations": clean_relations
    }


def extract_with_llm(text: str) -> dict:
    """
    Extract entities and relations from text using Groq LLaMA-3.3-70B.
    """

    response = client.responses.create(
        model="llama-3.3-70b-versatile",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.0,
        max_output_tokens=600,
    )

    raw_output = response.output_text.strip()
    clean_output = _strip_code_fences(raw_output)

    # Defensive parsing (still important)
    try:
        parsed = json.loads(clean_output)
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON from LLM")
        return {"entities": [], "relations": []}

    # Final schema safety
    if not isinstance(parsed, dict):
        return {"entities": [], "relations": []}

    parsed.setdefault("entities", [])
    parsed.setdefault("relations", [])

    return _clean_output(parsed)
