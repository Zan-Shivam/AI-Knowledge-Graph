from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.entity_extractor import extract_entities
from app.relationship_extractor import extract_relationships
from app.graph_builder import build_graph
import spacy

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
    doc = nlp(input.text)

    nodes = extract_entities(input.text)
    links = extract_relationships(doc)

    return build_graph(nodes,links)