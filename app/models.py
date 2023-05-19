from .database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Boolean, text, TIMESTAMP, ForeignKey
import uuid


class Post(Base):
    __tablename__ = "posts"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="TRUE", nullable=False)
    time_stamp = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    owner = relationship("User")


class User(Base):
    __tablename__ = "users"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    time_stamp = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )


class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    post_id = Column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
