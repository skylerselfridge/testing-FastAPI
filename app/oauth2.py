from jose import JWTError, jwt
from datetime import datetime, timedelta
from app import schemas, models
from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY
SECRET_KEY = settings.SECRET_KEY
# Algorithm
ALGORITHM = settings.TOKEN_ALGORITHM
# Expiration Time
ACCESS_TOKEN_EXPIRE_MINUTES = settings.TOKEN_EXPIRE


def create_access_token(payload: dict):
    data = payload.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})

    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return token


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id = payload.get("user_id")

        if not id:
            raise credentials_exception

        token_data = schemas.TokenData(user_id=id)

    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception=credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.user_id).first()

    return user
