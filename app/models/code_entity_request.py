from typing import List

from pydantic import BaseModel


class CodeEntityRequest(BaseModel):
    entities: List[str]
