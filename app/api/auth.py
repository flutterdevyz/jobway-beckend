from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.notification import Notification
from app.schemas.user import EmployerCreate, JobSeekerCreate, Token, UserResponse, UserLogin, UserAuthResponse, ResetPasswordRequest
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/employer", response_model=UserAuthResponse)
def register_employer(user: EmployerCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone_number == user.phone_number).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        phone_number=user.phone_number,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        email=user.email,
        company_name=user.company_name,
        city=user.city,
        location=user.location
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.phone_number, "role": new_user.role.value}, expires_delta=access_token_expires
    )
    
    return {**new_user.__dict__, "access_token": access_token, "token_type": "bearer"}

@router.post("/register/job-seeker", response_model=UserAuthResponse)
def register_job_seeker(user: JobSeekerCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone_number == user.phone_number).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    hashed_password = get_password_hash(user.password)
    new_user = User(
        phone_number=user.phone_number,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.phone_number, "role": new_user.role.value}, expires_delta=access_token_expires
    )
    
    return {**new_user.__dict__, "access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token, summary="Login for All Users (Admin, Employer, Job Seeker)")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == user_credentials.phone_number).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone_number, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/reset-password-request", summary="Request password reset (notifies admin)")
def reset_password_request(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    # Check if phone number is registered
    user = db.query(User).filter(User.phone_number == data.phone_number).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Bu telefon raqamga tegishli hisob topilmadi"
        )

    # Find all admin users to notify
    admins = db.query(User).filter(User.role == UserRole.admin).all()
    if not admins:
        raise HTTPException(
            status_code=503,
            detail="Admin topilmadi, so'rov yuborib bo'lmadi"
        )

    # Create a notification for each admin
    for admin in admins:
        notification = Notification(
            user_id=admin.id,
            title="Parolni tiklash so'rovi",
            message=(
                f"Foydalanuvchi {data.full_name} (telefon: {data.phone_number}) "
                f"parolini tiklashni so'radi.\n\nSabab / Xat:\n{data.letter}"
            ),
            is_read=False
        )
        db.add(notification)

    db.commit()
    return {"detail": "So'rovingiz adminga yuborildi. Tez orada siz bilan bog'lanishadi."}
