import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.load("en_core_web_sm")

# Add ruler BEFORE ner
ruler = nlp.add_pipe("entity_ruler", before="ner")

ruler.add_patterns([
    {
        "label": "TECH",
        "pattern": [{"TEXT": {"REGEX": "^[A-Z][a-zA-Z0-9]+$"}}]
    }
])

def extract_entities(text: str):
    doc = nlp(text)
    entities = {}
    
    # First: take spaCy's NER (higher priority)
    for ent in doc.ents:
        entities[ent.text] = {
            "id": ent.text,
            "label": ent.text,
            "type": ent.label_
        }

    # Then: add TECH entities if not already classified
    for token in doc:
        if token.ent_type_ == "TECH" and token.text not in entities:
            entities[token.text] = {
                "id": token.text,
                "label": token.text,
                "type": "TECH"
            }

    return list(entities.values())
