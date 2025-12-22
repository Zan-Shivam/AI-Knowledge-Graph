def normalize(text: str) -> str:
    return text.strip().strip(".,()")

def build_graph(entities, relations):
    normalized_nodes = {}
    
    for e in entities:
        norm_id = normalize(e["id"])
        normalized_nodes[norm_id] = {
            "id": norm_id,
            "label": e["label"],
            "type": e["type"]
        }

    node_ids = set(normalized_nodes.keys())

    normalized_links = []
    for r in relations:
        src = normalize(r["source"])
        tgt = normalize(r["target"])

        if src in node_ids and tgt in node_ids:
            normalized_links.append({
                "source": src,
                "target": tgt,
                "relation": r["relation"],
                "confidence": r.get("confidence", 1.0)
            })

    return {
        "nodes": list(normalized_nodes.values()),
        "links": normalized_links
    }

