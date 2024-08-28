from fastapi import status, Depends, HTTPException, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List

from ..database import models
from ..utils import schemas
from ..database.setup import get_db
from ..utils import utils, oauth2
from ..utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix='/users', tags = ['Users'])


@router.get('/all', status_code=status.HTTP_200_OK, response_model=List[schemas.UserOut])
def get_all_users(
        db: Session = Depends(get_db), 
        current_user: schemas.UserCurrent = Depends(oauth2.get_current_user)):

    if current_user.role != schemas.UserRole.ROLE_ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Insufficient priviledges to perform operation")
    
    users = db.query(models.Users).all()
    return users


@router.get('/{id}', response_model=schemas.UserOut)
def get_user(
        id: int,
        db: Session = Depends(get_db),
        current_user: schemas.UserCurrent = Depends(oauth2.get_current_user)):
    
    if id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=("Only access to own record is allowed."
                    + f" Current user_id: {current_user.id}" ))
    
    user = db.query(models.Users).filter(models.Users.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"User with id: {id} not found")
    else:
        return user


@router.post('/create', 
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    password_hash = utils.hash(user.password)
    user.password = password_hash
    new_user = models.Users(**user.model_dump())

    # check if user already exists
    existing_user = db.query(models.Users).filter_by(name=user.name).first()
    if existing_user:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with name: {user.name} already exists")

    # check if email already exists
    existing_email = db.query(models.Users).filter_by(email=user.email).first()
    if existing_email:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email: {user.email} already exists")

    try:
        db.add(new_user) 
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as e:
        logger.error(f"Error on user creation attempt: {e}")
        db.rollback()
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"An unexpected error occurred on deletion attempt")

    return new_user


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        id: int
        , db: Session = Depends(get_db)
        , current_user: schemas.UserCurrent = Depends(oauth2.get_current_user)
        ):
    if id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=("Only deletion of current user is allowed."
                    + f" Current user_id: {current_user.id}" ))

    user = db.query(models.Users).filter(models.Users.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail = f"User with id: {id} not found")
    
    try:
        db.delete(user)
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Error on entry deletion attempt: {e}")
        db.rollback()
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"An unexpected error occurred on deletion attempt")
    
    return