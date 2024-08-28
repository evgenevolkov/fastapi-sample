from decouple import config
from fastapi import status, Depends, HTTPException, APIRouter
from pydantic import TypeAdapter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from ..database import models
from ..database.setup import get_db
from ..utils import oauth2, schemas 
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix='/texts', tags = ['Texts'])

ROLE_ADMIN = config("role_admin")
ROLE_END_USER = config("role_end_user")


@router.post('/create', status_code=status.HTTP_201_CREATED
             , response_model=schemas.TextOut)
def create_text(
        text_data: schemas.TextCreate,
        db: Session = Depends(get_db),
        current_user: schemas.UserCurrent = Depends(oauth2.get_current_user)):

    db_record = models.Texts(
                    user_id=current_user.id,
                    **text_data.model_dump())
    try:
        db.add(db_record) 
        db.commit()
        db.refresh(db_record)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}", exc_info=True)
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected DB error while trying to insert data.")

    return db_record


@router.get('/all', status_code=status.HTTP_200_OK,
            response_model=list[schemas.TextOut])
def get_all_texts(
        limit: int = 3,
        skip: int = 0,
        search: Optional[str] = "",
        current_user: schemas.UserCurrent = Depends(oauth2.get_current_user),
        db: Session = Depends(get_db)):

    logger.debug(f"limit: {limit}")
    if current_user.role != ROLE_ADMIN:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Insufficient priviledges to perform operation")

    try:
        texts = (db.query(models.Texts)
                    .filter(models.Texts.name.contains(search))
                    .offset(skip)
                    .limit(limit)
                    .all())
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}", exc_info=True)
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected DB error while trying to get data.")

    ta = TypeAdapter(list[schemas.TextOut])
    texts_out = ta.validate_python(texts, from_attributes=True)

    return texts_out


@router.get('/all_own', status_code=status.HTTP_200_OK,
            response_model=list[schemas.TextOut])
def get_all_own_texts(
        current_user: schemas.UserCurrent = Depends(oauth2.get_current_user),
        db: Session = Depends(get_db)):

    try:
        texts = db.query(models.Texts).filter_by(user_id=current_user.id)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}", exc_info=True)
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected DB error while trying to get data.")

    ta = TypeAdapter(list[schemas.TextOut])
    texts_out = ta.validate_python(texts, from_attributes=True)

    return texts_out


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_text_by_id(
        id: int,
        db: Session = Depends(get_db),
        current_user: schemas.UserCurrent = Depends(oauth2.get_current_user)):
    
    text = (db.query(models.Texts)
                .filter_by(user_id=current_user.id, id=id)
                .first())
    if not text:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=(
                    f"Text with id: {id} not found."
                    + " Either not exists or not created by current user."))
    try:
        db.delete(text)
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Error on entry deletion attempt: {e}")
        db.rollback()
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"An unexpected error occurred on deletion attempt")
    
    return