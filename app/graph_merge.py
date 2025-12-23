def merge_graphs(graphs):
    entities = {}
    relations = {}

    for g in graphs:
        for e in g.get("entities", []):
            eid = e["id"]
            if eid not in entities:
                entities[eid] = e

        for r in g.get("relations", []):
            key = (r["source"], r["target"], r["relation"])
            if key not in relations:
                relations[key] = r
            else:
                # keep higher confidence
                relations[key]["confidence"] = max(
                    relations[key]["confidence"],
                    r.get("confidence", 0)
                )

    return {
        "entities": list(entities.values()),
        "relations": list(relations.values())
    }
