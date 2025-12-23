def normalize(text: str) -> str:
    return text.strip().strip(".,()")

def build_graph(entities, relations):
    nodes = {}
    
    for e in entities:
        eid = normalize(e["id"])
        nodes[eid] = {
            "id": eid,
            "label": eid,
            "type": e.get("type", "Unknown")
        }

    for r in relations:
        src = normalize(r["source"])
        tgt = normalize(r["target"])

        if src not in nodes:
            nodes[src] = {
                "id": src,
                "label": src,
                "type": "Unknown"
            }

        if tgt not in nodes:
            nodes[tgt] = {
                "id": tgt,
                "label": tgt,
                "type": "Unknown"
            }

    links = []
    for r in relations:
        links.append({
            "source": normalize(r["source"]),
            "target": normalize(r["target"]),
            "relation": r["relation"],
            "confidence": r.get("confidence", 1.0)
        })

    return {
        "nodes": list(nodes.values()),
        "links": links
    }


