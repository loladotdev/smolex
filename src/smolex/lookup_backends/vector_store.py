from typing import List
from src.smolex.config import config

from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex, Document


def create_vector_store_index():
    documents: List[Document] = []

    for source_root in config.roots:
        print(f"Loading documents from {source_root}...")
        documents.extend(SimpleDirectoryReader(source_root, recursive=True, required_exts=config.extensions,
                                               exclude=config.exclude).load_data())

    print("Creating vector store index...")
    index = GPTVectorStoreIndex.from_documents(documents)

    print("Persisting index...")
    index.storage_context.persist(persist_dir=config.vector_store_location)


if __name__ == '__main__':
    create_vector_store_index()
