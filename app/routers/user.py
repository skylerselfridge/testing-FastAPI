from typing import List
from fastapi import Depends, HTTPException, status, APIRouter
from app import models, utils
from app.schemas import UserCreate, UserData
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserData)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    try:
        db.add(new_user)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address is already registered",
        )
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=UserData)
def get_user(id: str, db: Session = Depends(get_db)):
    utils.testUUID(id)
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )
    return user
