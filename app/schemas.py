from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class UserData(BaseModel):
    id: UUID
    time_stamp: datetime
    email: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str]


class PostBase(BaseModel):
    title: str
    content: str
    # default value assignment
    published: bool = True
    # optional assignment


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: UUID
    time_stamp: datetime
    user_id: UUID
    owner: UserData

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True


class Vote(BaseModel):
    post_id: UUID
    dir: bool
