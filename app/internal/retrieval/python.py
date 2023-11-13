import ast
import os
import sqlite3
import pickle
from pathlib import Path
from typing import List

INDEXED_RETRIEVAL_TYPES = (ast.ClassDef, ast.FunctionDef)


def create_in_memory_database() -> sqlite3.Connection:
    """ Isolation_level=None -> autocommit. No need to commit manually. """

    connection = sqlite3.connect(":memory:", isolation_level=None)

    connection.execute(
        "CREATE TABLE Entities "  # noqa
        "(ID INTEGER PRIMARY KEY AUTOINCREMENT, FileName TEXT, Type TEXT, Name TEXT, AST BLOB)"  # noqa
    )

    return connection


def create_index(connection: sqlite3.Connection, index_root: Path):
    for root, dirs, files in os.walk(index_root):
        for file in files:
            if file.endswith(".py"):
                filename = root / Path(file)

                with open(filename, "r") as fd:
                    try:
                        root_node = ast.parse(fd.read())
                    except SyntaxError as e:
                        continue

                for node in [
                    relevant_node
                    for relevant_node in ast.walk(root_node)
                    if isinstance(relevant_node, INDEXED_RETRIEVAL_TYPES)
                ]:
                    connection.execute(
                        "INSERT INTO Entities (FileName, Type, Name, AST) VALUES (?, ?, ?, ?)",  # noqa
                        (filename.name, type(node).__name__, node.name, pickle.dumps(node)),
                    )


def query_index(connection: sqlite3.Connection, code_entities: List[str]) -> List[str]:
    where_clause = (
        "WHERE Name IN (" + ",".join(["'" + entity + "'" for entity in code_entities]) + ")"
    )

    query = f"SELECT AST FROM Entities {where_clause}"  # noqa

    if results := connection.execute(query).fetchall():
        nodes = [ast.parse(pickle.loads(result[0])) for result in results]
        return [ast.unparse(node) for node in nodes]

    return []


def retrieve_code_entities(code_entities: List[str], index_root: Path):
    """
    Create and retrieve code index. Since it's fast,
    we can do it in memory and on the fly.
    """
    connection = create_in_memory_database()
    create_index(connection=connection, index_root=index_root)
    return query_index(connection=connection, code_entities=code_entities)
