from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.job import Job, Application
from app.schemas.job import JobCreate, JobResponse, ApplicationResponse, JobUpdate, ApplicationCreate
from app.api import deps
import json

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", response_model=JobResponse)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role != UserRole.employer and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only employers can create jobs")

    # Check for Premium restriction
    has_active_premium = current_user.is_premium
    if has_active_premium and current_user.premium_expires_at:
        if current_user.premium_expires_at < datetime.utcnow():
            has_active_premium = False

    if current_user.role == UserRole.employer and not has_active_premium:
        # Count existing jobs
        job_count = db.query(Job).filter(Job.employer_id == current_user.id).count()
        if job_count >= 1:
            raise HTTPException(
                status_code=403, 
                detail="Free account limit reached. You can only post 1 job. Please upgrade to Premium."
            )

    # Serialize requirements list to string if it exists
    reqs_str = json.dumps(job_in.requirements) if job_in.requirements else None

    new_job = Job(
        title=job_in.title,
        employer_id=current_user.id,
        company_name=job_in.company_name or current_user.company_name, # Fallback to user's company
        company_image_url=job_in.company_image_url,
        min_salary=job_in.min_salary,
        max_salary=job_in.max_salary,
        description=job_in.description,
        requirements=reqs_str,
        city=job_in.city or current_user.city # Fallback to user's city
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # Deserialize for response (Pydantic expects list)
    new_job.requirements = json.loads(new_job.requirements) if new_job.requirements else []
    return new_job

@router.get("/", response_model=List[JobResponse])
def read_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    # Post-process requirements from JSON string to list
    for job in jobs:
         if job.requirements:
             try:
                 job.requirements = json.loads(job.requirements)
             except:
                 job.requirements = []
    return jobs

    return jobs

@router.get("/my-jobs", response_model=List[JobResponse])
def get_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role != UserRole.employer and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only employers can view their own jobs")
    
    jobs = db.query(Job).filter(Job.employer_id == current_user.id).order_by(Job.created_at.desc()).all()
    
    # Post-process requirements
    for job in jobs:
         if job.requirements:
             try:
                 job.requirements = json.loads(job.requirements)
             except:
                 job.requirements = []
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def read_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.requirements:
        try:
            job.requirements = json.loads(job.requirements)
        except:
             job.requirements = []
    return job

@router.post("/{job_id}/apply", response_model=ApplicationResponse)
def apply_to_job(
    job_id: int,
    application_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role != UserRole.job_seeker:
         raise HTTPException(status_code=403, detail="Only job seekers can apply")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if already applied
    existing_application = db.query(Application).filter(
        Application.job_id == job_id,
        Application.applicant_id == current_user.id
    ).first()
    
    if existing_application:
        raise HTTPException(status_code=400, detail="You have already applied to this job")

    new_app = Application(
        job_id=job_id,
        applicant_id=current_user.id,
        full_name=application_in.full_name,
        phone_number=application_in.phone_number,
        cover_letter=application_in.cover_letter
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_in: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Permission check: Admin or Owner
    if current_user.role != UserRole.admin and job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this job")

    # Update fields
    if job_in.title is not None:
        job.title = job_in.title
    if job_in.company_name is not None:
        job.company_name = job_in.company_name
    if job_in.company_image_url is not None:
        job.company_image_url = job_in.company_image_url
    if job_in.min_salary is not None:
        job.min_salary = job_in.min_salary
    if job_in.max_salary is not None:
        job.max_salary = job_in.max_salary
    if job_in.description is not None:
        job.description = job_in.description
    if job_in.city is not None:
        job.city = job_in.city
    if job_in.requirements is not None:
        job.requirements = json.dumps(job_in.requirements)

    db.commit()
    db.refresh(job)

    # Deserialize requirements for response
    if job.requirements:
        try:
            job.requirements = json.loads(job.requirements)
        except:
             job.requirements = []

    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Permission check: Admin or Owner
    if current_user.role != UserRole.admin and job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")

    db.delete(job)
    db.commit()
    return None

@router.get("/{job_id}/applications", response_model=List[ApplicationResponse])
def get_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Permission check: Admin or Owner
    if current_user.role != UserRole.admin and job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view applications for this job")

    return job.applications

from fpdf import FPDF
from fastapi.responses import Response

@router.get("/applications/{application_id}/pdf")
def generate_application_pdf(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    job = application.job
    # Permission: Admin, Employer (Owner of job), or Applicant themselves?
    # Usually Employer wants to download. Applicant might want strict privacy but they applied.
    # Let's allow Admin and Employer (Job Owner).
    if current_user.role == UserRole.admin or (job and job.employer_id == current_user.id):
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized to download this application")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Application for: {job.title}", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Company: {job.company_name}", ln=1, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(50, 10, txt="Applicant Name:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=application.full_name, ln=1)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(50, 10, txt="Phone Number:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=application.phone_number, ln=1)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(50, 10, txt="Applied At:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=str(application.applied_at), ln=1)

    pdf.ln(10)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 10, txt="Cover Letter:", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=application.cover_letter or "No cover letter provided.")

    pdf_content = pdf.output(dest='S').encode('latin-1', 'replace') # output returns string in 'S' mode, encode for bytes
    
    headers = {
        'Content-Disposition': f'attachment; filename="application_{application_id}.pdf"'
    }
    return Response(content=pdf_content, media_type="application/pdf", headers=headers)

@router.get("/applications/me", response_model=List[ApplicationResponse])
def get_my_all_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role != UserRole.employer and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only employers can view their applications")
    
    # Join with Job to filter by employer_id
    applications = db.query(Application).join(Job).filter(Job.employer_id == current_user.id).all()
    return applications

@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    job = application.job
    # Permission: Admin or Employer (Owner of job)
    if current_user.role != UserRole.admin and (not job or job.employer_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this application")

    db.delete(application)
    db.commit()
    return None

@router.post("/applications/{application_id}/accept", status_code=status.HTTP_204_NO_CONTENT)
def accept_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    job = application.job
    if not job:
          raise HTTPException(status_code=404, detail="Job associated with this application not found")

    # Permission check: Only the Employer who owns the job can accept
    if current_user.role != UserRole.admin and job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept applications for this job")
    
    # Logic: Accept the application -> Delete the Job (as requested)
    # We should delete the job. 
    # Note: Dependencies (other applications) might need handling. 
    # Safe approach: Delete all applications for this job first, then the job.
    
    db.query(Application).filter(Application.job_id == job.id).delete()
    db.delete(job)
    db.commit()
    
    return None
