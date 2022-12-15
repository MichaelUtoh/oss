from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class BusinessCreateUpdateSchema(BaseModel):
    name: str
    address: str
    established: Optional[str] = None


class BusinessListSchema(BaseModel):
    id: int
    name: str
    address: str
    established: Optional[str] = None
    timestamp: datetime = None
