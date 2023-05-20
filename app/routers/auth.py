from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserLogin, Token
from app import models, utils, oauth2
from app.templates import templates

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    auth_entry = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )
    if not auth_entry or not utils.verify(
        user_credentials.password, auth_entry.password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    # create token
    access_token = oauth2.create_access_token(payload={"user_id": str(auth_entry.id)})
    # return token

    return {"access_token": access_token, "token_type": "bearer"}
