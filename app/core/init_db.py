from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def init_db():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.phone_number == "Muhammadsodiq").first()
        if not admin:
            print("Creating superuser admin...")
            admin_user = User(
                phone_number="Muhammadsodiq",
                hashed_password=get_password_hash("934472477"),
                full_name="Admin User",
                role=UserRole.admin,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Superuser created.")
        else:
            print("Superuser already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
