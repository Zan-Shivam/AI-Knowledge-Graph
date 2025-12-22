import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.load("en_core_web_sm")

# Add EntityRuler BEFORE NER
ruler = nlp.add_pipe("entity_ruler", before="ner")

ruler.add_patterns([
    {"label": "TECH", "pattern": [{"TEXT": {"REGEX": "^[A-Z][a-zA-Z0-9]+$"}}]}
])

def extract_entities(text: str):
    doc = nlp(text)
    entities = []
    seen = set()

    for ent in doc.ents:
        if ent.text not in seen:
            seen.add(ent.text)
            entities.append({
                "id": ent.text,
                "label": ent.text,
                "type": ent.label_
            })

    return entities
