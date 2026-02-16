from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime
from datetime import datetime
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    employer = "employer"
    job_seeker = "job_seeker"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.job_seeker)
    
    # Employer specific fields (nullable for others)
    email = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    company_image_url = Column(String, nullable=True)
    company_description = Column(String, nullable=True)
    city = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)

