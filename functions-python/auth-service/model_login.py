from hmac import digest_size
from operator import gt, lt
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

# Define your entity class using Pydantic BaseModel
class Login(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=5, max_length=20)
