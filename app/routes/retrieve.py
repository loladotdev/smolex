from app.internal.retrieval.python import retrieve_code_entities
from app.models.code_entity_request import CodeEntityRequest
from fastapi import APIRouter, Request

from app.models.code_entity_response import CodeEntityResponse

router = APIRouter()


@router.post("/api/code/retrieve/", response_model=CodeEntityResponse)
async def retrieve(request: Request, body: CodeEntityRequest):
    """
    Lookup and retrieve existing code for given entities (classes, methods)
    This endpoint returns the existing code for given code entities (classes, methods).
    """

    return {"data": retrieve_code_entities(code_entities=body.entities, index_root=request.app.state.index_root)}
