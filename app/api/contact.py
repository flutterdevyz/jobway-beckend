from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.contact import ContactRequest
from app.schemas.contact import ContactRequestCreate, ContactRequestResponse

router = APIRouter(prefix="/contact", tags=["contact"])

@router.post("/", response_model=ContactRequestResponse, status_code=status.HTTP_201_CREATED)
def create_contact_request(
    contact_in: ContactRequestCreate,
    db: Session = Depends(deps.get_db)
):
    new_request = ContactRequest(
        name=contact_in.name,
        phone_number=contact_in.phone_number,
        letter=contact_in.letter
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request
