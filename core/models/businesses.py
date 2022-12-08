from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Business(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    address: str
    established: Optional[str] = None
    timestamp: datetime = datetime.now()
