from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Request, status, APIRouter
from app import utils
from app import models
from app.schemas import Post, PostCreate, PostOut
from app.database import get_db
from app import oauth2
from sqlalchemy import func


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[PostOut])
async def get_posts(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    results = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
    ).all()
    return results


@router.put("/{id}", response_model=Post)
async def update_post(
    id: str,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    utils.testUUID(id)
    query = db.query(models.Post).filter(models.Post.id == id)
    query_post = query.first()
    if not query_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if query_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    query.update(post.dict(), synchronize_session=False)
    db.commit()
    return query.first()


# path parameter
@router.get("/{id}", response_model=PostOut)
async def get_post(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    utils.testUUID(id)
    try:
        results = (
            db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
            .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
            .group_by(models.Post.id)
            .filter(models.Post.id == id)
        ).one()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if results:
        return results

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
async def create_posts(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    new_post = models.Post(user_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    utils.testUUID(id)
    query = db.query(models.Post).filter(models.Post.id == id)
    post = query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    query.delete(synchronize_session=False)
    db.commit()
