from fastapi import FastAPI,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.entity_extractor import extract_entities
from app.relationship_extractor import extract_relationships
from app.graph_builder import build_graph
import spacy
import tempfile
import os
from app.document_loader import extract_text_from_pdf
from app.chunker import chunk_text
from app.llm_extractor import extract_with_llm
from app.graph_merge import merge_graphs

nlp = spacy.load("en_core_web_sm")
app = FastAPI(title="AI Knowledge Graph")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text:str = "FastAPI was created by Tiangolo and is built on Starlette"

@app.post("/graph")
def generate_graph(input: TextInput):
    chunks = chunk_text(input.text)

    partial_graphs = []
    for chunk in chunks:
        result = extract_with_llm(chunk)
        partial_graphs.append(result)

    merged = merge_graphs(partial_graphs)

    return build_graph(
        merged["entities"],
        merged["relations"]
    )

@app.post("/graph/pdf")
async def generate_graph_from_pdf(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        text = extract_text_from_pdf(tmp_path)
        doc = nlp(text)

        nodes = extract_entities(text)
        links = extract_relationships(doc)

        return build_graph(nodes, links)
    finally:
        os.remove(tmp_path)
