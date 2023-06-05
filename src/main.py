import os

from src.smolex.plugin_api.api import require_refresh, refresh_backend, app

if __name__ == "__main__":
    import uvicorn

    if "OPENAI_API_KEY" not in os.environ:
        print("Please set the OPENAI_API_KEY environment variable.")
        exit(1)

    if require_refresh():
        print("Refreshing initial vector & AST db backends... (it may take a while)")
        print("This will only happen once, unless you delete the vector_store_location or ast_sqlite_db files.")
        print("You can also manually refresh the backends by calling the ./index.py function.")
        refresh_backend()
    else:
        print("Using existing vector & AST db backends. Refresh as needed by calling the ./index.py function.")

    uvicorn.run(app, host="0.0.0.0", port=5003)
