from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company_name: Optional[str] = None
    company_image_url: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    description: str
    requirements: Optional[List[str]] = None
    city: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_image_url: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    city: Optional[str] = None

class JobResponse(JobBase):
    id: int
    employer_id: int
    created_at: datetime

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
