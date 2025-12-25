def sanitize_llm_output(data: dict):
    clean_entities = []
    clean_relations = []

    
    for e in data.get("entities", []):
        if not isinstance(e, dict):
            continue
        if "id" in e and "type" in e:
            if isinstance(e["id"], str) and isinstance(e["type"], str):
                clean_entities.append({
                    "id": e["id"].strip(),
                    "type": e["type"].strip()
                })

    raw_relations = data.get("relations") or data.get("relationships") or []

    for r in raw_relations:
        if not isinstance(r, dict):
            continue

        if "no direct" in r["relation"].lower():
            continue
        if r["relation"].strip().startswith("-"):
            continue
        if not r["relation"].strip():
            continue

        required = {"source", "target", "relation"}
        if not required.issubset(r.keys()):
            continue

        try:
            confidence = float(r.get("confidence", 0.5))
        except (ValueError, TypeError):
            confidence = 0.5

        clean_relations.append({
            "source": str(r["source"]).strip(),
            "target": str(r["target"]).strip(),
            "relation": str(r["relation"]).strip(),
            "confidence": confidence
        })

    return {
        "entities": clean_entities,
        "relations": clean_relations
    }
