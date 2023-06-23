from src.smolex.lookup_backends.ast_sqlite import create_ast_sqlite_index
from src.smolex.lookup_backends.vector_store import create_vector_store_index

if __name__ == "__main__":
    create_vector_store_index()
    create_ast_sqlite_index()
