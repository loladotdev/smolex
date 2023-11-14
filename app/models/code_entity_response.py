from typing import List

from pydantic import BaseModel, Field


class CodeEntityResponse(BaseModel):
    data: List[str] = Field(..., description="Retrieved code for the given entities")
