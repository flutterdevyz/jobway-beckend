from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate, PasswordChange, JobSeekerResponse
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash

router = APIRouter(prefix="/job-seekers", tags=["job-seekers"])

@router.get("/me", response_model=JobSeekerResponse)
def read_job_seekers_me(current_user: User = Depends(deps.get_current_active_user)):
    if current_user.role != UserRole.job_seeker:
         raise HTTPException(status_code=403, detail="Not authorized as job seeker")
    return current_user

@router.put("/me", response_model=JobSeekerResponse)
def update_job_seeker_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role != UserRole.job_seeker:
         raise HTTPException(status_code=403, detail="Not authorized as job seeker")

    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_job_seeker_password(
    password_in: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role != UserRole.job_seeker:
         raise HTTPException(status_code=403, detail="Not authorized as job seeker")

    if not verify_password(password_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    current_user.hashed_password = get_password_hash(password_in.new_password)
    db.add(current_user)
    db.commit()
    return None

@router.get("/{user_id}", response_model=JobSeekerResponse)
def read_job_seeker_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    user = db.query(User).filter(User.id == user_id, User.role == UserRole.job_seeker).first()
    if not user:
        raise HTTPException(status_code=404, detail="Job Seeker not found")
    return user
