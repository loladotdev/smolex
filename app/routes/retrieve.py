from app.internal.retrieval.python import retrieve_code_entities
from app.models.code_entity_request import CodeEntityRequest
from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/api/code/retrieve/")
async def retrieve(request: Request, body: CodeEntityRequest):
    return {"data": retrieve_code_entities(code_entities=body.entities, index_root=request.app.state.index_root)}
