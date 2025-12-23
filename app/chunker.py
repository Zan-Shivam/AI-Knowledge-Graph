import spacy

nlp = spacy.load("en_core_web_sm")

def chunk_text(text: str, max_sentences: int = 2):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]

    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i:i + max_sentences])
        if chunk:
            chunks.append(chunk)

    return chunks
