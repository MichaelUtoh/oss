from typing import List

from pydantic import BaseModel


class IdListSchema(BaseModel):
    ids: List[int] = None
