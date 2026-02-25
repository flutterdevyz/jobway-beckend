from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserCreate, UserUpdate, AdminUserResponse, AdminPasswordReset
from app.models.job import Job, Application
from app.models.category import Category
from app.models.contact import ContactRequest
from app.schemas.job import JobResponse, JobUpdate, ApplicationResponse, JobCreate
from app.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate
from app.schemas.contact import ContactRequestResponse
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.models.notification import Notification
from app.core.security import get_password_hash
from sqlalchemy import func
import json

print("DEBUG: admin.py module loading...")

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/ping")
def admin_ping(current_user: User = Depends(deps.get_current_admin_user)):
    return {"status": "ok", "message": "Admin API is active"}

@router.get("/users", response_model=List[AdminUserResponse])
def admin_get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserCreate, # Using generic create schema for update for simplicity, ideally separate Update schema
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.phone_number = user_in.phone_number
    user.full_name = user_in.full_name
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)
    
    # Ideally handle other fields dynamically or specific schema
    
    db.commit()
    db.refresh(user)
    return user

@router.put("/users/{user_id}/reset-password")
def admin_reset_password(
    user_id: int,
    password_data: AdminPasswordReset,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    return {"message": "Password reset successfully"}

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return None
@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    return {
        "total_users": db.query(User).count(),
        "total_jobs": db.query(Job).count(),
        "total_categories": db.query(Category).count(),
        "total_applications": db.query(Application).count(),
        "total_contact_requests": db.query(ContactRequest).count(),
        "total_notifications": db.query(Notification).count(),
        "premium_users": db.query(User).filter(User.is_premium == True).count()
    }

# Jobs Management
@router.get("/jobs", response_model=List[JobResponse])
def admin_read_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    return db.query(Job).offset(skip).limit(limit).all()

@router.post("/jobs", response_model=JobResponse)
def admin_create_job(
    job_in: JobCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    # Serialize requirements list to string if it exists
    reqs_str = json.dumps(job_in.requirements) if job_in.requirements else None
    
    new_job = Job(
        title=job_in.title,
        employer_id=current_user.id, # Default to admin if not specified, though usually employers post
        company_name=job_in.company_name,
        company_image_url=job_in.company_image_url,
        min_salary=job_in.min_salary,
        max_salary=job_in.max_salary,
        description=job_in.description,
        requirements=reqs_str,
        city=job_in.city,
        category_id=job_in.category_id,
        job_image_url=job_in.job_image_url
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    if new_job.requirements:
        new_job.requirements = json.loads(new_job.requirements)
    return new_job

@router.put("/jobs/{job_id}", response_model=JobResponse)
def admin_update_job(
    job_id: int,
    job_in: JobUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = job_in.model_dump(exclude_unset=True)
    if "requirements" in update_data and update_data["requirements"]:
        update_data["requirements"] = json.dumps(update_data["requirements"])
        
    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    
    if job.requirements:
        try:
            job.requirements = json.loads(job.requirements)
        except:
             job.requirements = []
    return job

@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return None

# Categories Management
@router.get("/categories", response_model=List[CategoryResponse])
def admin_read_categories(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    return db.query(Category).all()

@router.post("/categories", response_model=CategoryResponse)
def admin_create_category(
    cat_in: CategoryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    new_cat = Category(**cat_in.model_dump())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@router.put("/categories/{cat_id}", response_model=CategoryResponse)
def admin_update_category(
    cat_id: int,
    cat_in: CategoryUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = cat_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cat, field, value)
        
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/categories/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_category(
    cat_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return None

# Applications Management
@router.get("/applications", response_model=List[ApplicationResponse])
def admin_read_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    return db.query(Application).offset(skip).limit(limit).all()

@router.delete("/applications/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_application(
    app_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    app_rec = db.query(Application).filter(Application.id == app_id).first()
    if not app_rec:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app_rec)
    db.commit()
    return None

# Contact Requests Management
@router.get("/contact-requests", response_model=List[ContactRequestResponse])
def admin_read_contact_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    return db.query(ContactRequest).offset(skip).limit(limit).all()

@router.delete("/contact-requests/{req_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_contact_request(
    req_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    req = db.query(ContactRequest).filter(ContactRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Contact request not found")
    db.delete(req)
    db.commit()
    return None

# Notifications Management
@router.post("/notifications", response_model=NotificationResponse)
def admin_send_notification(
    notification_in: NotificationCreate,    
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    new_notif = Notification(
        user_id=notification_in.user_id,
        title=notification_in.title,
        message=notification_in.message
    )
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)
    return new_notif

@router.get("/notifications", response_model=List[NotificationResponse])
def admin_get_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    try:
        return db.query(Notification).offset(skip).limit(limit).all()
    except Exception as e:
        print(f"ERROR in admin_get_notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/notifications/{notif_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_notification(
    notif_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    try:
        notif = db.query(Notification).filter(Notification.id == notif_id).first()
        if not notif:
            raise HTTPException(status_code=404, detail="Notification not found")
        db.delete(notif)
        db.commit()
    except Exception as e:
        print(f"ERROR in admin_delete_notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    return None
