from hmac import digest_size
import json
from multiprocessing.dummy import Array
from operator import gt, lt
from typing import Any, Optional
from pydantic import BaseModel, Field, EmailStr, Json

# Define your entity class using Pydantic BaseModel
class RepoObject(BaseModel):
    unique_id: str = Field(min_length=4, max_length=20)
    entity: str = Field(min_length=3, max_length=20)
    version: Optional[int] = Field(gt=0, lt=10, default=1)
    payload: Json
    searchableField: Json = None
