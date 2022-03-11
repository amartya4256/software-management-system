from typing import List, Optional
from xmlrpc.client import Boolean

from pydantic import BaseModel

from .enums import Status


class SoftwareBase(BaseModel):
    name: Optional[str]



class SoftwareCreate(SoftwareBase):
    pass


class Software(SoftwareBase):
    id: Optional[int]
    version: Optional[str]
    status: Optional[Status]

    class Config:
        orm_mode = True

class ApiKey(BaseModel):
    key: str

    class Config:
        orm_mode = True

class ApiKeyStatus(BaseModel):
    key: str
    activated: Boolean

    class Config:
        orm_mode = True