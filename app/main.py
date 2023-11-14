import argparse
import secrets
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.routes import retrieve


async def check_basic_api_key_auth_header(request: Request, call_next):
    authorization: str = request.headers.get('authorization')

    print(request.url.path)

    # allow /docs without api key
    if request.url.path in ["/docs", "/openapi.json", "/openapi.yaml"]:
        return await call_next(request)

    if authorization != f"Basic {request.app.state.api_key}":
        return Response("Unauthorized", status_code=401)

    return await call_next(request)


def create_app(index_root: Path, api_key: str):
    _app = FastAPI()
    _app.include_router(retrieve.router)

    # Root directory that should be indexed
    _app.state.index_root = index_root  # noqa

    _app.state.api_key = api_key  # noqa
    _app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=check_basic_api_key_auth_header)

    _app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Smolex Server")
    parser.add_argument("--index-root", required=True, help="Root directory that should be indexed")
    parser.add_argument("--api-key", required=False, help="API key for the Smolex Server")

    args = parser.parse_args()

    if args.api_key is None:
        args.api_key = secrets.token_urlsafe(32)
        print(f"Random API key generated. Use --api-key to set a custom API key: {args.api_key}")

    app = create_app(index_root=Path(args.index_root), api_key=args.api_key)
    uvicorn.run(app, host="0.0.0.0", port=5003)
