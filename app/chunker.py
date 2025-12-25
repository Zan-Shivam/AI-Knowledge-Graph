import re

MAX_CHARS = 1200
OVERLAP_SENTENCES = 2

def split_sentences(text: str) -> list[str]:
    # Simple but effective sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str) -> list[str]:
    sentences = split_sentences(text)

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        if current_length + sentence_len > MAX_CHARS:
            chunks.append(" ".join(current_chunk))

            # overlap last N sentences
            current_chunk = current_chunk[-OVERLAP_SENTENCES:]
            current_length = sum(len(s) for s in current_chunk)

        current_chunk.append(sentence)
        current_length += sentence_len

    if current_chunk:
        current_length = sum(len(s) for s in current_chunk) + (len(current_chunk) - 1)
    else:
        current_length = 0

    return chunks
