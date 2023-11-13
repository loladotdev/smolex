import argparse
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routes import retrieve


def create_app(index_root: Path):
    _app = FastAPI()
    _app.include_router(retrieve.router)
    _app.state.index_root = index_root  # noqa

    _app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Smolex Server")
    parser.add_argument("--index-root", required=True, help="Root directory that should be indexed")
    args = parser.parse_args()

    app = create_app(index_root=Path(args.index_root))
    uvicorn.run(app, host="0.0.0.0", port=5003)
