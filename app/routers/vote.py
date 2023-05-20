from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from app import utils
from app import models
from app.schemas import Vote
from app.database import get_db
from app import oauth2


router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: Vote,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post_exist = db.query(models.Post).filter(models.Post.id == vote.post_id)
    if not post_exist.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist"
        )
    query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id
    )
    found_vote = query.first()

    if vote.dir:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User has already voted"
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added vote"}
    else:
        # delete
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist"
            )
        query.delete(synchronize_session=False)
        db.commit()

        return {"message": "Successfully deleted vote"}
