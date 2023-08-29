from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4


class ObjectMetaModel(BaseModel):
    date_created: Optional[datetime] = Field(default_factory=datetime.now)
    date_last_edit: Optional[datetime] = Field(default_factory=datetime.now)
    slug: Optional[str] = uuid4().hex
    id: Optional[int] = None
