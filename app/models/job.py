from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    employer_id = Column(Integer, ForeignKey("users.id"))
    company_name = Column(String, nullable=True)
    company_image_url = Column(String, nullable=True)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True) # Storing as JSON string or simple text for now
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    job_image_url = Column(String, nullable=True)
    city = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employer = relationship("User", backref="jobs")
    category = relationship("Category", back_populates="data")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    applicant_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    cover_letter = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", backref="applications")
    applicant = relationship("User", backref="applications")
