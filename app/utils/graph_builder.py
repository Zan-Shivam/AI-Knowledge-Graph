def normalize(text: str) -> str:
    return text.strip().strip(".,()")

def prettify_relation(rel: str) -> str:
    if not rel:
        return rel

    return rel.replace("_", " ").strip()


def build_graph(entities, relations):
    nodes = {}
    
    for e in entities:
        eid = normalize(e["id"])
        nodes[eid] = {
            "id": eid,
            "label": eid.replace("_", " "),
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
            "relation": prettify_relation(r["relation"]),
            "confidence": r.get("confidence", 1.0)
        })

    print("nodes: ", list(nodes.values()))
    print("links: ", links)

    return {
        "nodes": list(nodes.values()),
        "links": links
    }


