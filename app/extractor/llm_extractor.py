from openai import OpenAI
import os
import json

# --- Groq client (OpenAI-compatible) ---
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

ENTITY_PROMPT = """
You are an information extraction engine.

Extract ONLY entities explicitly mentioned in the text.

Rules:
- Do NOT infer
- Do NOT invent entities
- Prefer concrete nouns over abstract concepts
- Use concise, canonical names
- Output JSON ONLY

Schema:
{
  "entities": [
    { "id": "string", "type": "string" }
  ]
}
"""

RELATION_PROMPT_TEMPLATE = """
You are an information extraction engine.

Extract ONLY relationships that are explicitly stated in the text.

IMPORTANT:
- You may ONLY use entities from the list below
- Do NOT introduce new entities
- If a relationship involves an unknown entity, OMIT it
- Do NOT infer or generalize

ENTITIES:
{entity_list}

Schema:
{{
  "relations": [
    {{
      "source": "string",
      "target": "string",
      "relation": "string",
      "confidence": number
    }}
  ]
}}

Output JSON ONLY.
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

def extract_entities_with_llm(text: str) -> list[dict]:
    response = client.responses.create(
        model="llama-3.3-70b-versatile",
        input=[
            {"role": "system", "content": ENTITY_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.0,
        max_output_tokens=400,
    )

    clean_output = _strip_code_fences(response.output_text)

    try:
        data = json.loads(clean_output)
        return data.get("entities", [])
    except json.JSONDecodeError:
        return []

def extract_relations_with_llm(text: str, entities: list[dict]) -> list[dict]:
    entity_names = [e["id"] for e in entities]

    prompt = RELATION_PROMPT_TEMPLATE.format(
        entity_list=", ".join(entity_names)
    )

    response = client.responses.create(
        model="llama-3.3-70b-versatile",
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.0,
        max_output_tokens=400,
    )

    clean_output = _strip_code_fences(response.output_text)

    try:
        data = json.loads(clean_output)
        return data.get("relations", [])
    except json.JSONDecodeError:
        return []

def extract_with_llm(text: str) -> dict:
    entities = extract_entities_with_llm(text)

    if not entities:
        return {"entities": [], "relations": []}

    relations = extract_relations_with_llm(text, entities)

    return _clean_output({
        "entities": entities,
        "relations": relations
    })
