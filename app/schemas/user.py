from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole
from app.core.utils import get_full_url

class UserBase(BaseModel):
    phone_number: str
    full_name: str

class UserCreate(UserBase):
    password: str

class EmployerCreate(UserCreate):
    role: UserRole = UserRole.employer
    email: EmailStr
    company_name: str
    city: str
    location: str

class JobSeekerCreate(UserCreate):
    role: UserRole = UserRole.job_seeker

class UserLogin(BaseModel):
    phone_number: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: Optional[bool] = True
    email: Optional[str] = None
    company_name: Optional[str] = None
    company_image_url: Optional[str] = None
    company_description: Optional[str] = None
    city: Optional[str] = None
    location: Optional[str] = None

    @field_validator("company_image_url", mode="after")
    @classmethod
    def prepend_base_url(cls, v: Optional[str]) -> Optional[str]:
        return get_full_url(v)

    class Config:
        from_attributes = True

class UserAuthResponse(UserResponse):
    access_token: str
    token_type: str

class AdminUserResponse(UserResponse):
    hashed_password: str
    is_premium: Optional[bool] = False
    premium_expires_at: Optional[datetime] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    company_image_url: Optional[str] = None
    company_description: Optional[str] = None
    city: Optional[str] = None
    location: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class AdminPasswordReset(BaseModel):
    new_password: str

# New Specific Responses
class EmployerResponse(UserBase):
    id: int
    role: UserRole = UserRole.employer
    email: Optional[str] = None
    company_name: Optional[str] = None
    company_image_url: Optional[str] = None
    company_description: Optional[str] = None
    city: Optional[str] = None
    location: Optional[str] = None
    
    @field_validator("company_image_url", mode="after")
    @classmethod
    def prepend_base_url(cls, v: Optional[str]) -> Optional[str]:
        return get_full_url(v)

    class Config:
        from_attributes = True

class JobSeekerResponse(UserBase):
    id: int
    role: UserRole = UserRole.job_seeker
    # Job seeker specific fields (currently none extra, but clean separation)
    
    class Config:
        from_attributes = True
