from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ContactRequestBase(BaseModel):
    name: str
    phone_number: str
    letter: str

class ContactRequestCreate(ContactRequestBase):
    pass

class ContactRequestResponse(ContactRequestBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
