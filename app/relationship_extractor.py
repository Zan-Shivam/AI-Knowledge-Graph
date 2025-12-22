def extract_relationships(doc):
    relations = []
    last_subject = None

    for token in doc:
        # ---- created by ----
        if token.lemma_ == "create" and token.dep_ == "ROOT":
            subject = None
            obj = None

            for child in token.children:
                if child.dep_ in ("nsubj", "nsubjpass"):
                    subject = child.text
                if child.dep_ == "agent":
                    for grandchild in child.children:
                        if grandchild.dep_ == "pobj":
                            obj = grandchild.text

            if subject:
                last_subject = subject

            if subject and obj:
                relations.append({
                    "source": subject,
                    "target": obj,
                    "relation": "created_by"
                })

        # ---- built on ----
        if token.lemma_ == "build":
            subject = None
            obj = None

            for child in token.children:
                if child.dep_ in ("nsubj", "nsubjpass"):
                    subject = child.text
                if child.dep_ == "prep" and child.text.lower() == "on":
                    for grandchild in child.children:
                        if grandchild.dep_ == "pobj":
                            obj = grandchild.text
            
            #carry subject forward aka last seen subject
            if subject is None:
                subject = last_subject

            if subject and obj:
                relations.append({
                    "source": subject,
                    "target": obj,
                    "relation": "built_on"
                })

    return relations
