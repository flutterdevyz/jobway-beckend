from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import requests

import base64

from app.api import deps
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate, PasswordChange, EmployerResponse
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash

router = APIRouter(prefix="/employers", tags=["employers"])

@router.get("/me", response_model=EmployerResponse)
def read_employers_me(current_user: User = Depends(deps.get_current_active_user)):
    if current_user.role != UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized as employer")
    return current_user

@router.put("/me", response_model=EmployerResponse)
def update_employer_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role != UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized as employer")

    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.email is not None:
        current_user.email = user_in.email
    if user_in.company_name is not None:
        current_user.company_name = user_in.company_name
    if user_in.city is not None:
        current_user.city = user_in.city
    if user_in.location is not None:
        current_user.location = user_in.location
    if user_in.company_image_url is not None:
        current_user.company_image_url = user_in.company_image_url
    if user_in.company_description is not None:
        current_user.company_description = user_in.company_description
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_employer_password(
    password_in: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role != UserRole.employer:
        raise HTTPException(status_code=403, detail="Not authorized as employer")

    if not verify_password(password_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    current_user.hashed_password = get_password_hash(password_in.new_password)
    db.add(current_user)
    db.commit()
    return None

@router.get("/{user_id}", response_model=EmployerResponse)
def read_employer_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    user = db.query(User).filter(User.id == user_id, User.role == UserRole.employer).first()
    if not user:
        raise HTTPException(status_code=404, detail="Employer not found")
    return user
