from hmac import digest_size
from operator import gt, lt
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from pydantic.dataclasses import dataclass

# Define your entity class using Pydantic BaseModel
@dataclass(config={"arbitrary_types_allowed": True})
class User(BaseModel):
    entity: str = Field(min_length=3, max_length=20, default=None)
    unique_id: str = Field(min_length=4, max_length=20, default=None)
    version: Optional[int] = Field(gt=0, lt=10, default=1)

    first_name: str = Field(min_length=4, max_length=25, default=None)     
    middle_name: Optional[str] = Field(min_length=1, max_length=10, default='')
    last_name: str = Field(min_length=3, max_length=25, default=None)     
    email: EmailStr | None = Field(default=None)
    phone_numer: int = Field(digest_size=10, default=-1)