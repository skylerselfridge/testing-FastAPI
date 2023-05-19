import uuid
from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def testUUID(id):
    try:
        uuid.UUID(id)
    except Exception as e:
        d = {
            "msg:": "failed to convert argument to proper type",
            "type": "argument_error.invalid",
        }
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=d)
