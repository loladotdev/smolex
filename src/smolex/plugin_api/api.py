import ast
import os
import pickle
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, Response

from llama_index import load_index_from_storage, StorageContext
from typing import List
from pydantic import BaseModel

from src.smolex.config import config
from src.smolex.lookup_backends.ast_sqlite import (
    generate_class_interface,
    create_ast_sqlite_index,
)
from src.smolex.lookup_backends.vector_store import create_vector_store_index

app = FastAPI()

origins = [
    "https://chat.openai.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ClassName(BaseModel):
    class_names: List[str]


class Items(BaseModel):
    items: List[str]


def query_sqlite_ast_db(where_clause: str):
    db = sqlite3.connect(config.ast_sqlite_db)
    db_query = f"SELECT AST FROM Entities {where_clause}"

    results = db.execute(db_query).fetchall()

    if results:
        print(results)
        print(f"Found {len(results)} results in SQLite DB")
        return [ast.parse(pickle.loads(result[0])) for result in results]

    return []


def query_vector_store(query_input: str):
    index = load_index_from_storage(
        StorageContext.from_defaults(persist_dir=config.vector_store_location)
    )
    query_engine = index.as_query_engine()
    return str(query_engine.query(query_input))


def lookup_interface(class_names: List[str]):
    where_clause = (
        "WHERE Name IN ("
        + ",".join(["'" + item + "'" for item in class_names])
        + ") AND Type = 'ClassDef'"
    )
    ast_nodes = query_sqlite_ast_db(where_clause)

    if ast_nodes:
        return [generate_class_interface(node) for node in ast_nodes]

    print("No AST nodes found in SQLite DB, falling back to vector store")
    return query_vector_store(
        "Extract the interface for the given existing classes: " + " ".join(class_names)
    )


def lookup_code(items: List[str]):
    where_clause = (
        "WHERE Name IN (" + ",".join(["'" + item + "'" for item in items]) + ")"
    )
    ast_nodes = query_sqlite_ast_db(where_clause)

    if ast_nodes:
        return [ast.unparse(node) for node in ast_nodes]

    print("No AST nodes found in SQLite DB, falling back to vector store")
    return query_vector_store(
        "Give me the existing code for the given existing items (e.g. class, method): "
        + " ".join(items)
    )


@app.post("/lookup_interface/")
async def post_lookup_interface(body: ClassName):
    data = lookup_interface(body.class_names)
    if data:
        return {"data": data}
    else:
        raise HTTPException(status_code=500, detail="Server error")


@app.post("/lookup_code/")
async def post_lookup_code(body: Items):
    data = lookup_code(body.items)
    if data:
        return {"data": data}
    else:
        raise HTTPException(status_code=500, detail="Server error")


@app.get("/logo.png")
async def plugin_logo():
    filename = Path(__file__).parent / "logo.png"
    return FileResponse(filename, media_type="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open(".well-known/ai-plugin.json") as f:
        text = f.read()
        return Response(content=text, media_type="application/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(content=text, media_type="text/yaml")


def refresh_backend() -> None:
    create_vector_store_index()
    create_ast_sqlite_index()


def require_refresh() -> bool:
    return not os.path.exists(config.vector_store_location) or not os.path.exists(
        config.ast_sqlite_db
    )
