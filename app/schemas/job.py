from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator
from app.schemas.category import CategoryResponse
from app.core.utils import get_full_url

class JobBase(BaseModel):
    title: str
    company_name: Optional[str] = None
    company_image_url: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    description: str
    requirements: Optional[List[str]] = None
    city: Optional[str] = None
    category_id: Optional[int] = None
    job_image_url: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobFilterRequest(BaseModel):
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    city: Optional[str] = None
    skip: int = 0
    limit: int = 100

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_image_url: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    city: Optional[str] = None
    category_id: Optional[int] = None
    job_image_url: Optional[str] = None

class JobResponse(JobBase):
    id: int
    employer_id: Optional[int] = None
    created_at: datetime
    category: Optional[CategoryResponse] = None

    @field_validator("requirements", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except:
                return [v]
        return v

    @field_validator("job_image_url", "company_image_url", mode="after")
    @classmethod
    def prepend_base_url(cls, v: Optional[str]) -> Optional[str]:
        return get_full_url(v)

    class Config:
        from_attributes = True

class ApplicationBase(BaseModel):
    full_name: str
    phone_number: str
    cover_letter: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationResponse(ApplicationBase):
    id: int
    job_id: int
    applicant_id: int
    applied_at: datetime
    
    class Config:
        from_attributes = True
