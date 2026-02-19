from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.app.database import get_session
from backend.app.models.marketing import SocialMediaPost

router = APIRouter()

@router.post("/posts/", response_model=SocialMediaPost)
def create_post(post: SocialMediaPost, session: Session = Depends(get_session)):
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

@router.get("/posts/", response_model=List[SocialMediaPost])
def read_posts(
    session: Session = Depends(get_session)
):
    posts = session.exec(select(SocialMediaPost)).all()
    return posts
