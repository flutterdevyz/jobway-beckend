from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from app.core.utils import get_full_url

class JobSimple(BaseModel):
    id: int
    title: str
    company_name: Optional[str] = None
    company_image_url: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    description: str
    city: Optional[str] = None
    job_image_url: Optional[str] = None
    created_at: datetime

    @field_validator("job_image_url", "company_image_url", mode="after")
    @classmethod
    def prepend_base_url(cls, v: Optional[str]) -> Optional[str]:
        return get_full_url(v)

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    data: List[JobSimple] = []

    @field_validator("image_url", mode="after")
    @classmethod
    def prepend_base_url(cls, v: Optional[str]) -> Optional[str]:
        return get_full_url(v)

    class Config:
        from_attributes = True
