from openai import OpenAI
import os
import json

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

FACT_PROMPT = """
You are an information extraction engine.

Extract ONLY factual statements explicitly stated in the text.

Rules:
- Do NOT infer or assume
- Do NOT invent facts
- A fact must have a clear subject, predicate, and object
- Use concise canonical names
- Use snake_case for predicates
- If no explicit fact exists, return an empty list
- Output JSON ONLY

Schema:
{
  "facts": [
    {
      "subject": "string",
      "predicate": "string",
      "object": "string",
      "confidence": number
    }
  ]
}
"""

def _get_response_text(response) -> str:
    texts = []

    for item in response.output:
        # Case 1: item has `.content`
        if hasattr(item, "content") and item.content:
            for c in item.content:
                # Case 1a: output text block
                if hasattr(c, "text") and isinstance(c.text, str):
                    texts.append(c.text)

        # Case 2: item itself has `.text`
        elif hasattr(item, "text") and isinstance(item.text, str):
            texts.append(item.text)

    return "\n".join(texts).strip()

def _strip_code_fences(text: str) -> str:
    text = text.strip()

    # Remove leading 'json' (common LLM artifact)
    if text.lower().startswith("json"):
        text = text[4:].strip()

    # Remove fenced code blocks if present
    if text.startswith("```"):
        text = text.split("```", 1)[1]
        if "```" in text:
            text = text.rsplit("```", 1)[0]

    return text.strip()

import re
import json

def _extract_facts_robustly(text: str) -> list[dict]:
    """
    Extract individual fact objects from malformed JSON-like text.
    Keeps only valid subject-predicate-object triples.
    """
    facts = []

    # Find JSON object-like blocks
    object_blocks = re.findall(r'\{[^{}]*\}', text)

    for block in object_blocks:
        try:
            data = json.loads(block)

            if (
                isinstance(data, dict)
                and "subject" in data
                and "predicate" in data
                and "object" in data
            ):
                data["confidence"] = float(data.get("confidence", 1.0))
                facts.append(data)

        except Exception:
            # Skip malformed object
            continue

    return facts

def deduplicate_facts(facts: list[dict]) -> list[dict]:
    unique = {}

    for f in facts:
        key = (
            f["subject"].strip().lower(),
            f["predicate"].strip().lower(),
            f["object"].strip().lower(),
        )

        if key not in unique:
            unique[key] = f
        else:
            # keep highest confidence
            unique[key]["confidence"] = max(
                unique[key].get("confidence", 1.0),
                f.get("confidence", 1.0)
            )

    return list(unique.values())

def extract_facts_with_llm(text: str) -> list[dict]:
    response = client.responses.create(
        model="llama-3.3-70b-versatile",
        input=[
            {"role": "system", "content": FACT_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.0,
        max_output_tokens=500,
    )

    raw_output = _get_response_text(response)

    if not raw_output:
        print("⚠️ Empty LLM output")
        return []

    clean_output = _strip_code_fences(raw_output)

    facts = _extract_facts_robustly(clean_output)

    if not facts:
        print("⚠️ No valid facts extracted")
    else:
        print(f"✅ Extracted {len(facts)} facts")

    return facts


def extract_with_llm(text: str) -> dict:
    facts = extract_facts_with_llm(text)
    facts = deduplicate_facts(facts)

    entities = {}
    relations = []

    for f in facts:
        subj = f.get("subject")
        obj = f.get("object")
        pred = f.get("predicate")
        conf = float(f.get("confidence", 1.0))

        if not subj or not obj or not pred:
            continue

        if conf < 0.6:
            continue

        # derive entities
        entities[subj] = {"id": subj, "type": "Unknown"}
        entities[obj] = {"id": obj, "type": "Unknown"}

        relations.append({
            "source": subj,
            "target": obj,
            "relation": pred,
            "confidence": conf
        })

    return {
        "entities": list(entities.values()),
        "relations": relations
    }
